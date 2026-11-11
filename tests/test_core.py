"""Çekirdeğin sınamaları: depo, katalog, atom çağırma, denetim, tablo, molekül, çalıştırıcı.

Atom çağrıları örnek yapılacaklar servisine gider; ağ kullanılmaz.

Çalıştırma:  python3 -m unittest discover -s tests -v   (proje kökünden)
"""
import unittest

import helpers
from core import caller, catalog, molecules, rows, runlog, runner, store, validation
from core.models import FieldSpec, InstalledElement


class StoreTest(unittest.TestCase):

    def setUp(self) -> None:
        helpers.reset()

    def test_put_get_delete(self) -> None:
        store.put("notes", "a", {"text": "merhaba"})
        self.assertEqual(store.get("notes", "a"), {"text": "merhaba"})
        store.put("notes", "a", {"text": "değişti"})
        self.assertEqual(store.all_of("notes"), [{"text": "değişti"}])
        store.delete("notes", "a")
        self.assertIsNone(store.get("notes", "a"))

    def test_next_key_counts_up(self) -> None:
        self.assertEqual(store.next_key("notes"), "1")
        store.put("notes", "1", {})
        store.put("notes", "2", {})
        self.assertEqual(store.next_key("notes"), "3")


class CatalogTest(unittest.TestCase):

    def setUp(self) -> None:
        self.installed = helpers.reset()

    def test_installed_element_is_listed(self) -> None:
        names = [installed.element.name for installed in catalog.installed_elements()]
        self.assertEqual(names, ["yapilacaklar"])

    def test_find_atom(self) -> None:
        installed, atom = catalog.find_atom("yapilacaklar", "todos_create")
        self.assertEqual(atom.title, "Görev oluştur")
        self.assertIsNone(catalog.find_atom("yapilacaklar", "yok"))
        self.assertIsNone(catalog.find_atom("yok", "todos_create"))

    def test_uninstall(self) -> None:
        catalog.uninstall("yapilacaklar")
        self.assertEqual(catalog.installed_elements(), [])


class CallerTest(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.installed = helpers.reset()

    async def call(self, atom_name: str, values: dict):
        return await caller.call_atom(self.installed, helpers.atom_of(self.installed, atom_name), values)

    async def test_create_then_list(self) -> None:
        created = await self.call("lists_create", {"name": "İş", "color": "yeşil"})
        self.assertTrue(created.ok)
        self.assertEqual(created.data["id"], 1)
        listed = await self.call("lists_list", {})
        self.assertEqual([row["name"] for row in listed.data], ["İş"])

    async def test_update_and_delete_use_id_in_path(self) -> None:
        await self.call("lists_create", {"name": "İş", "color": "mavi"})
        updated = await self.call("lists_update", {"id": 1, "name": "Ev", "color": "sarı"})
        self.assertEqual(updated.data["name"], "Ev")
        deleted = await self.call("lists_delete", {"id": 1})
        self.assertTrue(deleted.ok)
        self.assertEqual((await self.call("lists_list", {})).data, [])

    async def test_validation_error_becomes_field_errors(self) -> None:
        await self.call("lists_create", {"name": "İş", "color": "mavi"})
        answer = await self.call("todos_create", {"title": "Rapor", "code": "12", "list_id": 1,
                                                  "priority": 3, "done": False, "due": None})
        self.assertFalse(answer.ok)
        self.assertEqual(answer.status, 422)
        self.assertIn("code", answer.field_errors)

    async def test_business_error_keeps_service_sentence(self) -> None:
        await self.call("lists_create", {"name": "İş", "color": "mavi"})
        answer = await self.call("lists_create", {"name": "İş", "color": "mavi"})
        self.assertEqual(answer.status, 409)
        self.assertEqual(answer.message, "'İş' adında bir liste zaten var.")

    async def test_unreachable_service(self) -> None:
        saved = caller.TRANSPORT
        caller.TRANSPORT = None
        try:
            dead = InstalledElement(element=self.installed.element, base_url="http://127.0.0.1:9")
            answer = await caller.call_atom(dead, helpers.atom_of(dead, "lists_list"), {})
        finally:
            caller.TRANSPORT = saved
        self.assertFalse(answer.ok)
        self.assertIn("ulaşılamadı", answer.message)

    async def test_fetch_document(self) -> None:
        document = await caller.fetch_document(helpers.BASE_URL)
        self.assertEqual(document["info"]["title"], "Yapılacaklar")


class ValidationTest(unittest.TestCase):

    def field(self, **settings) -> FieldSpec:
        return FieldSpec(name="x", title="X", description="x", **settings)

    def test_required(self) -> None:
        self.assertEqual(validation.check_value(self.field(kind="text"), ""), "Bu alan zorunlu.")
        self.assertIsNone(validation.check_value(self.field(kind="text", required=False), ""))

    def test_eight_digit_pattern(self) -> None:
        code = self.field(kind="text", pattern=r"^\d{8}$")
        self.assertIsNone(validation.check_value(code, "12345678"))
        self.assertIsNotNone(validation.check_value(code, "1234567"))
        self.assertIsNotNone(validation.check_value(code, "123456789"))
        self.assertIsNotNone(validation.check_value(code, "1234567a"))

    def test_length(self) -> None:
        title = self.field(kind="text", min_length=3, max_length=5)
        self.assertIn("En az 3", validation.check_value(title, "ab"))
        self.assertIn("En çok 5", validation.check_value(title, "abcdef"))
        self.assertIsNone(validation.check_value(title, "abcd"))

    def test_integer_range(self) -> None:
        priority = self.field(kind="integer", minimum=1, maximum=5)
        self.assertIsNone(validation.check_value(priority, 3.0))
        self.assertIn("En az 1", validation.check_value(priority, 0))
        self.assertIn("En çok 5", validation.check_value(priority, 6))
        self.assertEqual(validation.check_value(priority, 2.5), "Tam sayı olmalı.")
        self.assertEqual(validation.check_value(priority, "abc"), "Sayı olmalı.")

    def test_choice(self) -> None:
        color = self.field(kind="choice", choices=["mavi", "sarı"])
        self.assertIsNone(validation.check_value(color, "mavi"))
        self.assertIsNotNone(validation.check_value(color, "mor"))

    def test_check_form_and_clean_values(self) -> None:
        fields = [FieldSpec(name="title", title="Başlık", description="-", kind="text", min_length=3),
                  FieldSpec(name="priority", title="Öncelik", description="-", kind="integer"),
                  FieldSpec(name="due", title="Tarih", description="-", kind="date", required=False)]
        self.assertEqual(list(validation.check_form(fields, {"title": "ab", "priority": 3})), ["title"])
        cleaned = validation.clean_values(fields, {"title": "abc", "priority": 3.0, "due": ""})
        self.assertEqual(cleaned, {"title": "abc", "priority": 3, "due": None})
        self.assertIsInstance(cleaned["priority"], int)


class RowsTest(unittest.TestCase):

    ROWS = [{"id": 1, "title": "Rapor yaz", "done": True, "owner": "Işıl"},
            {"id": 2, "title": "Rapor oku", "done": False, "owner": "İlker"},
            {"id": 3, "title": "Toplantı", "done": False, "owner": "Işıl"}]

    def ids(self, **filters) -> list[int]:
        return [row["id"] for row in rows.filter_rows(self.ROWS, filters)]

    def test_no_filter_returns_all(self) -> None:
        self.assertEqual(self.ids(), [1, 2, 3])

    def test_single_column(self) -> None:
        self.assertEqual(self.ids(title="rapor"), [1, 2])

    def test_two_columns_intersect(self) -> None:
        self.assertEqual(self.ids(title="rapor", owner="ışıl"), [1])

    def test_boolean_is_searched_as_shown(self) -> None:
        self.assertEqual(self.ids(done="hayır"), [2, 3])

    def test_turkish_letters(self) -> None:
        self.assertEqual(self.ids(owner="ilker"), [2])
        self.assertEqual(self.ids(owner="IŞIL"), [1, 3])

    def test_csv(self) -> None:
        columns = [FieldSpec(name="title", title="Başlık", description="-", kind="text"),
                   FieldSpec(name="done", title="Tamamlandı", description="-", kind="boolean")]
        text = rows.to_csv(columns, self.ROWS[:2])
        self.assertEqual(text.lstrip("﻿").splitlines(),
                         ["Başlık,Tamamlandı", "Rapor yaz,Evet", "Rapor oku,Hayır"])


class MoleculeTest(unittest.TestCase):

    def setUp(self) -> None:
        self.installed = helpers.reset()

    def generate(self, atom_name: str) -> molecules.Molecule:
        return molecules.generate(self.installed, helpers.atom_of(self.installed, atom_name))

    def test_list_atom_becomes_one_step(self) -> None:
        molecule = self.generate("todos_list")
        self.assertEqual([step.atom for step in molecule.steps], ["todos_list"])
        self.assertFalse(molecules.needs_selection(molecule, 0))

    def test_create_atom_asks_every_field(self) -> None:
        molecule = self.generate("todos_create")
        fields = molecule.steps[0].fields
        self.assertEqual(list(fields), ["title", "code", "list_id", "priority", "done", "due"])
        self.assertTrue(all(source.kind == "form" for source in fields.values()))
        self.assertEqual(fields["code"].label, "Kod")

    def test_update_atom_gets_a_select_step_first(self) -> None:
        molecule = self.generate("todos_update")
        self.assertEqual([step.atom for step in molecule.steps], ["todos_list", "todos_update"])
        fields = molecule.steps[1].fields
        self.assertEqual((fields["id"].kind, fields["id"].step, fields["id"].field), ("step", 0, "id"))
        self.assertEqual((fields["title"].kind, fields["title"].step, fields["title"].field),
                         ("form", 0, "title"))
        self.assertTrue(molecules.needs_selection(molecule, 0))

    def test_delete_atom_gets_a_select_step_first(self) -> None:
        molecule = self.generate("todos_delete")
        self.assertEqual([step.atom for step in molecule.steps], ["todos_list", "todos_delete"])
        self.assertEqual(list(molecule.steps[1].fields), ["id"])

    def test_save_find_remove(self) -> None:
        saved = molecules.save(self.generate("todos_list"))
        self.assertEqual(saved.id, "1")
        self.assertEqual(molecules.find("1").title, "Görevleri göster")
        self.assertEqual(len(molecules.all_molecules()), 1)
        molecules.remove("1")
        self.assertIsNone(molecules.find("1"))


class RunnerTest(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.installed = helpers.reset()

    def generate(self, atom_name: str) -> molecules.Molecule:
        return molecules.generate(self.installed, helpers.atom_of(self.installed, atom_name))

    async def add_list(self, name: str = "İş") -> dict:
        result = await runner.run_molecule(self.generate("lists_create"),
                                           [{"name": name, "color": "mavi"}], [None])
        return result.steps[0].data

    async def test_create(self) -> None:
        result = await runner.run_molecule(self.generate("lists_create"),
                                           [{"name": "İş", "color": "mavi"}], [None])
        self.assertTrue(result.ok)
        self.assertEqual(result.steps[0].status, "done")
        self.assertEqual(result.steps[0].data["id"], 1)

    async def test_select_then_update(self) -> None:
        row = await self.add_list()
        result = await runner.run_molecule(self.generate("lists_update"),
                                           [{}, {"name": "Ev", "color": "sarı"}], [row, None])
        self.assertEqual([step.status for step in result.steps], ["selected", "done"])
        self.assertEqual(result.steps[1].data, {"id": 1, "name": "Ev", "color": "sarı"})

    async def test_select_then_delete(self) -> None:
        row = await self.add_list()
        result = await runner.run_molecule(self.generate("lists_delete"), [{}, {}], [row, None])
        self.assertTrue(result.ok)
        self.assertEqual(helpers.todo_store.all_rows("lists"), [])

    async def test_missing_selection_fails_cleanly(self) -> None:
        result = await runner.run_molecule(self.generate("lists_delete"), [{}, {}], [None, None])
        self.assertFalse(result.ok)
        self.assertEqual(result.steps[1].status, "failed")
        self.assertIn("kayıt seçilmedi", result.steps[1].message)

    async def test_output_of_first_step_feeds_second(self) -> None:
        molecule = molecules.Molecule(title="Yeni proje", steps=[
            molecules.Step(element="yapilacaklar", atom="lists_create", title="Liste oluştur",
                           fields={"name": molecules.Source(kind="form", label="Ad"),
                                   "color": molecules.Source(kind="const", value="yeşil")}),
            molecules.Step(element="yapilacaklar", atom="todos_create", title="Görev oluştur",
                           fields={"title": molecules.Source(kind="const", value="Proje planını yaz"),
                                   "code": molecules.Source(kind="form", label="Kod"),
                                   "list_id": molecules.Source(kind="step", step=0, field="id"),
                                   "priority": molecules.Source(kind="const", value=5),
                                   "done": molecules.Source(kind="const", value=False),
                                   "due": molecules.Source(kind="const", value=None)}),
        ])
        result = await runner.run_molecule(molecule, [{"name": "Proje X"}, {"code": "11112222"}],
                                           [None, None])
        self.assertTrue(result.ok)
        todo = result.steps[1].data
        self.assertEqual((todo["list_id"], todo["title"], todo["priority"]), (1, "Proje planını yaz", 5))
        self.assertEqual(helpers.todo_store.all_rows("lists")[0]["color"], "yeşil")

    async def test_failure_stops_and_reports_each_step(self) -> None:
        await self.add_list("Proje X")
        molecule = molecules.Molecule(title="İki liste", steps=[
            molecules.Step(element="yapilacaklar", atom="lists_create", title="Birinci",
                           fields={"name": molecules.Source(kind="const", value="Yeni"),
                                   "color": molecules.Source(kind="const", value="mavi")}),
            molecules.Step(element="yapilacaklar", atom="lists_create", title="İkinci",
                           fields={"name": molecules.Source(kind="const", value="Proje X"),
                                   "color": molecules.Source(kind="const", value="mavi")}),
            molecules.Step(element="yapilacaklar", atom="lists_create", title="Üçüncü",
                           fields={"name": molecules.Source(kind="const", value="Başka"),
                                   "color": molecules.Source(kind="const", value="mavi")}),
        ])
        result = await runner.run_molecule(molecule, [{}, {}, {}], [None, None, None])
        self.assertFalse(result.ok)
        self.assertEqual([step.status for step in result.steps], ["done", "failed", "skipped"])
        self.assertEqual(result.steps[1].message, "'Proje X' adında bir liste zaten var.")
        # Geri alma yok: birinci adımın oluşturduğu liste yerinde durur.
        self.assertEqual([row["name"] for row in helpers.todo_store.all_rows("lists")], ["Proje X", "Yeni"])

    async def test_every_run_is_logged(self) -> None:
        await self.add_list()
        await runner.run_molecule(self.generate("lists_create"), [{"name": "İş", "color": "mavi"}], [None])
        log = runlog.recent()
        self.assertEqual(len(log), 2)
        self.assertFalse(log[0]["ok"])  # en yenisi başta: aynı adla ikinci liste
        self.assertTrue(log[1]["ok"])
        self.assertEqual(log[0]["molecule"], "Liste oluştur")

    async def test_unknown_atom(self) -> None:
        molecule = molecules.Molecule(title="Bozuk", steps=[
            molecules.Step(element="yapilacaklar", atom="yok_create", title="Yok")])
        result = await runner.run_molecule(molecule, [{}], [None])
        self.assertEqual(result.steps[0].status, "failed")


if __name__ == "__main__":
    unittest.main()
