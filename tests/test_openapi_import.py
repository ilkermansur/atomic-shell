"""İçe aktarıcının sınamaları.

İlk bölüm örnek yapılacaklar servisinin belgesini içe aktarır ve atomların doğru
okunduğuna bakar. İkinci bölüm aynı belgeyi bilerek bozar ve her bozukluğun
doğru kural numarasıyla bildirildiğine bakar.

Çalıştırma:  python3 -m unittest discover -s tests -v   (proje kökünden)
"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "examples" / "todo"))

from core.openapi_import import import_document, short_name  # noqa: E402
from main import app  # noqa: E402  (örnek servis)

GOOD_DOCUMENT = app.openapi()


def broken_document() -> dict:
    """Üzerinde değişiklik yapılabilecek bir belge kopyası."""
    return copy.deepcopy(GOOD_DOCUMENT)


def rules(result) -> list[str]:
    """Bulunan sorunların kural numaraları."""
    return [problem.rule for problem in result.problems]


def atom_names(result) -> list[str]:
    return [atom.name for atom in result.element.atoms]


class GoodDocumentTest(unittest.TestCase):

    def setUp(self) -> None:
        self.result = import_document(GOOD_DOCUMENT)
        self.atoms = {atom.name: atom for atom in self.result.element.atoms}

    def test_no_problems(self) -> None:
        self.assertEqual(self.result.problems, [])

    def test_element_identity(self) -> None:
        element = self.result.element
        self.assertEqual(element.title, "Yapılacaklar")
        self.assertEqual(element.name, "yapilacaklar")
        self.assertEqual(element.symbol, "Ya")
        self.assertEqual(element.version, "0.1.0")

    def test_all_nine_operations_become_atoms(self) -> None:
        self.assertEqual(sorted(self.atoms), [
            "lists_create", "lists_delete", "lists_list", "lists_update",
            "todos_create", "todos_delete", "todos_get", "todos_list", "todos_update",
        ])

    def test_atom_details(self) -> None:
        atom = self.atoms["todos_update"]
        self.assertEqual((atom.resource, atom.action), ("todos", "update"))
        self.assertEqual((atom.method, atom.path), ("PUT", "/todos/{id}"))
        self.assertEqual(atom.title, "Görevi güncelle")
        self.assertEqual(atom.description, "Görevin alanlarını değiştirir.")

    def test_list_atom_has_columns_but_no_inputs(self) -> None:
        atom = self.atoms["todos_list"]
        self.assertEqual(atom.inputs, [])
        self.assertEqual([column.name for column in atom.columns],
                         ["title", "code", "list_id", "priority", "done", "due", "id"])

    def test_delete_atom_has_no_inputs(self) -> None:
        self.assertEqual(self.atoms["todos_delete"].inputs, [])

    def test_text_field_with_pattern(self) -> None:
        code = self.field("todos_create", "code")
        self.assertEqual(code.kind, "text")
        self.assertEqual(code.pattern, r"^\d{8}$")
        self.assertTrue(code.required)
        self.assertEqual(code.title, "Kod")

    def test_text_field_with_length(self) -> None:
        title = self.field("todos_create", "title")
        self.assertEqual((title.min_length, title.max_length), (3, 80))

    def test_integer_field_with_range_and_default(self) -> None:
        priority = self.field("todos_create", "priority")
        self.assertEqual(priority.kind, "integer")
        self.assertEqual((priority.minimum, priority.maximum), (1, 5))
        self.assertEqual(priority.default, 3)
        self.assertFalse(priority.required)

    def test_boolean_field(self) -> None:
        done = self.field("todos_create", "done")
        self.assertEqual(done.kind, "boolean")
        self.assertIs(done.default, False)

    def test_optional_date_field(self) -> None:
        due = self.field("todos_create", "due")
        self.assertEqual(due.kind, "date")
        self.assertFalse(due.required)

    def test_choice_field(self) -> None:
        color = self.field("lists_create", "color")
        self.assertEqual(color.kind, "choice")
        self.assertEqual(color.choices, ["mavi", "yeşil", "sarı", "kırmızı"])
        self.assertEqual(color.default, "mavi")

    def test_linked_field(self) -> None:
        list_id = self.field("todos_create", "list_id")
        self.assertEqual((list_id.ref, list_id.ref_label), ("lists_list", "name"))

    def field(self, atom_name: str, field_name: str):
        return next(field for field in self.atoms[atom_name].inputs if field.name == field_name)


class BrokenDocumentTest(unittest.TestCase):

    def test_missing_service_description(self) -> None:
        document = broken_document()
        del document["info"]["description"]
        self.assertEqual(rules(import_document(document)), ["1.1"])

    def test_missing_summary_drops_only_that_atom(self) -> None:
        document = broken_document()
        del document["paths"]["/todos"]["post"]["summary"]
        result = import_document(document)
        self.assertEqual(rules(result), ["3.3"])
        self.assertEqual(result.problems[0].where, "POST /todos")
        self.assertNotIn("todos_create", atom_names(result))
        self.assertIn("todos_list", atom_names(result))

    def test_missing_docstring(self) -> None:
        document = broken_document()
        del document["paths"]["/todos"]["get"]["description"]
        self.assertEqual(rules(import_document(document)), ["3.4"])

    def test_wrong_operation_id(self) -> None:
        document = broken_document()
        document["paths"]["/todos"]["post"]["operationId"] = "add_todo"
        result = import_document(document)
        self.assertEqual(rules(result), ["3.1"])
        self.assertIn("todos_create", result.problems[0].message)

    def test_wrong_tag(self) -> None:
        document = broken_document()
        document["paths"]["/todos"]["post"]["tags"] = ["görevler"]
        self.assertEqual(rules(import_document(document)), ["3.2"])

    def test_path_parameter_must_be_named_id(self) -> None:
        document = broken_document()
        document["paths"]["/todos/{todo_id}"] = document["paths"].pop("/todos/{id}")
        result = import_document(document)
        self.assertEqual(set(rules(result)), {"2.3"})
        self.assertEqual(len(result.problems), 3)  # get, put, delete

    def test_unsupported_method(self) -> None:
        document = broken_document()
        document["paths"]["/todos/{id}"]["patch"] = document["paths"]["/todos/{id}"]["put"]
        self.assertEqual(rules(import_document(document)), ["2"])

    def test_nested_path(self) -> None:
        document = broken_document()
        document["paths"]["/lists/{id}/todos"] = {"get": document["paths"]["/todos"]["get"]}
        self.assertEqual(rules(import_document(document)), ["2.3"])

    def test_missing_response_model(self) -> None:
        document = broken_document()
        document["paths"]["/todos"]["get"]["responses"]["200"]["content"]["application/json"]["schema"] = {}
        self.assertEqual(rules(import_document(document)), ["3.5"])

    def test_create_must_return_201(self) -> None:
        document = broken_document()
        responses = document["paths"]["/todos"]["post"]["responses"]
        responses["200"] = responses.pop("201")
        self.assertEqual(rules(import_document(document)), ["3.7"])

    def test_record_without_id(self) -> None:
        document = broken_document()
        del document["components"]["schemas"]["TodoList"]["properties"]["id"]
        result = import_document(document)
        self.assertIn("2.2", rules(result))
        self.assertNotIn("lists_list", atom_names(result))

    def test_field_without_title(self) -> None:
        document = broken_document()
        del document["components"]["schemas"]["TodoCreate"]["properties"]["code"]["title"]
        result = import_document(document)
        self.assertEqual(rules(result), ["4.1"])
        self.assertEqual(result.problems[0].where, "POST /todos › code")

    def test_nested_field_is_rejected(self) -> None:
        document = broken_document()
        document["components"]["schemas"]["TodoCreate"]["properties"]["tags"] = {
            "title": "Etiketler", "description": "Görevin etiketleri.",
            "type": "array", "items": {"type": "string"}}
        result = import_document(document)
        self.assertEqual(rules(result), ["4.2"])
        self.assertNotIn("todos_create", atom_names(result))

    def test_required_query_parameter(self) -> None:
        document = broken_document()
        document["paths"]["/todos"]["get"]["parameters"] = [
            {"name": "list_id", "in": "query", "required": True, "schema": {"type": "integer"}}]
        self.assertEqual(rules(import_document(document)), ["6"])

    def test_link_to_unknown_list(self) -> None:
        document = broken_document()
        for model in ("Todo", "TodoCreate", "TodoUpdate"):
            document["components"]["schemas"][model]["properties"]["list_id"]["x-ref"] = "groups_list"
        result = import_document(document)
        self.assertEqual(set(rules(result)), {"4"})
        self.assertEqual(sorted(atom_names(result)),
                         ["lists_create", "lists_delete", "lists_list", "lists_update"])

    def test_empty_document(self) -> None:
        result = import_document({})
        self.assertEqual(result.element.atoms, [])
        self.assertEqual(rules(result), ["1.1", "1.1", "1.1"])


class ShortNameTest(unittest.TestCase):

    def test_turkish_letters_and_spaces(self) -> None:
        self.assertEqual(short_name("Çağrı Kayıt Servisi"), "cagri_kayit_servisi")

    def test_empty_title(self) -> None:
        self.assertEqual(short_name(""), "element")


if __name__ == "__main__":
    unittest.main()
