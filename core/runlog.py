"""Çalıştırma kaydı: hangi molekül ne zaman çalıştı ve her adımı nasıl bitti.

Kayıt yalnızca eklenir. Geri alma olmadığı için bu kayıt, yarıda kalan bir işin
hangi adımda kaldığını sonradan görmenin tek yoludur.
"""
from datetime import datetime
from typing import Any

from core import store

KIND = "runs"


def record(molecule_title: str, ok: bool, steps: list[dict[str, Any]]) -> dict[str, Any]:
    """Bir çalıştırmayı kayda ekler."""
    run = {
        "id": store.next_key(KIND),
        "time": datetime.now().isoformat(sep=" ", timespec="seconds"),
        "molecule": molecule_title,
        "ok": ok,
        "steps": steps,
    }
    store.put(KIND, run["id"], run)
    return run


def recent() -> list[dict[str, Any]]:
    """Bütün çalıştırmalar, en yenisi başta."""
    return list(reversed(store.all_of(KIND)))
