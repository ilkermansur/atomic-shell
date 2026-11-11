"""Örnek yapılacaklar servisinin sınamaları.

Servis gerçek bir sunucu açılmadan, FastAPI'nin sınama istemcisiyle çağrılır.
Her sınama boş bir geçici JSON dosyasıyla başlar.

Çalıştırma:  python3 -m unittest discover -s tests -v   (proje kökünden)
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

ELEMENT_DIR = Path(__file__).parent.parent / "examples" / "todo"
sys.path.insert(0, str(ELEMENT_DIR))

# Depo modülü yüklenmeden önce veri dosyasının yeri geçici bir dosyaya çevrilir.
os.environ["TODO_DATA_FILE"] = str(Path(tempfile.mkdtemp()) / "data.json")

from fastapi.testclient import TestClient  # noqa: E402

import store  # noqa: E402
from main import app  # noqa: E402

client = TestClient(app)

GOOD_TODO = {"title": "Rapor yaz", "code": "12345678", "list_id": 1}


class TodoElementTest(unittest.TestCase):

    def setUp(self) -> None:
        """Her sınamadan önce depoyu boşaltır ve tek bir liste ekler."""
        store.save({"lists": [], "todos": []})
        client.post("/lists", json={"name": "İş"})

    # ------------------------------------------------------------- temel işlemler

    def test_create_and_list(self) -> None:
        created = client.post("/todos", json=GOOD_TODO)
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json()["id"], 1)
        self.assertEqual(created.json()["priority"], 3)  # varsayılan değer
        self.assertEqual(len(client.get("/todos").json()), 1)

    def test_update(self) -> None:
        client.post("/todos", json=GOOD_TODO)
        changed = client.put("/todos/1", json={**GOOD_TODO, "title": "Raporu bitir", "done": True})
        self.assertEqual(changed.status_code, 200)
        self.assertEqual(client.get("/todos/1").json()["title"], "Raporu bitir")
        self.assertTrue(client.get("/todos/1").json()["done"])

    def test_delete_returns_deleted_row(self) -> None:
        client.post("/todos", json=GOOD_TODO)
        deleted = client.delete("/todos/1")
        self.assertEqual(deleted.status_code, 200)
        self.assertEqual(deleted.json()["code"], "12345678")
        self.assertEqual(client.get("/todos").json(), [])

    def test_data_survives_in_file(self) -> None:
        client.post("/todos", json=GOOD_TODO)
        self.assertEqual(store.load()["todos"][0]["title"], "Rapor yaz")

    # ------------------------------------------------------------- girdi denetimi

    def test_code_must_be_eight_digits(self) -> None:
        for bad_code in ["1234567", "123456789", "1234567a"]:
            answer = client.post("/todos", json={**GOOD_TODO, "code": bad_code})
            self.assertEqual(answer.status_code, 422, bad_code)

    def test_priority_range(self) -> None:
        self.assertEqual(client.post("/todos", json={**GOOD_TODO, "priority": 6}).status_code, 422)
        self.assertEqual(client.post("/todos", json={**GOOD_TODO, "priority": 0}).status_code, 422)

    def test_color_must_be_a_known_choice(self) -> None:
        self.assertEqual(client.post("/lists", json={"name": "Ev", "color": "mor"}).status_code, 422)

    # --------------------------------------------------------------- iş kuralları

    def test_duplicate_code_is_conflict(self) -> None:
        client.post("/todos", json=GOOD_TODO)
        again = client.post("/todos", json=GOOD_TODO)
        self.assertEqual(again.status_code, 409)
        self.assertIn("zaten var", again.json()["detail"])

    def test_unknown_list_is_not_found(self) -> None:
        answer = client.post("/todos", json={**GOOD_TODO, "list_id": 99})
        self.assertEqual(answer.status_code, 404)

    def test_duplicate_list_name_is_conflict(self) -> None:
        self.assertEqual(client.post("/lists", json={"name": "İş"}).status_code, 409)

    def test_list_with_todos_cannot_be_deleted(self) -> None:
        client.post("/todos", json=GOOD_TODO)
        self.assertEqual(client.delete("/lists/1").status_code, 409)

    def test_missing_rows_are_not_found(self) -> None:
        self.assertEqual(client.get("/todos/7").status_code, 404)
        self.assertEqual(client.put("/todos/7", json=GOOD_TODO).status_code, 404)
        self.assertEqual(client.delete("/todos/7").status_code, 404)

    # ------------------------------------------------------- anayasaya uygunluk

    def test_every_operation_follows_the_constitution(self) -> None:
        document = client.get("/openapi.json").json()
        self.assertTrue(document["info"]["title"])
        self.assertTrue(document["info"]["description"])
        for path, operations in document["paths"].items():
            for method, operation in operations.items():
                where = f"{method.upper()} {path}"
                resource = path.strip("/").split("/")[0]
                self.assertTrue(operation["operationId"].startswith(resource + "_"), where)
                self.assertEqual(operation["tags"], [resource], where)
                self.assertTrue(operation.get("summary"), where)
                self.assertTrue(operation.get("description"), where)

    def test_every_field_has_title_and_description(self) -> None:
        schemas = client.get("/openapi.json").json()["components"]["schemas"]
        for name in ["Todo", "TodoCreate", "TodoUpdate", "TodoList", "ListCreate", "ListUpdate"]:
            for field, spec in schemas[name]["properties"].items():
                self.assertTrue(spec.get("title"), f"{name}.{field}")
                self.assertTrue(spec.get("description"), f"{name}.{field}")

    def test_linked_field_is_declared(self) -> None:
        schemas = client.get("/openapi.json").json()["components"]["schemas"]
        self.assertEqual(schemas["TodoCreate"]["properties"]["list_id"]["x-ref"], "lists_list")


if __name__ == "__main__":
    unittest.main()
