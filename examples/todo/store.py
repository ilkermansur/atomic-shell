"""Kayıtları tek bir JSON dosyasında saklar.

Bu bir veritabanı değildir; kabuğu sınamak için en basit kalıcı depodur.
Dosyanın biçimi:

    {"lists": [ {...}, {...} ], "todos": [ {...} ]}

Her işlev dosyayı baştan okur ve değişiklikten sonra baştan yazar. Yavaştır ama
okuması kolaydır ve örnek bir servis için yeterlidir.
"""
import json
import os
from pathlib import Path

DEFAULT_FILE = Path(__file__).parent / "data.json"

RESOURCES = ("lists", "todos")


def data_file() -> Path:
    """Veri dosyasının yeri.

    Sınamalar kendi dosyasını kullanabilsin diye yol ortam değişkeninden okunur.
    Her çağrıda yeniden okunur; böylece modül ne zaman yüklenmiş olursa olsun
    değişkenin o andaki değeri geçerli olur.
    """
    return Path(os.environ.get("TODO_DATA_FILE", DEFAULT_FILE))


def load() -> dict[str, list[dict]]:
    """Dosyadaki bütün kayıtları döndürür. Dosya yoksa boş depo döner."""
    if not data_file().exists():
        return {name: [] for name in RESOURCES}
    return json.loads(data_file().read_text(encoding="utf-8"))


def save(data: dict[str, list[dict]]) -> None:
    """Bütün kayıtları dosyaya yazar."""
    data_file().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def all_rows(resource: str) -> list[dict]:
    """Bir kaynağın bütün kayıtları."""
    return load()[resource]


def find(resource: str, row_id: int) -> dict | None:
    """Kimliği verilen kayıt; yoksa None."""
    for row in all_rows(resource):
        if row["id"] == row_id:
            return row
    return None


def insert(resource: str, values: dict) -> dict:
    """Yeni kayıt ekler ve ona sıradaki kimliği verir."""
    data = load()
    rows = data[resource]
    next_id = max((row["id"] for row in rows), default=0) + 1
    row = {"id": next_id, **values}
    rows.append(row)
    save(data)
    return row


def replace(resource: str, row_id: int, values: dict) -> dict | None:
    """Kaydın alanlarını değiştirir; kayıt yoksa None döner."""
    data = load()
    for index, row in enumerate(data[resource]):
        if row["id"] == row_id:
            data[resource][index] = {"id": row_id, **values}
            save(data)
            return data[resource][index]
    return None


def remove(resource: str, row_id: int) -> dict | None:
    """Kaydı siler ve silinen kaydı döndürür; kayıt yoksa None döner."""
    data = load()
    for index, row in enumerate(data[resource]):
        if row["id"] == row_id:
            removed = data[resource].pop(index)
            save(data)
            return removed
    return None
