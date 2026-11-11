"""Kayıt uçları."""
from typing import Any

from fastapi import APIRouter

from core import runlog

router = APIRouter(tags=["runs"])


@router.get("/runs", summary="Çalıştırma kaydı")
def list_runs() -> list[dict[str, Any]]:
    """Bütün çalıştırmalar, en yenisi başta."""
    return runlog.recent()
