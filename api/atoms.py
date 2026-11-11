"""Atom uçları: bir atomu doğrudan çalıştırma.

Mimarın atom ekranı, tabloların doldurulması ve bağlantılı alanların seçenekleri
bu ucu kullanır.
"""
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core import catalog
from core.caller import call_atom
from core.models import CallResult

router = APIRouter(tags=["atoms"])


class CallRequest(BaseModel):
    values: dict[str, Any] = {}


@router.post("/atoms/{element}/{atom}/call", summary="Atomu çalıştır")
async def call(element: str, atom: str, body: CallRequest) -> CallResult:
    """Atomu verilen değerlerle çağırır ve servisin cevabını döndürür."""
    found = catalog.find_atom(element, atom)
    if found is None:
        raise HTTPException(status_code=404, detail=f"`{element}` elementinde `{atom}` atomu yok.")
    installed, atom_spec = found
    return await call_atom(installed, atom_spec, body.values)
