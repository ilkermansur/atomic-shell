"""Tablo için yardımcılar: değerleri gösterme, kolon bazında süzme, CSV üretme.

Arayüzdeki tablo süzmeyi tarayıcıda aynı kuralla yapar (gui/tables.py);
filter_rows API ve betikler için aynı kuralın Python karşılığıdır.
"""
import csv
import io
from typing import Any

from core.models import FieldSpec


def display(value: Any) -> str:
    """Bir değerin tabloda ve CSV'de görünecek hali."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Evet" if value else "Hayır"
    return str(value)


def fold(text: str) -> str:
    """Aramada büyük/küçük harf farkını kaldırır; Türkçe I ve İ harflerini doğru çevirir."""
    return text.replace("İ", "i").replace("I", "ı").lower()


def filter_rows(rows: list[dict[str, Any]], filters: dict[str, str]) -> list[dict[str, Any]]:
    """Her dolu arama kutusuna uyan satırları döndürür.

    Birden çok kolonda arama yapılmışsa sonuç bunların kesişimidir: satır
    aramaların hepsine uymalıdır.
    """
    active = {column: fold(text) for column, text in filters.items() if text}
    return [row for row in rows
            if all(wanted in fold(display(row.get(column))) for column, wanted in active.items())]


def to_csv(columns: list[FieldSpec], rows: list[dict[str, Any]]) -> str:
    """Satırları CSV metnine çevirir; ilk satır kolon başlıklarıdır.

    Başa eklenen işaret (BOM) Excel'in Türkçe harfleri doğru açmasını sağlar.
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([column.title for column in columns])
    for row in rows:
        writer.writerow([display(row.get(column.name)) for column in columns])
    return "﻿" + buffer.getvalue()
