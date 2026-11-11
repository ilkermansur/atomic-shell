"""Form üretici: alan listesinden girdi formu çizer.

Her alan türü için bir girdi bileşeni seçilir ve alanın kısıtları yazarken
denetlenir. Mimarın atom ekranı ve adminin sihirbazı aynı üreticiyi kullanır.
"""
from functools import partial
from typing import Any

from nicegui import ui

from core.models import FieldSpec
from core.validation import check_value
from gui import client
from gui.i18n import t

# Bu sayıya kadar seçenek radyo düğmesi olarak, fazlası açılır liste olarak çizilir.
MAX_RADIO_CHOICES = 4


def initial_values(fields: list[FieldSpec], record: dict[str, Any] | None = None) -> dict[str, Any]:
    """Formun başlangıç değerleri: varsa kayıttaki değer, yoksa alanın varsayılanı."""
    record = record or {}
    return {field.name: record.get(field.name, field.default) for field in fields}


async def load_options(element: str, fields: list[FieldSpec]) -> dict[str, dict[Any, str]]:
    """Bağlantılı alanların seçeneklerini bağlı oldukları listeden okur.

    Dönen sözlük: alan adı -> {kayıt kimliği: gösterilecek ad}
    """
    options: dict[str, dict[Any, str]] = {}
    for field in fields:
        if field.ref is None:
            continue
        answer = await client.call_atom(element, field.ref, {})
        rows = answer["data"] if answer["ok"] else []
        options[field.name] = {row["id"]: str(row.get(field.ref_label, row["id"])) for row in rows}
    return options


def render_form(fields: list[FieldSpec], values: dict[str, Any],
                options: dict[str, dict[Any, str]]) -> None:
    """Alanları sırayla çizer. Girilen değerler `values` sözlüğüne yazılır."""
    for field in fields:
        with ui.column().classes("w-full gap-0"):
            render_field(field, values, options.get(field.name))
            ui.label(field.description).classes("muted text-xs")


def render_field(field: FieldSpec, values: dict[str, Any], choices: dict[Any, str] | None) -> None:
    """Alanın türüne uygun girdi bileşenini çizer."""
    label = field.title + (" *" if field.required else "")
    check = partial(check_value, field)

    if choices is not None:
        widget = ui.select(choices, label=label, validation=check).props("outlined dense")
    elif field.kind == "boolean":
        ui.label(label).classes("text-sm")
        widget = ui.radio({True: t("Evet"), False: t("Hayır")}).props("inline dense")
    elif field.kind == "choice" and len(field.choices) <= MAX_RADIO_CHOICES:
        ui.label(label).classes("text-sm")
        widget = ui.radio(field.choices).props("inline dense")
    elif field.kind == "choice":
        widget = ui.select(field.choices, label=label, validation=check).props("outlined dense")
    elif field.kind in ("integer", "number"):
        precision = 0 if field.kind == "integer" else None
        widget = ui.number(label=label, precision=precision, validation=check).props("outlined dense")
    elif field.kind == "date":
        widget = ui.input(label, validation=check).props("outlined dense type=date stack-label")
    elif field.kind == "datetime":
        widget = ui.input(label, validation=check).props("outlined dense type=datetime-local stack-label")
    else:
        widget = ui.input(label, validation=check).props("outlined dense")

    # Sıra önemli: değer bağlanırken denetim çalışmasın diye önce otomatik denetim kapatılır.
    validate_on_leave(widget)
    widget.classes("w-full").bind_value(values, field.name)


def validate_on_leave(widget) -> None:
    """Alanı yazarken değil, alandan çıkınca denetler.

    Aksi halde boş form açılır açılmaz bütün zorunlu alanlar hata gösterir.
    Radyo düğmelerinin denetimi yoktur; onlar atlanır.
    """
    if hasattr(widget, "without_auto_validation"):
        widget.without_auto_validation()
        widget.on("blur", widget.validate)
