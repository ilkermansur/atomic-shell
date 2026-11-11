"""Molekül: sıralı adımlar ve her adımın her alanı için değerin nereden geleceği.

Molekül kod değil veridir; kabuğun veritabanında saklanır. Bu dosya molekül
modelini, saklamayı ve bir atomdan hazır molekül üretmeyi içerir. Çalıştırma
core/runner.py içindedir.
"""
from typing import Any, Literal

from pydantic import BaseModel

from core import store
from core.models import Atom, InstalledElement

KIND = "molecules"


class Source(BaseModel):
    """Bir alanın değerinin nereden geleceği.

    form  : admin sihirbazda yazar. `step` ve `field` doluysa form o kayıttaki
            değerle dolu gelir (güncellemede olduğu gibi).
    const : tasarımcının belirlediği sabit değer.
    step  : daha önceki bir adımın kaydından bir alan.
    """

    kind: Literal["form", "const", "step"]
    label: str = ""  # form: sihirbazda görünen etiket
    value: Any = None  # const: sabit değer
    step: int | None = None  # kaynak adımın sırası (0'dan başlar)
    field: str | None = None  # kaynak adımın kaydındaki alan


class Step(BaseModel):
    """Molekülün tek adımı: bir atom ve alanlarının kaynakları."""

    element: str
    atom: str
    title: str
    fields: dict[str, Source] = {}


class Molecule(BaseModel):
    id: str = ""
    title: str
    description: str = ""
    steps: list[Step]


# ---------------------------------------------------------------------------- saklama

def save(molecule: Molecule) -> Molecule:
    """Molekülü kaydeder; kimliği yoksa sıradaki numarayı verir."""
    if not molecule.id:
        molecule.id = store.next_key(KIND)
    store.put(KIND, molecule.id, molecule.model_dump())
    return molecule


def all_molecules() -> list[Molecule]:
    return [Molecule.model_validate(data) for data in store.all_of(KIND)]


def find(molecule_id: str) -> Molecule | None:
    data = store.get(KIND, molecule_id)
    return Molecule.model_validate(data) if data else None


def remove(molecule_id: str) -> None:
    store.delete(KIND, molecule_id)


# ------------------------------------------------------------------- atomdan üretme

def generate(installed: InstalledElement, atom: Atom) -> Molecule:
    """Bir atomdan çalıştırılabilir bir molekül üretir.

    list ve create atomları tek adımlı molekül olur. Tek kayda dokunan atomlar
    (get, update, delete) hangi kayıt üzerinde çalışacaklarını bilmek zorundadır;
    bu yüzden önlerine aynı kaynağın listesinden bir "seç" adımı konur.
    """
    element_name = installed.element.name
    if atom.action == "list":
        steps = [Step(element=element_name, atom=atom.name, title=atom.title)]
    elif atom.action == "create":
        steps = [Step(element=element_name, atom=atom.name, title=atom.title,
                      fields=form_sources(atom))]
    else:
        list_atom = find_list_atom(installed, atom.resource)
        if list_atom is None:
            raise ValueError(f"`{atom.resource}` kaynağının listesi olmadığı için kayıt seçilemez.")
        select = Step(element=element_name, atom=list_atom.name, title=list_atom.title)
        fields = {"id": Source(kind="step", step=0, field="id"),
                  **form_sources(atom, prefill_from=0)}
        steps = [select, Step(element=element_name, atom=atom.name, title=atom.title, fields=fields)]
    return Molecule(title=atom.title, description=atom.description, steps=steps)


def form_sources(atom: Atom, prefill_from: int | None = None) -> dict[str, Source]:
    """Atomun bütün girdi alanlarını "formda sor" olarak işaretler."""
    return {field.name: Source(kind="form", label=field.title, step=prefill_from,
                               field=field.name if prefill_from is not None else None)
            for field in atom.inputs}


def find_list_atom(installed: InstalledElement, resource: str) -> Atom | None:
    for atom in installed.element.atoms:
        if atom.resource == resource and atom.action == "list":
            return atom
    return None


def needs_selection(molecule: Molecule, index: int) -> bool:
    """Sonraki adımlardan biri bu adımın kaydını kullanıyor mu.

    Kullanıyorsa admin bu adımın tablosundan bir satır seçmek zorundadır.
    """
    for step in molecule.steps[index + 1:]:
        if any(source.step == index for source in step.fields.values()):
            return True
    return False
