"""Örnek servisin veri modelleri.

İki kaynak var: listeler (lists) ve görevler (todos). Her kaynak için üç model
yazılır: kayıt, oluşturma ve güncelleme. Kabuk formları ve tablo kolonlarını bu
modellerden üretir; bu yüzden her alanın başlığı, açıklaması ve kısıtı burada
tanımlanır.
"""
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

Color = Literal["mavi", "yeşil", "sarı", "kırmızı"]


# ----------------------------------------------------------------------- listeler

class ListCreate(BaseModel):
    name: str = Field(title="Ad", description="Listenin adı. Benzersiz olmalıdır.",
                      min_length=2, max_length=40)
    color: Color = Field(default="mavi", title="Renk", description="Listenin etiketi.")


class ListUpdate(ListCreate):
    """Güncellemede oluşturmadaki alanların aynısı istenir."""


class TodoList(ListCreate):
    id: int = Field(title="No", description="Listenin kimliği.")


# ------------------------------------------------------------------------ görevler

class TodoCreate(BaseModel):
    title: str = Field(title="Başlık", description="Görevin kısa adı.",
                       min_length=3, max_length=80)
    code: str = Field(title="Kod", description="Sekiz haneli iş kodu. Benzersiz olmalıdır.",
                      pattern=r"^\d{8}$")
    list_id: int = Field(title="Liste", description="Görevin ait olduğu liste.",
                         json_schema_extra={"x-ref": "lists_list", "x-ref-label": "name"})
    priority: int = Field(default=3, title="Öncelik",
                          description="1 en düşük, 5 en yüksek.", ge=1, le=5)
    done: bool = Field(default=False, title="Tamamlandı", description="Görev bitti mi.")
    due: date | None = Field(default=None, title="Son tarih",
                             description="Görevin bitmesi gereken gün. Boş bırakılabilir.")


class TodoUpdate(TodoCreate):
    """Güncellemede oluşturmadaki alanların aynısı istenir."""


class Todo(TodoCreate):
    id: int = Field(title="No", description="Görevin kimliği.")
