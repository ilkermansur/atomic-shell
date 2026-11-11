"""atomic-shell: kabuğun giriş noktası.

Tek bir FastAPI uygulaması kurar, kabuğun API'sini /api altına bağlar ve
arayüzü aynı uygulamanın üstüne giydirir.

Çalıştırma:  python3 -m uvicorn app:app --port 8100   (proje kökünden)
"""
import os
from pathlib import Path

# NiceGUI kullanıcı tercihlerini (tema, dil, gizli kolonlar) bu klasörde saklar.
# Kabuk hangi klasörden başlatılırsa başlatılsın dosyalar proje kökünde kalsın
# diye yol, NiceGUI yüklenmeden önce belirlenir.
os.environ.setdefault("NICEGUI_STORAGE_PATH", str(Path(__file__).parent / ".nicegui"))

from fastapi import FastAPI  # noqa: E402
from nicegui import ui  # noqa: E402

import api  # noqa: E402
from gui import shell  # noqa: F401  (içe alınınca kabuğun sayfasını kaydeder)

app = FastAPI(
    title="atomic-shell",
    description="İçine API uçları alan kabuk.",
    version="0.1.0",
)
app.include_router(api.router)

# Kullanıcı tercihlerini (tema, dil) saklayan çerezin imza anahtarı.
SECRET = os.environ.get("SHELL_SECRET", "yalnizca-yerel-gelistirme")

ui.run_with(app, title="atomic-shell", storage_secret=SECRET)
