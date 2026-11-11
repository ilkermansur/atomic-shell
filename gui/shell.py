"""Kabuğun tek sayfası.

Bütün ekranlar bu sayfanın içinde açılır. Menüler arasında geçerken tarayıcı
sayfayı yeniden yüklemez; yalnızca ortadaki bölüm değişir. Böylece geçişlerde
ekran boşalıp parlamaz ve üst çubuk yerinde kalır.
"""
from nicegui import ui

from gui import kayit, layout, mimar, molekuller

ROUTES = {
    "/": mimar.build,
    "/molekuller": molekuller.build_list,
    "/calistir/{molecule_id}": molekuller.build_run,
    "/kayit": kayit.build,
}


@ui.page("/")
@ui.page("/{_:path}")  # alt adresler de (örnek: /kayit) doğrudan açılabilsin
def shell_page() -> None:
    layout.frame()
    ui.sub_pages(ROUTES).classes("w-full")
