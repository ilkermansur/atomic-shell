"""Arayüzün kabuğun API'sine konuştuğu tek yer.

Arayüz çekirdeği doğrudan çağırmaz; her iş buradaki işlevlerle, HTTP üzerinden
yapılır. Böylece arayüzde yapılabilen her şey API'de de vardır.
"""
import os
from typing import Any

import httpx


class ApiError(Exception):
    """API'nin döndürdüğü, kullanıcıya gösterilecek hata."""


def api_url() -> str:
    """Kabuğun API adresi. Arayüz ve API aynı süreçte çalışır; adres kendi adresidir."""
    return os.environ.get("SHELL_URL", "http://127.0.0.1:8100") + "/api"


async def request(method: str, path: str, body: dict[str, Any] | None = None) -> Any:
    """API'ye istek atar ve cevabın gövdesini döndürür; hata durumunda ApiError fırlatır."""
    try:
        async with httpx.AsyncClient(base_url=api_url(), timeout=30) as http:
            response = await http.request(method, path, json=body)
    except httpx.HTTPError as error:
        raise ApiError("Kabuğun API'sine ulaşılamadı.") from error
    if response.status_code >= 400:
        raise ApiError(str(response.json().get("detail", "Beklenmeyen bir hata oluştu.")))
    return response.json()


async def elements() -> list[dict[str, Any]]:
    return await request("GET", "/elements")


async def import_element(base_url: str, api_key: str, document: dict[str, Any] | None) -> dict[str, Any]:
    body = {"base_url": base_url, "api_key": api_key, "document": document}
    return await request("POST", "/elements/import", body)


async def remove_element(name: str) -> None:
    await request("DELETE", f"/elements/{name}")


async def call_atom(element: str, atom: str, values: dict[str, Any]) -> dict[str, Any]:
    return await request("POST", f"/atoms/{element}/{atom}/call", {"values": values})


async def molecules() -> list[dict[str, Any]]:
    return await request("GET", "/molecules")


async def generate_molecule(element: str, atom: str) -> dict[str, Any]:
    return await request("POST", "/molecules/generate", {"element": element, "atom": atom})


async def remove_molecule(molecule_id: str) -> None:
    await request("DELETE", f"/molecules/{molecule_id}")


async def run_molecule(molecule_id: str, inputs: list[dict[str, Any]],
                       selections: list[dict[str, Any] | None]) -> dict[str, Any]:
    body = {"inputs": inputs, "selections": selections}
    return await request("POST", f"/molecules/{molecule_id}/run", body)


async def runs() -> list[dict[str, Any]]:
    return await request("GET", "/runs")
