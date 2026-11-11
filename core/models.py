"""Kabuğun çekirdek veri modelleri.

İçe aktarıcı bir OpenAPI belgesini bu modellere çevirir; kabuğun geri kalanı
(katalog, form ve tablo üreticileri, molekül çalıştırıcı) yalnızca bunları
tanır, OpenAPI'yi bilmez.
"""
from typing import Any, Literal

from pydantic import BaseModel

# Formda hangi tür girdi alanı çizileceğini belirler.
FieldKind = Literal["text", "integer", "number", "boolean", "choice", "date", "datetime"]

# Atomun ne yaptığı; kabuk arayüzü buna göre seçer (tablo, form, silme onayı).
Action = Literal["list", "get", "create", "update", "delete"]

# Eylemi yazan atomlar. Bunlar sihirbazın sonunda, diğerleri sihirbaz sırasında çalışır.
WRITING_ACTIONS = ("create", "update", "delete")


class FieldSpec(BaseModel):
    """Bir modelin tek alanı: formda bir girdi, tabloda bir kolon."""

    name: str
    title: str
    description: str
    kind: FieldKind
    required: bool = True
    default: Any = None
    choices: list[Any] = []

    # Kısıtlar; yalnızca modelde tanımlı olanlar doludur.
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    minimum: float | None = None
    maximum: float | None = None
    exclusive_minimum: float | None = None
    exclusive_maximum: float | None = None

    # Bağlantılı alan: seçenekler başka bir kaynağın list atomundan gelir.
    ref: str | None = None
    ref_label: str | None = None


class Atom(BaseModel):
    """İçe aktarılmış tek bir API ucu."""

    name: str  # operation_id, örnek: todos_create
    resource: str  # örnek: todos
    action: Action
    method: str  # GET, POST, PUT, DELETE
    path: str  # örnek: /todos/{id}
    title: str
    description: str
    inputs: list[FieldSpec] = []  # create ve update için form alanları
    columns: list[FieldSpec] = []  # ucun döndürdüğü kaydın alanları


class Element(BaseModel):
    """İçe aktarılmış bir servis ve atomları."""

    name: str  # adreslerde ve kayıtlarda kullanılan kısa ad, örnek: yapilacaklar
    symbol: str  # periyodik tablodaki iki harf, örnek: Ya
    title: str
    description: str
    version: str
    atoms: list[Atom] = []


class Problem(BaseModel):
    """Belgenin anayasaya uymayan bir yeri."""

    where: str  # örnek: "POST /todos" ya da "POST /todos › code"
    rule: str  # anayasadaki kural numarası, örnek: "3.3"
    message: str


class ImportResult(BaseModel):
    """İçe aktarmanın sonucu: kurala uyan atomlarıyla element ve bulunan sorunlar."""

    element: Element
    problems: list[Problem] = []


class InstalledElement(BaseModel):
    """Kabuğa takılmış bir element: atomları ve servise nasıl ulaşılacağı."""

    element: Element
    base_url: str  # servisin temel adresi, örnek: http://localhost:8101
    api_key: str = ""  # servis istiyorsa X-API-Key başlığında gönderilir


class CallResult(BaseModel):
    """Bir atom çağrısının sonucu. Hata da bir sonuçtur; istisna fırlatılmaz."""

    ok: bool
    status: int = 0  # HTTP durum kodu; servise ulaşılamadıysa 0
    data: Any = None  # başarılıysa servisin döndürdüğü kayıt ya da liste
    message: str = ""  # başarısızsa kullanıcıya gösterilecek cümle
    field_errors: dict[str, str] = {}  # girdi hatalarında alan adı -> mesaj
