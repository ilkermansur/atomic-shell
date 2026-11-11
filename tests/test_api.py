"""Kabuğun API'sinin sınamaları: içe aktarmadan veri değiştirmeye uçtan uca akış.

Çalıştırma:  python3 -m unittest discover -s tests -v   (proje kökünden)
"""
import copy
import unittest

import helpers
from fastapi import FastAPI
from fastapi.testclient import TestClient

import api

app = FastAPI()
app.include_router(api.router)
client = TestClient(app)

TODO = {"title": "Rapor yaz", "code": "12345678", "list_id": 1, "priority": 3,
        "done": False, "due": None}


class ApiTest(unittest.TestCase):

    def setUp(self) -> None:
        helpers.reset()
        client.delete("/api/elements/yapilacaklar")  # sınama boş kabukla başlar

    def import_todo(self):
        return client.post("/api/elements/import", json={"base_url": helpers.BASE_URL})

    def call(self, atom: str, values: dict):
        return client.post(f"/api/atoms/yapilacaklar/{atom}/call", json={"values": values}).json()

    def generate(self, atom: str) -> dict:
        return client.post("/api/molecules/generate",
                           json={"element": "yapilacaklar", "atom": atom}).json()

    def test_shell_starts_empty(self) -> None:
        self.assertEqual(client.get("/api/elements").json(), [])
        self.assertEqual(client.get("/api/molecules").json(), [])

    def test_import_from_service_address(self) -> None:
        answer = self.import_todo().json()
        self.assertEqual(answer["problems"], [])
        self.assertEqual(len(answer["element"]["atoms"]), 9)
        self.assertEqual(client.get("/api/elements").json()[0]["element"]["symbol"], "Ya")

    def test_import_from_uploaded_document(self) -> None:
        document = helpers.todo_app.openapi()
        answer = client.post("/api/elements/import",
                             json={"base_url": helpers.BASE_URL, "document": document})
        self.assertEqual(len(answer.json()["element"]["atoms"]), 9)

    def test_import_reports_problems_and_keeps_good_atoms(self) -> None:
        # FastAPI belgeyi önbellekte tutar; asıl belge bozulmasın diye kopyası değiştirilir.
        document = copy.deepcopy(helpers.todo_app.openapi())
        del document["paths"]["/todos"]["post"]["summary"]
        answer = client.post("/api/elements/import",
                             json={"base_url": helpers.BASE_URL, "document": document}).json()
        self.assertEqual([problem["rule"] for problem in answer["problems"]], ["3.3"])
        self.assertEqual(len(answer["element"]["atoms"]), 8)

    def test_remove_element(self) -> None:
        self.import_todo()
        client.delete("/api/elements/yapilacaklar")
        self.assertEqual(client.get("/api/elements").json(), [])

    def test_call_atom(self) -> None:
        self.import_todo()
        self.assertTrue(self.call("lists_create", {"name": "İş", "color": "mavi"})["ok"])
        self.assertEqual(len(self.call("lists_list", {})["data"]), 1)
        self.assertEqual(client.post("/api/atoms/yapilacaklar/yok/call", json={}).status_code, 404)

    def test_full_flow_with_generated_molecules(self) -> None:
        """İçe aktar, molekül üret, veri gir, değiştir, sil."""
        self.import_todo()
        create_list = self.generate("lists_create")
        create_todo = self.generate("todos_create")
        update_todo = self.generate("todos_update")
        delete_todo = self.generate("todos_delete")
        self.assertEqual(len(client.get("/api/molecules").json()), 4)

        def run(molecule: dict, inputs: list, selections: list) -> dict:
            return client.post(f"/api/molecules/{molecule['id']}/run",
                               json={"inputs": inputs, "selections": selections}).json()

        self.assertTrue(run(create_list, [{"name": "İş", "color": "mavi"}], [None])["ok"])
        self.assertTrue(run(create_todo, [TODO], [None])["ok"])

        row = self.call("todos_list", {})["data"][0]
        changed = run(update_todo, [{}, {**TODO, "title": "Raporu bitir", "done": True}], [row, None])
        self.assertTrue(changed["ok"])
        self.assertEqual(self.call("todos_list", {})["data"][0]["title"], "Raporu bitir")

        row = self.call("todos_list", {})["data"][0]
        self.assertTrue(run(delete_todo, [{}, {}], [row, None])["ok"])
        self.assertEqual(self.call("todos_list", {})["data"], [])

        self.assertEqual(len(client.get("/api/runs").json()), 4)

    def test_run_reports_failure(self) -> None:
        self.import_todo()
        molecule = self.generate("lists_create")
        body = {"inputs": [{"name": "İş", "color": "mavi"}], "selections": [None]}
        client.post(f"/api/molecules/{molecule['id']}/run", json=body)
        again = client.post(f"/api/molecules/{molecule['id']}/run", json=body).json()
        self.assertFalse(again["ok"])
        self.assertEqual(again["steps"][0]["message"], "'İş' adında bir liste zaten var.")

    def test_run_needs_one_entry_per_step(self) -> None:
        self.import_todo()
        molecule = self.generate("lists_update")
        answer = client.post(f"/api/molecules/{molecule['id']}/run",
                             json={"inputs": [{}], "selections": [None]})
        self.assertEqual(answer.status_code, 422)

    def test_delete_molecule(self) -> None:
        self.import_todo()
        molecule = self.generate("lists_list")
        client.delete(f"/api/molecules/{molecule['id']}")
        self.assertEqual(client.get("/api/molecules").json(), [])


if __name__ == "__main__":
    unittest.main()
