"""OpenAPI belgesini okur, FastAPI anayasasına göre denetler ve atomlara çevirir.

Giriş noktası `import_document`. Belgedeki her uç için bir atom üretmeyi dener;
anayasaya uymayan uç atom olarak alınmaz ve nedeni sorun listesine yazılır.
Kural numaraları docs/07-fastapi-anayasasi.md ile aynıdır.

Bu dosya ağa çıkmaz ve hiçbir şeyi kaydetmez: sözlük alır, model döndürür.
"""
from typing import Any

from core.models import Atom, Element, FieldSpec, ImportResult, Problem

# (HTTP yöntemi, yol tek kayda mı işaret ediyor) -> eylem
ACTIONS: dict[tuple[str, bool], str] = {
    ("get", False): "list",
    ("get", True): "get",
    ("post", False): "create",
    ("put", True): "update",
    ("delete", True): "delete",
}

# Türkçe harflerin kısa adda kullanılacak karşılıkları.
ASCII = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")


def import_document(document: dict[str, Any]) -> ImportResult:
    """Belgenin tamamını içe aktarır."""
    problems: list[Problem] = []
    info = document.get("info", {})
    check_service(info, problems)

    atoms: list[Atom] = []
    for path, operations in document.get("paths", {}).items():
        for method, operation in operations.items():
            atom = read_operation(method, path, operation, document, problems)
            if atom is not None:
                atoms.append(atom)

    atoms = drop_atoms_with_broken_links(atoms, problems)
    title = info.get("title", "")
    element = Element(
        name=short_name(title),
        symbol=short_name(title)[:2].capitalize(),
        title=title,
        description=info.get("description", ""),
        version=info.get("version", ""),
        atoms=atoms,
    )
    return ImportResult(element=element, problems=problems)


# --------------------------------------------------------------------------- servis

def check_service(info: dict[str, Any], problems: list[Problem]) -> None:
    """Kural 1.1: başlık, açıklama ve sürüm dolu olmalı."""
    for key in ("title", "description", "version"):
        if not info.get(key):
            problems.append(Problem(where="servis", rule="1.1", message=f"`{key}` boş."))


def short_name(title: str) -> str:
    """Başlıktan adreslerde kullanılabilecek kısa ad üretir: 'Yapılacaklar' -> 'yapilacaklar'."""
    plain = title.translate(ASCII).lower()
    kept = [char if char.isalnum() else "_" for char in plain]
    return "".join(kept).strip("_") or "element"


# ------------------------------------------------------------------------------ uç

def read_operation(method: str, path: str, operation: dict[str, Any],
                   document: dict[str, Any], problems: list[Problem]) -> Atom | None:
    """Tek bir ucu atoma çevirir. Uç anayasaya uymuyorsa None döner."""
    where = f"{method.upper()} {path}"
    count_before = len(problems)

    parts = path.strip("/").split("/")
    resource = parts[0]
    has_id = len(parts) == 2
    action = ACTIONS.get((method, has_id))

    if len(parts) > 2 or (has_id and parts[1] != "{id}"):
        problems.append(Problem(where=where, rule="2.3",
                                message="Yol `/{kaynak}` ya da `/{kaynak}/{id}` biçiminde olmalı."))
        return None
    if action is None:
        problems.append(Problem(where=where, rule="2",
                                message="Bu yöntem ve yol birleşimi desteklenmiyor."))
        return None

    check_operation_labels(operation, resource, action, where, problems)
    check_no_required_query(operation, action, where, problems)
    if action == "create" and "201" not in operation.get("responses", {}):
        problems.append(Problem(where=where, rule="3.7", message="`create` ucu 201 döndürmeli."))

    columns = read_record_fields(operation, action, document, where, problems)
    inputs = read_input_fields(operation, action, document, where, problems)

    if len(problems) > count_before:
        return None
    return Atom(
        name=operation["operationId"], resource=resource, action=action,
        method=method.upper(), path=path, title=operation["summary"],
        description=operation["description"], inputs=inputs, columns=columns,
    )


def check_operation_labels(operation: dict[str, Any], resource: str, action: str,
                           where: str, problems: list[Problem]) -> None:
    """Kural 3.1 - 3.4: ad, etiket, başlık ve açıklama."""
    expected_id = f"{resource}_{action}"
    if operation.get("operationId") != expected_id:
        problems.append(Problem(where=where, rule="3.1",
                                message=f"`operation_id` `{expected_id}` olmalı."))
    if operation.get("tags") != [resource]:
        problems.append(Problem(where=where, rule="3.2",
                                message=f"`tags` yalnızca `{resource}` etiketini taşımalı."))
    if not operation.get("summary"):
        problems.append(Problem(where=where, rule="3.3", message="`summary` yok."))
    if not operation.get("description"):
        problems.append(Problem(where=where, rule="3.4", message="Docstring yok."))


def check_no_required_query(operation: dict[str, Any], action: str,
                            where: str, problems: list[Problem]) -> None:
    """Kural 6: uç zorunlu sorgu parametresi isteyemez."""
    for parameter in operation.get("parameters", []):
        if parameter.get("in") == "query" and parameter.get("required"):
            problems.append(Problem(where=where, rule="6",
                                    message=f"Zorunlu sorgu parametresi desteklenmiyor: `{parameter['name']}`."))


# -------------------------------------------------------------------------- modeller

def read_record_fields(operation: dict[str, Any], action: str, document: dict[str, Any],
                       where: str, problems: list[Problem]) -> list[FieldSpec]:
    """Kural 3.5: ucun döndürdüğü kayıt modelinin alanları. Tablonun kolonları buradan gelir."""
    schema = response_schema(operation)
    if action == "list":
        schema = schema.get("items", {}) if schema.get("type") == "array" else {}
    model = resolve(schema, document)
    if "properties" not in model:
        problems.append(Problem(where=where, rule="3.5",
                                message="`response_model` kayıt modelini döndürmeli."))
        return []
    if "id" not in model["properties"]:
        problems.append(Problem(where=where, rule="2.2", message="Kayıt modelinde `id` alanı yok."))
    return read_fields(model, document, where, problems)


def read_input_fields(operation: dict[str, Any], action: str, document: dict[str, Any],
                      where: str, problems: list[Problem]) -> list[FieldSpec]:
    """`create` ve `update` uçlarının girdi modelindeki alanlar. Form buradan üretilir."""
    if action not in ("create", "update"):
        return []
    content = operation.get("requestBody", {}).get("content", {})
    model = resolve(content.get("application/json", {}).get("schema", {}), document)
    if "properties" not in model:
        problems.append(Problem(where=where, rule="4", message="Girdi modeli yok."))
        return []
    return read_fields(model, document, where, problems)


def response_schema(operation: dict[str, Any]) -> dict[str, Any]:
    """Başarılı cevabın (200 ya da 201) şeması; yoksa boş sözlük."""
    responses = operation.get("responses", {})
    answer = responses.get("200") or responses.get("201") or {}
    return answer.get("content", {}).get("application/json", {}).get("schema", {})


def resolve(schema: dict[str, Any], document: dict[str, Any]) -> dict[str, Any]:
    """Şema başka bir modele işaret ediyorsa (`$ref`) o modeli döndürür."""
    reference = schema.get("$ref")
    if reference is None:
        return schema
    name = reference.split("/")[-1]
    return document.get("components", {}).get("schemas", {}).get(name, {})


# --------------------------------------------------------------------------- alanlar

def read_fields(model: dict[str, Any], document: dict[str, Any],
                where: str, problems: list[Problem]) -> list[FieldSpec]:
    """Bir modelin bütün alanlarını okur. Okunamayan alan sorun olarak yazılır."""
    required_names = model.get("required", [])
    fields: list[FieldSpec] = []
    for name, spec in model["properties"].items():
        field = read_field(name, spec, name in required_names, document, where, problems)
        if field is not None:
            fields.append(field)
    return fields


def read_field(name: str, spec: dict[str, Any], required: bool, document: dict[str, Any],
               where: str, problems: list[Problem]) -> FieldSpec | None:
    """Tek bir alanı okur."""
    where = f"{where} › {name}"
    value = value_schema(spec, document)
    kind = field_kind(value)

    if not spec.get("title") or not spec.get("description"):
        problems.append(Problem(where=where, rule="4.1", message="`title` ve `description` zorunlu."))
    if kind is None:
        problems.append(Problem(where=where, rule="4.2",
                                message="Alan türü desteklenmiyor (iç içe model ya da liste olabilir)."))
    if kind is None or not spec.get("title") or not spec.get("description"):
        return None

    return FieldSpec(
        name=name, title=spec["title"], description=spec["description"], kind=kind,
        required=required, default=spec.get("default"), choices=field_choices(value),
        min_length=value.get("minLength"), max_length=value.get("maxLength"),
        pattern=value.get("pattern"),
        minimum=value.get("minimum"), maximum=value.get("maximum"),
        exclusive_minimum=value.get("exclusiveMinimum"),
        exclusive_maximum=value.get("exclusiveMaximum"),
        ref=spec.get("x-ref"), ref_label=spec.get("x-ref-label"),
    )


def value_schema(spec: dict[str, Any], document: dict[str, Any]) -> dict[str, Any]:
    """Alanın değerini tarif eden şemayı bulur.

    Pydantic isteğe bağlı alanı `anyOf: [gerçek tür, null]` olarak, Enum
    sınıflarını ise `$ref` olarak yazar; ikisi de burada açılır.
    """
    if "anyOf" in spec:
        variants = [variant for variant in spec["anyOf"] if variant.get("type") != "null"]
        spec = variants[0] if len(variants) == 1 else {}
    return resolve(spec, document)


def field_kind(value: dict[str, Any]) -> str | None:
    """Şemadan alan türünü çıkarır; desteklenmeyen tür için None döner."""
    if "enum" in value or "const" in value:
        return "choice"
    kinds = {"boolean": "boolean", "integer": "integer", "number": "number"}
    if value.get("type") in kinds:
        return kinds[value["type"]]
    if value.get("type") == "string":
        formats = {"date": "date", "date-time": "datetime"}
        return formats.get(value.get("format", ""), "text")
    return None


def field_choices(value: dict[str, Any]) -> list[Any]:
    """Seçenekli alanın seçenekleri; seçenekli değilse boş liste."""
    if "const" in value:
        return [value["const"]]
    return list(value.get("enum", []))


# ----------------------------------------------------------------- bağlantılı alanlar

def drop_atoms_with_broken_links(atoms: list[Atom], problems: list[Problem]) -> list[Atom]:
    """Bağlantılı alanı var olmayan bir listeye işaret eden atomları ayıklar."""
    lists = {atom.name: atom for atom in atoms if atom.action == "list"}
    kept: list[Atom] = []
    for atom in atoms:
        broken = [field for field in atom.inputs + atom.columns
                  if field.ref is not None and not link_is_valid(field, lists)]
        for field in broken:
            problems.append(Problem(
                where=f"{atom.method} {atom.path} › {field.name}", rule="4",
                message=f"Bağlantılı alan geçersiz: `{field.ref}` listesi ya da "
                        f"`{field.ref_label}` alanı bulunamadı."))
        if not broken:
            kept.append(atom)
    return kept


def link_is_valid(field: FieldSpec, lists: dict[str, Atom]) -> bool:
    """Alanın işaret ettiği list atomu ve o listedeki etiket alanı var mı."""
    target = lists.get(field.ref or "")
    if target is None:
        return False
    return any(column.name == field.ref_label for column in target.columns)
