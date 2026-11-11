"""Periyodik tablo: kabuğa takılmış elementler ve atomları."""
from core import store
from core.models import Atom, Element, InstalledElement

KIND = "elements"


def install(element: Element, base_url: str, api_key: str = "") -> InstalledElement:
    """Elementi kataloğa ekler. Aynı adda element varsa yenisiyle değişir."""
    installed = InstalledElement(element=element, base_url=base_url.rstrip("/"), api_key=api_key)
    store.put(KIND, element.name, installed.model_dump())
    return installed


def installed_elements() -> list[InstalledElement]:
    """Takılı bütün elementler."""
    return [InstalledElement.model_validate(data) for data in store.all_of(KIND)]


def find_element(element_name: str) -> InstalledElement | None:
    data = store.get(KIND, element_name)
    return InstalledElement.model_validate(data) if data else None


def find_atom(element_name: str, atom_name: str) -> tuple[InstalledElement, Atom] | None:
    """Atomu ve ait olduğu elementi döndürür; yoksa None."""
    installed = find_element(element_name)
    if installed is None:
        return None
    for atom in installed.element.atoms:
        if atom.name == atom_name:
            return installed, atom
    return None


def uninstall(element_name: str) -> None:
    store.delete(KIND, element_name)
