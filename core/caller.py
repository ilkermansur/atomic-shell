"""Bir atomu çağırır: elementin servisine HTTP isteği atar ve cevabı çevirir.

Çağrı ne olursa olsun bir CallResult döner. Servis hata verse ya da hiç cevap
vermese bile istisna fırlatılmaz; arayüz ve molekül çalıştırıcı tek bir biçimle
uğraşır.
"""
from typing import Any

import httpx

from core.models import Atom, CallResult, InstalledElement

# Sınamalar gerçek ağ yerine doğrudan bir uygulamaya bağlanmak için bunu değiştirir.
TRANSPORT: httpx.AsyncBaseTransport | None = None

TIMEOUT_SECONDS = 10


async def call_atom(installed: InstalledElement, atom: Atom, values: dict[str, Any]) -> CallResult:
    """Atomu verilen değerlerle çağırır.

    `values` içindeki `id` yol parametresine, atomun girdi alanları istek
    gövdesine konur.
    """
    path = atom.path.replace("{id}", str(values.get("id", "")))
    body = {field.name: values.get(field.name) for field in atom.inputs} if atom.inputs else None
    try:
        async with open_client(installed) as client:
            response = await client.request(atom.method, path, json=body)
    except httpx.HTTPError:
        return CallResult(ok=False, message=f"{installed.element.title} servisine ulaşılamadı.")
    return read_response(response)


async def fetch_document(base_url: str) -> dict[str, Any] | None:
    """Servisin OpenAPI belgesini adresinden okur; okunamazsa None döner."""
    try:
        async with httpx.AsyncClient(base_url=base_url, transport=TRANSPORT,
                                     timeout=TIMEOUT_SECONDS) as client:
            response = await client.get("/openapi.json")
            return response.json() if response.status_code == 200 else None
    except (httpx.HTTPError, ValueError):
        return None


def open_client(installed: InstalledElement) -> httpx.AsyncClient:
    """Elementin servisine bağlanan istemci; erişim anahtarı varsa başlığa eklenir."""
    headers = {"X-API-Key": installed.api_key} if installed.api_key else {}
    return httpx.AsyncClient(base_url=installed.base_url, headers=headers,
                             transport=TRANSPORT, timeout=TIMEOUT_SECONDS)


def read_response(response: httpx.Response) -> CallResult:
    """Servisin cevabını CallResult'a çevirir (anayasa, bölüm 5)."""
    status = response.status_code
    try:
        payload = response.json()
    except ValueError:
        payload = None

    if 200 <= status < 300:
        return CallResult(ok=True, status=status, data=payload)

    detail = payload.get("detail") if isinstance(payload, dict) else None
    if status == 422 and isinstance(detail, list):
        return CallResult(ok=False, status=status, message="Girdi hatalı.",
                          field_errors=read_field_errors(detail))
    if isinstance(detail, str):
        return CallResult(ok=False, status=status, message=detail)
    return CallResult(ok=False, status=status, message=f"Servis {status} koduyla hata döndürdü.")


def read_field_errors(detail: list[dict[str, Any]]) -> dict[str, str]:
    """FastAPI'nin 422 cevabındaki hataları alan adı -> mesaj sözlüğüne çevirir."""
    errors: dict[str, str] = {}
    for item in detail:
        location = item.get("loc", [])
        field_name = str(location[-1]) if location else ""
        errors[field_name] = item.get("msg", "Geçersiz değer.")
    return errors
