"""Her ekranda ortak olan parçalar: üst çubuk ve düğmeler."""
from functools import partial
from typing import Callable

from nicegui import app, ui

from gui import theme
from gui.i18n import lang, t

PAGES = [("/", "Elementler"), ("/molekuller", "Moleküller"), ("/kayit", "Kayıt")]


def frame() -> None:
    """Üst çubuğu çizer: ekran geçişi, tema ve dil düğmeleri."""
    dark = theme.apply()
    links: dict[str, ui.link] = {}
    with ui.header().classes("items-center"):
        ui.label("atomic-shell").classes("text-base font-medium")
        ui.space()
        for path, title in PAGES:
            links[path] = ui.link(t(title), path).classes("nav")
        ui.button(icon="contrast", on_click=partial(theme.toggle, dark), color=None).props(
            "flat round dense").classes("btn-secondary").tooltip(t("Koyu / açık tema"))
        ui.button("EN" if lang() == "tr" else "TR", on_click=switch_language, color=None).props(
            "outline dense no-caps").classes("btn-secondary").tooltip(t("Dil"))

    # Ekran değiştikçe menüde o ekranın bağlantısı işaretlenir.
    mark_active(links, ui.context.client.request.url.path)
    ui.context.client.sub_pages_router.on_path_changed(partial(mark_active, links))


def mark_active(links: dict[str, ui.link], path: str) -> None:
    """Menüde açık olan ekranın bağlantısını vurgular."""
    for link_path, link in links.items():
        if link_path == section_of(path):
            link.classes(add="on")
        else:
            link.classes(remove="on")


def section_of(path: str) -> str:
    """Adresin hangi menüye ait olduğunu söyler; sihirbaz Moleküller'e aittir."""
    if path.startswith(("/molekuller", "/calistir")):
        return "/molekuller"
    if path.startswith("/kayit"):
        return "/kayit"
    return "/"


def switch_language() -> None:
    app.storage.user["lang"] = "tr" if lang() == "en" else "en"
    ui.navigate.reload()


def primary(text: str, on_click: Callable) -> ui.button:
    """Ekrandaki asıl eylemin düğmesi."""
    return ui.button(t(text), on_click=on_click, color=None).props("unelevated no-caps").classes("btn-primary")


def secondary(text: str, on_click: Callable) -> ui.button:
    return ui.button(t(text), on_click=on_click, color=None).props("outline no-caps").classes("btn-secondary")
