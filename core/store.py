"""Kabuğun kendi veritabanı.

Tek tablolu küçük bir SQLite deposudur. Her kayıt üç şeyden oluşur: türü
(elements, molecules, runs), anahtarı ve JSON olarak saklanan içeriği. Kabuğun
sakladığı her şey sözlük olduğu için ayrı tablolar ve sütunlar gerekmez.
"""
import json
import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS records (
        kind TEXT NOT NULL,
        key  TEXT NOT NULL,
        data TEXT NOT NULL,
        PRIMARY KEY (kind, key)
    )
"""


# Kabuk hangi klasörden başlatılırsa başlatılsın dosya proje kökünde durur.
DEFAULT_FILE = Path(__file__).parent.parent / "shell.db"


def db_file() -> Path:
    """Veritabanı dosyasının yeri. Sınamalar ortam değişkeniyle değiştirir."""
    return Path(os.environ.get("SHELL_DB", DEFAULT_FILE))


def execute(sql: str, parameters: tuple = ()) -> list[tuple]:
    """Tek bir SQL komutu çalıştırır ve dönen satırları verir.

    Her çağrıda bağlantı açılır ve kapanır. Kabuk için yeterince hızlıdır ve
    açık kalan bağlantı sorunlarını ortadan kaldırır.
    """
    with closing(sqlite3.connect(db_file())) as connection:
        connection.execute(CREATE_TABLE)
        rows = connection.execute(sql, parameters).fetchall()
        connection.commit()
        return rows


def put(kind: str, key: str, value: dict[str, Any]) -> None:
    """Kaydı yazar; aynı anahtarda kayıt varsa üzerine yazar."""
    data = json.dumps(value, ensure_ascii=False)
    execute("INSERT INTO records (kind, key, data) VALUES (?, ?, ?) "
            "ON CONFLICT (kind, key) DO UPDATE SET data = excluded.data", (kind, key, data))


def get(kind: str, key: str) -> dict[str, Any] | None:
    """Kaydı döndürür; yoksa None."""
    rows = execute("SELECT data FROM records WHERE kind = ? AND key = ?", (kind, key))
    return json.loads(rows[0][0]) if rows else None


def all_of(kind: str) -> list[dict[str, Any]]:
    """Bir türün bütün kayıtları, eklenme sırasıyla."""
    rows = execute("SELECT data FROM records WHERE kind = ? ORDER BY rowid", (kind,))
    return [json.loads(row[0]) for row in rows]


def delete(kind: str, key: str) -> None:
    """Kaydı siler; kayıt yoksa bir şey yapmaz."""
    execute("DELETE FROM records WHERE kind = ? AND key = ?", (kind, key))


def next_key(kind: str) -> str:
    """Bir tür için sıradaki numarayı verir: "1", "2", "3" ..."""
    rows = execute("SELECT key FROM records WHERE kind = ?", (kind,))
    numbers = [int(row[0]) for row in rows if row[0].isdigit()]
    return str(max(numbers, default=0) + 1)
