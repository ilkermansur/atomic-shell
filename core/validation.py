"""Form değerlerini alanın kısıtlarına göre denetler.

Aynı denetimi servis de yapar; burada amaç hatayı istek atmadan, kullanıcı
yazarken göstermektir. Mesajlar kullanıcıya gösterilecek cümlelerdir.
"""
import re
from typing import Any

from core.models import FieldSpec


def is_empty(value: Any) -> bool:
    return value is None or value == ""


def check_value(field: FieldSpec, value: Any) -> str | None:
    """Değer geçerliyse None, değilse hata mesajı döndürür."""
    if is_empty(value):
        return "Bu alan zorunlu." if field.required else None
    if field.kind == "text":
        return check_text(field, str(value))
    if field.kind in ("integer", "number"):
        return check_number(field, value)
    if field.kind == "choice" and value not in field.choices:
        return "Seçeneklerden biri olmalı."
    return None


def check_text(field: FieldSpec, text: str) -> str | None:
    if field.min_length is not None and len(text) < field.min_length:
        return f"En az {field.min_length} karakter olmalı."
    if field.max_length is not None and len(text) > field.max_length:
        return f"En çok {field.max_length} karakter olabilir."
    if field.pattern is not None and re.search(field.pattern, text) is None:
        return f"Biçim uygun değil. Beklenen: {field.pattern}"
    return None


def check_number(field: FieldSpec, value: Any) -> str | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "Sayı olmalı."
    if field.kind == "integer" and not number.is_integer():
        return "Tam sayı olmalı."
    if field.minimum is not None and number < field.minimum:
        return f"En az {field.minimum:g} olmalı."
    if field.maximum is not None and number > field.maximum:
        return f"En çok {field.maximum:g} olabilir."
    if field.exclusive_minimum is not None and number <= field.exclusive_minimum:
        return f"{field.exclusive_minimum:g} değerinden büyük olmalı."
    if field.exclusive_maximum is not None and number >= field.exclusive_maximum:
        return f"{field.exclusive_maximum:g} değerinden küçük olmalı."
    return None


def check_form(fields: list[FieldSpec], values: dict[str, Any]) -> dict[str, str]:
    """Formun bütün alanlarını denetler; alan adı -> hata mesajı döndürür."""
    errors: dict[str, str] = {}
    for field in fields:
        message = check_value(field, values.get(field.name))
        if message is not None:
            errors[field.name] = message
    return errors


def clean_values(fields: list[FieldSpec], values: dict[str, Any]) -> dict[str, Any]:
    """Form değerlerini servise gönderilecek hale getirir.

    Boş metinler None olur; tam sayı alanlarındaki 3.0 gibi değerler 3 olur
    (sayı kutusu her zaman ondalıklı sayı verir).
    """
    cleaned: dict[str, Any] = {}
    for field in fields:
        value = values.get(field.name)
        if is_empty(value):
            cleaned[field.name] = None
        elif field.kind == "integer" and float(value).is_integer():
            cleaned[field.name] = int(float(value))
        else:
            cleaned[field.name] = value
    return cleaned
