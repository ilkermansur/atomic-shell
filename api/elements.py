"""Element uçları: içe aktarma, listeleme, çıkarma."""
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core import caller, catalog
from core.models import ImportResult, InstalledElement
from core.openapi_import import import_document

router = APIRouter(tags=["elements"])


class ImportRequest(BaseModel):
    base_url: str  # kabuğun uçları çağıracağı servis adresi
    api_key: str = ""
    document: dict[str, Any] | None = None  # verilmezse servis adresinden okunur


@router.post("/elements/import", summary="Element içe aktar")
async def import_element(body: ImportRequest) -> ImportResult:
    """OpenAPI belgesini anayasaya göre denetler ve kurala uyan uçları atom olarak alır."""
    document = body.document or await caller.fetch_document(body.base_url)
    if document is None:
        raise HTTPException(status_code=502,
                            detail="OpenAPI belgesi servis adresinden okunamadı.")
    result = import_document(document)
    if result.element.atoms:
        catalog.install(result.element, body.base_url, body.api_key)
    return result


@router.get("/elements", summary="Takılı elementler")
def list_elements() -> list[InstalledElement]:
    """Periyodik tablo: takılı elementler ve atomları."""
    return catalog.installed_elements()


@router.delete("/elements/{name}", summary="Elementi çıkar")
def remove_element(name: str) -> dict[str, bool]:
    """Elementi katalogdan çıkarır. Servisin kendisine dokunulmaz."""
    catalog.uninstall(name)
    return {"ok": True}
