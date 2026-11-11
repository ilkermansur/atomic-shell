"""Molekülü çalıştırır.

Sihirbaz önce bütün girdileri toplar: admin tablolardan satır seçer, formları
doldurur. Bu dosyadaki `run_molecule` sonra yazan adımları sırayla uygular.

Bir adım hata verirse durulur; sonraki adımlar denenmez ve yapılanlar geri
alınmaz. Sonuç her adım için ayrı ayrı bildirilir.
"""
from typing import Any, Literal

from pydantic import BaseModel

from core import catalog, runlog
from core.caller import call_atom
from core.models import CallResult
from core.molecules import Molecule, Step


class StepResult(BaseModel):
    """Tek adımın sonucu.

    selected : tablo adımı; adminin seçtiği kayıt kullanıldı.
    done     : atom çalıştı.
    failed   : atom hata verdi.
    skipped  : önceki bir adım hata verdiği için denenmedi.
    """

    title: str
    status: Literal["selected", "done", "failed", "skipped"]
    message: str = ""
    data: Any = None


class RunResult(BaseModel):
    ok: bool
    steps: list[StepResult]


async def run_molecule(molecule: Molecule, inputs: list[dict[str, Any]],
                       selections: list[dict[str, Any] | None]) -> RunResult:
    """Molekülü uygular.

    inputs[i]     : i. adımın formunda adminin yazdığı değerler.
    selections[i] : i. adım bir tablo adımıysa adminin seçtiği satır.
    """
    records: list[dict[str, Any] | None] = []  # her adımın ortaya koyduğu kayıt
    results: list[StepResult] = []
    stopped = False

    for index, step in enumerate(molecule.steps):
        if stopped:
            result = StepResult(title=step.title, status="skipped")
        else:
            result = await run_step(step, inputs[index], selections[index], records)
            stopped = result.status == "failed"
        records.append(result.data if isinstance(result.data, dict) else None)
        results.append(result)

    ok = not stopped
    runlog.record(molecule.title, ok, [result.model_dump() for result in results])
    return RunResult(ok=ok, steps=results)


async def run_step(step: Step, form_values: dict[str, Any], selection: dict[str, Any] | None,
                   records: list[dict[str, Any] | None]) -> StepResult:
    """Tek bir adımı çalıştırır."""
    found = catalog.find_atom(step.element, step.atom)
    if found is None:
        return StepResult(title=step.title, status="failed",
                          message=f"`{step.atom}` atomu katalogda yok.")
    installed, atom = found

    # Tablo adımı uygulamada bir şey çağırmaz; sihirbazda seçilen satır bu adımın kaydıdır.
    if atom.action == "list":
        return StepResult(title=step.title, status="selected", data=selection)

    try:
        values = resolve_values(step, form_values, records)
    except LookupError as error:
        return StepResult(title=step.title, status="failed", message=str(error))

    answer = await call_atom(installed, atom, values)
    if answer.ok:
        return StepResult(title=step.title, status="done", data=answer.data)
    return StepResult(title=step.title, status="failed", message=failure_message(answer))


def resolve_values(step: Step, form_values: dict[str, Any],
                   records: list[dict[str, Any] | None]) -> dict[str, Any]:
    """Adımın her alanının değerini kaynağına göre bulur."""
    values: dict[str, Any] = {}
    for name, source in step.fields.items():
        if source.kind == "form":
            values[name] = form_values.get(name)
        elif source.kind == "const":
            values[name] = source.value
        else:
            values[name] = record_of(source.step, records).get(source.field)
    return values


def record_of(step_index: int | None, records: list[dict[str, Any] | None]) -> dict[str, Any]:
    """Önceki bir adımın kaydı; kayıt yoksa LookupError."""
    if step_index is None or step_index >= len(records) or records[step_index] is None:
        raise LookupError("Önceki adımda kayıt seçilmedi ya da oluşturulmadı.")
    return records[step_index]


def failure_message(answer: CallResult) -> str:
    """Hata mesajına varsa alan hatalarını ekler."""
    if not answer.field_errors:
        return answer.message
    details = "; ".join(f"{name}: {message}" for name, message in answer.field_errors.items())
    return f"{answer.message} {details}"
