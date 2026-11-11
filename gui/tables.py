"""Tablo üretici: kayıt listesinden Excel benzeri süzülebilir tablo çizer.

Tablo AG Grid ile çizilir (NiceGUI'nin içinde gelir). Her kolon başlığının
altında bir süzgeç kutusu bulunur; birden çok kutu doluysa sonuç bunların
kesişimidir. Süzme ve sıralama tarayıcıda yapılır, sunucuya gidilmez.

Kullanıcı hangi kolonların görüneceğini seçer; seçimi sonraki açılışta da
hatırlanır. CSV, o anda ekranda görünen satırları görünen sırayla verir.
"""
from functools import partial
from typing import Any, Callable

from nicegui import app, ui

from core import rows as row_tools
from core.models import FieldSpec
from gui.i18n import lang, t

INDEX = "_index"  # satırın özgün listedeki sırası; seçilen satırı bulmak için

PAGE_SIZE = 15

# Süzgeçte büyük/küçük harf farkını Türkçe I ve İ ile birlikte kaldırır;
# core/rows.py içindeki fold ile aynı kuraldır.
TEXT_FORMATTER = ("(text) => text == null ? null : "
                  "String(text).replace(/İ/g, 'i').replace(/I/g, 'ı').toLowerCase()")

# Tablonun kendi metinlerinin Türkçesi. İngilizce seçiliyse AG Grid'in kendi
# metinleri kullanılır.
TURKISH = {
    "noRowsToShow": "Kayıt yok", "filterOoo": "Süz...", "page": "Sayfa", "of": "/",
    "to": "-", "firstPage": "İlk sayfa", "lastPage": "Son sayfa",
    "nextPage": "Sonraki sayfa", "previousPage": "Önceki sayfa",
}

# Görünen satırları görünen sırayla toplayan tarayıcı kodu. ID tablonun kimliğidir.
DISPLAYED_ROWS = """
const rows = [];
getElement(ID).api.forEachNodeAfterFilterAndSort(node => rows.push(node.data));
return rows;
"""


class SearchTable:
    """Tek bir tablo: kolon seçici, sayaç, CSV düğmesi ve süzülebilir satırlar."""

    def __init__(self, columns: list[FieldSpec], rows: list[dict[str, Any]],
                 options: dict[str, dict[Any, str]] | None = None,
                 on_select: Callable[[dict[str, Any] | None], None] | None = None,
                 file_name: str = "liste") -> None:
        self.columns = columns
        self.rows = rows
        self.options = options or {}
        self.on_select = on_select
        self.file_name = file_name  # CSV dosyasının adı ve kolon seçiminin saklandığı anahtar
        self.hidden: set[str] = set(self.saved_hidden().get(file_name, []))
        self.shown = [self.shown_row(index, row) for index, row in enumerate(rows)]

    # ------------------------------------------------------------------------ veri

    def shown_row(self, index: int, row: dict[str, Any]) -> dict[str, Any]:
        """Satırın tabloda görünecek hali: evet/hayır ve bağlı kayıt adları metne çevrilir."""
        shown: dict[str, Any] = {INDEX: index}
        for column in self.columns:
            value = row.get(column.name)
            names = self.options.get(column.name)
            shown[column.name] = names.get(value, value) if names else row_tools.display(value)
        return shown

    def visible_columns(self) -> list[FieldSpec]:
        """Kullanıcının gizlemediği kolonlar."""
        return [column for column in self.columns if column.name not in self.hidden]

    def saved_hidden(self) -> dict[str, list[str]]:
        """Kullanıcının tablo başına gizlediği kolonlar."""
        return app.storage.user.setdefault("hidden_columns", {})

    def grid_options(self) -> dict[str, Any]:
        """AG Grid'in ayarları."""
        options: dict[str, Any] = {
            "columnDefs": [{"headerName": column.title, "field": column.name,
                            "hide": column.name in self.hidden} for column in self.columns],
            "defaultColDef": {
                "sortable": True, "resizable": True, "flex": 1, "minWidth": 110,
                "filter": "agTextColumnFilter", "floatingFilter": True,
                "filterParams": {":textFormatter": TEXT_FORMATTER},
            },
            "rowData": self.shown,
            "domLayout": "autoHeight",
            "pagination": True,
            "paginationPageSize": PAGE_SIZE,
            "paginationPageSizeSelector": False,
        }
        if self.on_select:
            options["rowSelection"] = {"mode": "singleRow", "checkboxes": True,
                                       "enableClickSelection": True}
        if lang() == "tr":
            options["localeText"] = TURKISH
        return options

    # ----------------------------------------------------------------------- çizim

    def build(self) -> None:
        """Tabloyu çizer."""
        with ui.row().classes("w-full items-center gap-2"):
            self.counter = ui.label().classes("muted text-xs")
            ui.space()
            self.build_column_picker()
            ui.button(t("CSV indir"), on_click=self.download_csv, color=None).props(
                "outline dense no-caps").classes("btn-secondary")
        self.grid = ui.aggrid(self.grid_options(), theme="quartz", auto_size_columns=False).classes("w-full")
        self.grid.style("height:auto")  # NiceGUI'nin sabit yüksekliği yerine satır sayısı kadar uzar
        self.grid.on("filterChanged", self.show_count)
        if self.on_select:
            self.grid.on("selectionChanged", self.handle_select)
        self.counter.set_text(f"{len(self.rows)} / {len(self.rows)} {t('kayıt')}")

    def build_column_picker(self) -> None:
        """Hangi kolonların görüneceğinin seçildiği açılır liste."""
        with ui.button(t("Kolonlar"), icon="view_column", color=None).props(
                "outline dense no-caps").classes("btn-secondary"):
            with ui.menu(), ui.column().classes("gap-0 p-2"):
                for column in self.columns:
                    ui.checkbox(column.title, value=column.name not in self.hidden,
                                on_change=partial(self.toggle_column, column.name))

    # --------------------------------------------------------------------- eylemler

    async def show_count(self) -> None:
        """Süzgece uyan satır sayısını gösterir."""
        count = await self.grid.run_grid_method("getDisplayedRowCount")
        self.counter.set_text(f"{count} / {len(self.rows)} {t('kayıt')}")

    def toggle_column(self, column_name: str, event) -> None:
        """Bir kolonu gösterir ya da gizler ve seçimi kullanıcı için saklar."""
        if event.value:
            self.hidden.discard(column_name)
        elif len(self.visible_columns()) == 1:
            event.sender.set_value(True)  # son kolon gizlenemez
            return
        else:
            self.hidden.add(column_name)
        self.saved_hidden()[self.file_name] = sorted(self.hidden)
        self.grid.run_grid_method("setColumnsVisible", [column_name], bool(event.value))

    async def handle_select(self) -> None:
        """Seçilen satırın özgün kaydını bildirir; seçim kalktıysa None bildirir."""
        chosen = await self.grid.get_selected_row()
        self.on_select(self.rows[chosen[INDEX]] if chosen else None)

    async def download_csv(self) -> None:
        """Görünen kolonları ve ekrandaki satırları, ekrandaki sırayla CSV olarak indirir."""
        rows = await ui.run_javascript(DISPLAYED_ROWS.replace("ID", str(self.grid.id)))
        text = row_tools.to_csv(self.visible_columns(), rows)
        ui.download.content(text, f"{self.file_name}.csv")
