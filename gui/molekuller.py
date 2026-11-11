"""Moleküller ekranı ve sihirbaz.

Moleküller ekranı üretilmiş molekülleri listeler. Bir molekül çalıştırılınca
sihirbaz açılır: adımlar sırayla gelir, tablolardan satır seçilir, formlar
doldurulur, sonda özet gösterilir ve "uygula" denince yazan adımlar çalışır.
"""
import json
from functools import partial
from typing import Any

from nicegui import ui

from core import rows as row_tools
from core.models import Atom, FieldSpec
from core.molecules import Molecule, needs_selection
from core.validation import check_form, clean_values
from gui import client, forms, layout
from gui.i18n import t
from gui.tables import SearchTable

STATUS = {"selected": ("seçildi", "tag"), "done": ("yapıldı", "tag ok"),
          "failed": ("yapılamadı", "tag bad"), "skipped": ("denenmedi", "tag warn")}


# ------------------------------------------------------------------ molekül listesi

async def build_list() -> None:
    """Moleküller ekranını kurar. gui/shell.py tarafından çağrılır."""
    await MoleculesPage().build()


class MoleculesPage:

    async def build(self) -> None:
        with ui.column().classes("w-full max-w-4xl mx-auto gap-4 p-4"):
            ui.label(t("Moleküller")).classes("text-lg font-medium")
            self.cards = ui.row().classes("gap-3")
        await self.reload()

    async def reload(self) -> None:
        molecules = await client.molecules()
        self.cards.clear()
        with self.cards:
            if not molecules:
                ui.label(t("Henüz molekül yok. Elementler ekranında bir atom seçip molekül üret.")
                         ).classes("muted text-sm")
            for molecule in molecules:
                self.draw_card(molecule)

    def draw_card(self, molecule: dict[str, Any]) -> None:
        steps = " → ".join(step["title"] for step in molecule["steps"])
        with ui.column().classes("box p-4 gap-2").style("width:300px"):
            ui.label(molecule["title"]).classes("text-sm font-medium")
            ui.label(molecule["description"]).classes("muted text-xs")
            ui.label(f"{len(molecule['steps'])} {t('adım')}: {steps}").classes("muted text-xs")
            with ui.row().classes("gap-2"):
                layout.primary("Çalıştır", partial(ui.navigate.to, f"/calistir/{molecule['id']}"))
                layout.secondary("Sil", partial(self.remove, molecule["id"]))

    async def remove(self, molecule_id: str) -> None:
        await client.remove_molecule(molecule_id)
        await self.reload()


# -------------------------------------------------------------------------- sihirbaz

async def build_run(molecule_id: str) -> None:
    """Sihirbazı kurar. gui/shell.py tarafından çağrılır."""
    found = [item for item in await client.molecules() if item["id"] == molecule_id]
    with ui.column().classes("w-full max-w-4xl mx-auto gap-4 p-4"):
        if not found:
            ui.label(t("Molekül bulunamadı.")).classes("muted text-sm")
            return
        molecule = Molecule.model_validate(found[0])
        atoms = await atoms_of(molecule)
        if atoms is None:
            ui.label("Bu molekülün kullandığı atomlardan biri katalogda yok.").classes("tag bad")
            return
        await Wizard(molecule, atoms).build()


async def atoms_of(molecule: Molecule) -> list[Atom] | None:
    """Molekülün her adımının atomunu katalogdan bulur; biri eksikse None döner."""
    catalog: dict[tuple[str, str], Atom] = {}
    for item in await client.elements():
        for atom in item["element"]["atoms"]:
            catalog[(item["element"]["name"], atom["name"])] = Atom.model_validate(atom)
    atoms = [catalog.get((step.element, step.atom)) for step in molecule.steps]
    return None if None in atoms else atoms


class Wizard:
    """Bir molekülün çalıştırılması: toplanan girdiler ve o anki ekran."""

    def __init__(self, molecule: Molecule, atoms: list[Atom]) -> None:
        count = len(molecule.steps)
        self.molecule = molecule
        self.atoms = atoms
        self.inputs: list[dict[str, Any]] = [{} for _ in range(count)]  # adım başına form değerleri
        self.selections: list[dict[str, Any] | None] = [None] * count  # adım başına seçilen satır
        self.prefilled: list[str | None] = [None] * count  # formun hangi kayıtla doldurulduğu
        self.pages = [index for index in range(count) if self.asks(index)]  # admine sorulan adımlar
        self.position = 0  # pages içindeki yerimiz; sonuna gelince özet gösterilir
        self.result: dict[str, Any] | None = None

    # ------------------------------------------------------------------- adım bilgisi

    def is_table(self, index: int) -> bool:
        return self.atoms[index].action == "list"

    def form_fields(self, index: int) -> list[FieldSpec]:
        """Adımın admine sorulacak alanları; etiketler molekülde verilen etiketlerdir."""
        step = self.molecule.steps[index]
        fields: list[FieldSpec] = []
        for field in self.atoms[index].inputs:
            source = step.fields.get(field.name)
            if source is not None and source.kind == "form":
                fields.append(field.model_copy(update={"title": source.label or field.title}))
        return fields

    def asks(self, index: int) -> bool:
        """Bu adımda admine gösterilecek bir şey var mı."""
        return self.is_table(index) or bool(self.form_fields(index))

    def has_writes(self) -> bool:
        return any(atom.action != "list" for atom in self.atoms)

    # ------------------------------------------------------------------------ çizim

    async def build(self) -> None:
        ui.label(self.molecule.title).classes("text-lg font-medium")
        self.body = ui.column().classes("w-full gap-3")
        await self.show()

    async def show(self) -> None:
        """O anki ekranı çizer: bir adım, özet ya da sonuç."""
        self.body.clear()
        with self.body:
            if self.result is not None:
                self.draw_result()
            elif self.position >= len(self.pages):
                self.draw_summary()
            else:
                await self.draw_step(self.pages[self.position])

    async def draw_step(self, index: int) -> None:
        step = self.molecule.steps[index]
        ui.label(f"{t('Adım')} {self.position + 1} / {len(self.pages)}: {step.title}").classes(
            "text-sm font-medium")
        if self.is_table(index):
            await self.draw_table_step(index)
        else:
            await self.draw_form_step(index)
        with ui.row().classes("gap-2"):
            if self.position > 0:
                layout.secondary("Geri", self.back)
            if self.has_writes():
                layout.primary("İleri", self.next)
            else:
                layout.secondary("Moleküllere dön", partial(ui.navigate.to, "/molekuller"))

    async def draw_table_step(self, index: int) -> None:
        """Tablo adımı: kayıtlar servisten okunur; sonraki adım istiyorsa satır seçilir."""
        step, atom = self.molecule.steps[index], self.atoms[index]
        answer = await client.call_atom(step.element, atom.name, {})
        if not answer["ok"]:
            ui.label(answer["message"]).classes("tag bad")
            return
        selectable = needs_selection(self.molecule, index)
        self.selections[index] = None
        if selectable:
            ui.label(t("Bir satır seç.")).classes("muted text-xs")
        options = await forms.load_options(step.element, atom.columns)
        SearchTable(atom.columns, answer["data"], options, file_name=atom.name,
                    on_select=partial(self.select_row, index) if selectable else None).build()

    async def draw_form_step(self, index: int) -> None:
        """Form adımı: yalnızca "formda sor" alanları çizilir."""
        fields = self.form_fields(index)
        self.fill_from_selection(index, fields)
        options = await forms.load_options(self.molecule.steps[index].element, fields)
        with ui.column().classes("box p-4 gap-3").style("width:420px"):
            forms.render_form(fields, self.inputs[index], options)

    def fill_from_selection(self, index: int, fields: list[FieldSpec]) -> None:
        """Formu ilk açılışta ve seçilen kayıt değiştiğinde yeniden doldurur."""
        step = self.molecule.steps[index]
        from_record: dict[str, Any] = {}
        for field in fields:
            source = step.fields[field.name]
            record = self.selections[source.step] if source.step is not None else None
            if record is not None:
                from_record[field.name] = record.get(source.field)
        signature = json.dumps(from_record, sort_keys=True, default=str)
        if self.prefilled[index] != signature:
            self.inputs[index] = {**forms.initial_values(fields), **from_record}
            self.prefilled[index] = signature

    def draw_summary(self) -> None:
        """Uygulamadan önce neyin yapılacağını gösterir."""
        ui.label(t("Şunlar yapılacak")).classes("text-sm font-medium")
        for index, step in enumerate(self.molecule.steps):
            with ui.column().classes("box p-3 gap-1 w-full"):
                ui.label(f"{index + 1}. {step.title}").classes("text-sm font-medium")
                if self.is_table(index):
                    ui.label(f"{t('Seçilen kayıt')}: {self.describe(self.selections[index])}").classes("text-sm")
                for field in self.form_fields(index):
                    value = row_tools.display(self.inputs[index].get(field.name))
                    ui.label(f"{field.title}: {value}").classes("text-sm")
        with ui.row().classes("gap-2"):
            if self.pages:
                layout.secondary("Geri", self.back)
            layout.primary("Uygula", self.apply)

    def draw_result(self) -> None:
        """Her adımın nasıl bittiğini gösterir."""
        ui.label(t("Sonuç")).classes("text-sm font-medium")
        for index, step in enumerate(self.result["steps"]):
            text, style = STATUS[step["status"]]
            with ui.row().classes("box p-3 gap-3 w-full items-center"):
                ui.label(f"{index + 1}. {step['title']}").classes("text-sm font-medium")
                ui.label(t(text)).classes(style)
                ui.label(step["message"]).classes("text-sm")
        with ui.row().classes("gap-2"):
            layout.primary("Yeniden çalıştır", self.restart)
            layout.secondary("Moleküllere dön", partial(ui.navigate.to, "/molekuller"))

    def describe(self, record: dict[str, Any] | None) -> str:
        """Seçilen kaydı tek satırda özetler."""
        if record is None:
            return "-"
        return ", ".join(row_tools.display(value) for value in list(record.values())[:4])

    # --------------------------------------------------------------------- eylemler

    def select_row(self, index: int, record: dict[str, Any] | None) -> None:
        self.selections[index] = record

    async def next(self) -> None:
        """Adımı denetler ve bir sonrakine geçer."""
        index = self.pages[self.position]
        if self.is_table(index):
            if needs_selection(self.molecule, index) and self.selections[index] is None:
                ui.notify(t("Bir satır seç."), type="warning")
                return
        else:
            fields = self.form_fields(index)
            errors = check_form(fields, self.inputs[index])
            if errors:
                titles = {field.name: field.title for field in fields}
                name, message = next(iter(errors.items()))
                ui.notify(f"{titles[name]}: {message}", type="warning")
                return
        self.position += 1
        await self.show()

    async def restart(self) -> None:
        """Sihirbazı boş girdilerle baştan başlatır."""
        count = len(self.molecule.steps)
        self.inputs = [{} for _ in range(count)]
        self.selections = [None] * count
        self.prefilled = [None] * count
        self.position = 0
        self.result = None
        await self.show()

    async def back(self) -> None:
        self.position -= 1
        await self.show()

    async def apply(self) -> None:
        """Toplanan girdilerle molekülü uygular."""
        inputs = [clean_values(self.form_fields(index), self.inputs[index])
                  for index in range(len(self.molecule.steps))]
        try:
            self.result = await client.run_molecule(self.molecule.id, inputs, self.selections)
        except client.ApiError as error:
            ui.notify(str(error), type="negative")
            return
        await self.show()
