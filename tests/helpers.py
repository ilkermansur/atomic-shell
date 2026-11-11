"""Sınamaların ortak hazırlığı.

Kabuğun veritabanını ve örnek servisin veri dosyasını geçici dosyalara
yönlendirir, atom çağrılarını gerçek ağ yerine doğrudan örnek servise bağlar.
"""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "examples" / "todo"))

TEMP = Path(tempfile.mkdtemp())
os.environ["SHELL_DB"] = str(TEMP / "shell.db")
os.environ["TODO_DATA_FILE"] = str(TEMP / "todo.json")

import httpx  # noqa: E402

import store as todo_store  # noqa: E402  (örnek servisin deposu)
from core import caller, catalog  # noqa: E402
from core.models import InstalledElement  # noqa: E402
from core.openapi_import import import_document  # noqa: E402
from main import app as todo_app  # noqa: E402  (örnek servis)

BASE_URL = "http://todo.test"

# Atom çağrıları ağa çıkmadan doğrudan örnek servise gider.
caller.TRANSPORT = httpx.ASGITransport(app=todo_app)


def reset() -> InstalledElement:
    """Her şeyi boşaltır ve örnek servisi kabuğa takar."""
    db_file = Path(os.environ["SHELL_DB"])
    if db_file.exists():
        db_file.unlink()
    todo_store.save({"lists": [], "todos": []})
    result = import_document(todo_app.openapi())
    return catalog.install(result.element, BASE_URL)


def atom_of(installed: InstalledElement, name: str):
    return next(atom for atom in installed.element.atoms if atom.name == name)
