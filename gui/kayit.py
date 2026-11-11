"""Kayıt ekranı: çalıştırılan moleküller ve her adımının sonucu."""
from nicegui import ui

from gui import client
from gui.i18n import t
from gui.molekuller import STATUS


async def build() -> None:
    """Kayıt ekranını kurar. gui/shell.py tarafından çağrılır."""
    runs = await client.runs()
    with ui.column().classes("w-full max-w-4xl mx-auto gap-3 p-4"):
        ui.label(t("Kayıt")).classes("text-lg font-medium")
        if not runs:
            ui.label(t("Henüz çalıştırma yok.")).classes("muted text-sm")
        for run in runs:
            draw_run(run)


def draw_run(run: dict) -> None:
    """Tek bir çalıştırma: başlık satırı ve altında adımları."""
    with ui.column().classes("box p-3 gap-2 w-full"):
        with ui.row().classes("w-full items-center gap-3"):
            ui.label(run["time"]).classes("muted text-xs mono")
            ui.label(run["molecule"]).classes("text-sm font-medium")
            ui.space()
            ui.label(t("tamamlandı") if run["ok"] else t("yarıda kaldı")).classes(
                "tag ok" if run["ok"] else "tag bad")
        for index, step in enumerate(run["steps"]):
            text, style = STATUS[step["status"]]
            with ui.row().classes("items-center gap-2"):
                ui.label(f"{index + 1}. {step['title']}").classes("text-sm")
                ui.label(t(text)).classes(style)
                ui.label(step["message"]).classes("muted text-xs")
