"""Elementler ekranı: periyodik tablo, içe aktarma ve her atomun arayüzü.

Bir atom seçildiğinde kabuk onun arayüzünü içe aktarılan bilgiden üretir:
liste atomu için tablo, diğerleri için form. Atom buradan denenebilir ve
tek tıkla moleküle çevrilebilir.
"""
import json
from functools import partial
from typing import Any

from nicegui import ui

from core.models import Atom, FieldSpec
from core.validation import check_form, clean_values
from gui import client, forms, layout
from gui.i18n import t
from gui.tables import SearchTable

DEFAULT_SERVICE = "http://localhost:8101"

# Tek kayda dokunan atomlar hangi kayıt üzerinde çalışacaklarını bu alandan öğrenir.
ID_FIELD = FieldSpec(name="id", title="Kayıt numarası", kind="integer",
                     description="İşlem yapılacak kaydın numarası.")


async def build() -> None:
    """Elementler ekranını kurar. gui/shell.py tarafından çağrılır."""
    await ElementsPage().build()


class ElementsPage:
    """Ekranın durumu ve çizimi. Her tarayıcı sekmesi kendi nesnesini alır."""

    def __init__(self) -> None:
        self.installed: list[dict[str, Any]] = []
        self.element_name: str | None = None
        self.atom_name: str | None = None
        self.document: dict[str, Any] | None = None  # içe aktarma için yüklenen dosya
        self.values: dict[str, Any] = {}  # açık olan formun değerleri

    async def build(self) -> None:
        with ui.column().classes("w-full max-w-6xl mx-auto gap-4 p-4"):
            with ui.row().classes("w-full items-center"):
                ui.label(t("Periyodik tablo")).classes("text-lg font-medium")
                ui.space()
                layout.primary("İçe aktar", self.open_import)
            self.tiles = ui.row().classes("gap-3")
            with ui.row().classes("w-full gap-4 no-wrap items-start"):
                self.atom_list = ui.column().classes("gap-2").style("width:300px")
                self.panel = ui.column().classes("gap-3").style("flex:1;min-width:0")
        await self.reload()

    # ----------------------------------------------------------------- veri ve seçim

    async def reload(self) -> None:
        """Elementleri API'den yeniden okur ve ekranı baştan çizer."""
        self.installed = await client.elements()
        names = [item["element"]["name"] for item in self.installed]
        if self.element_name not in names:
            self.element_name = names[0] if names else None
            self.atom_name = None
        self.draw_tiles()
        self.draw_atom_list()
        await self.draw_panel()

    def atoms(self) -> list[Atom]:
        """Seçili elementin atomları."""
        for item in self.installed:
            if item["element"]["name"] == self.element_name:
                return [Atom.model_validate(atom) for atom in item["element"]["atoms"]]
        return []

    def atom(self) -> Atom | None:
        """Seçili atom."""
        for atom in self.atoms():
            if atom.name == self.atom_name:
                return atom
        return None

    async def select_element(self, name: str) -> None:
        self.element_name = name
        self.atom_name = None
        self.draw_tiles()
        self.draw_atom_list()
        await self.draw_panel()

    async def select_atom(self, name: str) -> None:
        self.atom_name = name
        self.draw_atom_list()
        await self.draw_panel()

    # ---------------------------------------------------------------------- çizim

    def draw_tiles(self) -> None:
        """Periyodik tablo: her element bir kutu."""
        self.tiles.clear()
        with self.tiles:
            if not self.installed:
                ui.label(t("Henüz element yok. Bir servisin OpenAPI belgesini içe aktararak başla.")
                         ).classes("muted text-sm")
            for item in self.installed:
                element = item["element"]
                chosen = " on" if element["name"] == self.element_name else ""
                with ui.element("div").classes("tile" + chosen).on(
                        "click", partial(self.select_element, element["name"])):
                    ui.label(element["symbol"]).classes("sym")
                    ui.label(element["title"]).classes("text-sm font-medium")
                    ui.label(f"{len(element['atoms'])} {t('atom')}").classes("muted text-xs")

    def draw_atom_list(self) -> None:
        """Seçili elementin atomları, kaynaklarına göre gruplanmış."""
        self.atom_list.clear()
        if self.element_name is None:
            return
        with self.atom_list:
            resource = None
            for atom in self.atoms():
                if atom.resource != resource:
                    resource = atom.resource
                    ui.label(resource).classes("muted text-xs mono q-mt-sm")
                chosen = " on" if atom.name == self.atom_name else ""
                with ui.element("div").classes("item w-full" + chosen).on(
                        "click", partial(self.select_atom, atom.name)):
                    ui.label(atom.title).classes("text-sm font-medium")
                    ui.label(f"{atom.method} {atom.path}").classes("muted text-xs mono")
            layout.secondary("Elementi çıkar", self.remove_element).classes("w-full q-mt-md")

    async def draw_panel(self) -> None:
        """Seçili atomun arayüzü."""
        self.panel.clear()
        atom = self.atom()
        with self.panel:
            if atom is None:
                if self.element_name is not None:
                    ui.label(t("Arayüzünü görmek için bir atom seç.")).classes("muted text-sm")
                return
            with ui.row().classes("w-full items-center gap-2"):
                ui.label(atom.title).classes("text-base font-medium")
                ui.label(atom.name).classes("tag mono")
                ui.space()
                layout.secondary("Molekül üret", partial(self.generate_molecule, atom))
            ui.label(atom.description).classes("muted text-sm")
            if atom.action == "list":
                await self.draw_table(atom)
            else:
                await self.draw_form(atom)

    async def draw_table(self, atom: Atom) -> None:
        """Liste atomu: servisten kayıtları okur ve tabloyu çizer."""
        answer = await client.call_atom(self.element_name, atom.name, {})
        if not answer["ok"]:
            ui.label(answer["message"]).classes("tag bad")
            return
        options = await forms.load_options(self.element_name, atom.columns)
        SearchTable(atom.columns, answer["data"], options, file_name=atom.name).build()
        layout.secondary("Yenile", self.draw_panel)

    async def draw_form(self, atom: Atom) -> None:
        """Diğer atomlar: girdi formu ve çalıştırma düğmesi."""
        fields = ([ID_FIELD] if "{id}" in atom.path else []) + atom.inputs
        options = await forms.load_options(self.element_name, fields)
        self.values = forms.initial_values(fields)
        with ui.column().classes("box p-4 gap-3").style("width:420px"):
            forms.render_form(fields, self.values, options)
            layout.primary("Çalıştır", partial(self.run_atom, atom, fields))
        self.answer_box = ui.column().classes("w-full gap-2")

    # --------------------------------------------------------------------- eylemler

    async def run_atom(self, atom: Atom, fields: list[FieldSpec]) -> None:
        """Formu denetler, atomu çağırır ve servisin cevabını gösterir."""
        if check_form(fields, self.values):
            ui.notify(t("Formda hata var."), type="warning")
            return
        answer = await client.call_atom(self.element_name, atom.name,
                                        clean_values(fields, self.values))
        self.answer_box.clear()
        with self.answer_box:
            if answer["ok"]:
                ui.label(t("Yapıldı")).classes("tag ok")
                ui.code(json.dumps(answer["data"], ensure_ascii=False, indent=2),
                        language="json").classes("w-full")
            else:
                ui.label(f"{t('Yapılamadı')}: {answer['message']}").classes("tag bad")
                for name, message in answer["field_errors"].items():
                    ui.label(f"{name}: {message}").classes("text-sm")

    async def generate_molecule(self, atom: Atom) -> None:
        try:
            molecule = await client.generate_molecule(self.element_name, atom.name)
        except client.ApiError as error:
            ui.notify(str(error), type="negative")
            return
        ui.notify(f"{t('Molekül üretildi')}: {molecule['title']}", type="positive")

    async def remove_element(self) -> None:
        await client.remove_element(self.element_name)
        await self.reload()

    # ------------------------------------------------------------------ içe aktarma

    def open_import(self) -> None:
        """İçe aktarma penceresini açar."""
        self.document = None
        with ui.dialog() as dialog, ui.card().style("min-width:460px"):
            ui.label(t("Element içe aktar")).classes("text-base font-medium")
            address = ui.input(t("Servis adresi"), value=DEFAULT_SERVICE).props("outlined dense").classes("w-full")
            api_key = ui.input(t("Erişim anahtarı (isteğe bağlı)")).props("outlined dense").classes("w-full")
            ui.upload(label=t("OpenAPI dosyası (isteğe bağlı)"), on_upload=self.keep_document,
                      auto_upload=True, max_files=1).props("accept=.json flat bordered").classes("w-full")
            ui.label(t("Dosya verilmezse belge servis adresinden okunur.")).classes("muted text-xs")
            with ui.row().classes("gap-2"):
                layout.primary("İçe aktar", partial(self.import_element, dialog, address, api_key))
                layout.secondary("Vazgeç", dialog.close)
        dialog.open()

    async def keep_document(self, event) -> None:
        """Yüklenen OpenAPI dosyasını içe aktarma için saklar."""
        self.document = await event.file.json()

    async def import_element(self, dialog: ui.dialog, address: ui.input, api_key: ui.input) -> None:
        try:
            result = await client.import_element(address.value.strip(), api_key.value, self.document)
        except client.ApiError as error:
            ui.notify(str(error), type="negative")
            return
        dialog.close()
        self.show_import_result(result)
        await self.reload()

    def show_import_result(self, result: dict[str, Any]) -> None:
        """Kaç atomun alındığını ve anayasaya uymayan yerleri gösterir."""
        atoms = result["element"]["atoms"]
        with ui.dialog() as dialog, ui.card().style("min-width:520px"):
            ui.label(t("İçe aktarma sonucu")).classes("text-base font-medium")
            ui.label(f"{result['element']['title']}: {len(atoms)} {t('atom alındı')}").classes(
                "tag ok" if atoms else "tag bad")
            if not atoms:
                ui.label(t("Hiçbir uç anayasaya uymadığı için element takılmadı.")).classes("text-sm")
            if result["problems"]:
                ui.label(t("Anayasaya uymayan yerler")).classes("muted text-xs q-mt-sm")
            for problem in result["problems"]:
                with ui.row().classes("items-start gap-2 no-wrap"):
                    ui.label(problem["rule"]).classes("tag warn")
                    ui.label(f"{problem['where']}: {problem['message']}").classes("text-sm")
            layout.secondary("Kapat", dialog.close)
        dialog.open()
