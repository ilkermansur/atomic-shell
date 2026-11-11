"""Molekül uçları: üretme, listeleme, silme, çalıştırma."""
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core import catalog, molecules
from core.molecules import Molecule
from core.runner import RunResult, run_molecule

router = APIRouter(tags=["molecules"])


class GenerateRequest(BaseModel):
    element: str
    atom: str


class RunRequest(BaseModel):
    inputs: list[dict[str, Any]]  # adım başına form değerleri
    selections: list[dict[str, Any] | None]  # adım başına seçilen satır


@router.get("/molecules", summary="Moleküller")
def list_molecules() -> list[Molecule]:
    return molecules.all_molecules()


@router.post("/molecules/generate", summary="Atomdan molekül üret")
def generate(body: GenerateRequest) -> Molecule:
    """Bir atomdan çalıştırılabilir bir molekül üretir ve kaydeder."""
    found = catalog.find_atom(body.element, body.atom)
    if found is None:
        raise HTTPException(status_code=404, detail="Atom bulunamadı.")
    try:
        molecule = molecules.generate(*found)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return molecules.save(molecule)


@router.delete("/molecules/{molecule_id}", summary="Molekülü sil")
def remove(molecule_id: str) -> dict[str, bool]:
    molecules.remove(molecule_id)
    return {"ok": True}


@router.post("/molecules/{molecule_id}/run", summary="Molekülü çalıştır")
async def run(molecule_id: str, body: RunRequest) -> RunResult:
    """Sihirbazda toplanan girdilerle molekülü uygular."""
    molecule = molecules.find(molecule_id)
    if molecule is None:
        raise HTTPException(status_code=404, detail="Molekül bulunamadı.")
    if len(body.inputs) != len(molecule.steps) or len(body.selections) != len(molecule.steps):
        raise HTTPException(status_code=422, detail="Her adım için bir girdi ve bir seçim gönderilmeli.")
    return await run_molecule(molecule, body.inputs, body.selections)
