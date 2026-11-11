"""Örnek element: yapılacaklar listesi.

Kabuğu sınamak için FastAPI anayasasına (docs/07-fastapi-anayasasi.md) göre
yazılmış küçük bir servistir. İki kaynak sunar: listeler ve görevler.

Çalıştırma:  uvicorn main:app --port 8101   (bu klasörün içinden)
Belge:       http://localhost:8101/openapi.json
"""
from fastapi import FastAPI, HTTPException

import store
from models import Todo, TodoCreate, TodoList, TodoUpdate, ListCreate, ListUpdate

app = FastAPI(
    title="Yapılacaklar",
    description="Listeler ve görevlerden oluşan örnek element.",
    version="0.1.0",
)


# ------------------------------------------------------------------- yardımcılar

def to_json(body) -> dict:
    """Modeli JSON dosyasına yazılabilir sözlüğe çevirir (tarihler metne döner)."""
    return body.model_dump(mode="json")


def check_list_name_is_free(name: str, ignore_id: int | None = None) -> None:
    """Aynı adda başka bir liste varsa 409 verir."""
    for row in store.all_rows("lists"):
        if row["name"] == name and row["id"] != ignore_id:
            raise HTTPException(status_code=409, detail=f"'{name}' adında bir liste zaten var.")


def check_todo_is_valid(body: TodoCreate, ignore_id: int | None = None) -> None:
    """Görevin listesi var mı ve kodu benzersiz mi diye bakar."""
    if store.find("lists", body.list_id) is None:
        raise HTTPException(status_code=404, detail=f"{body.list_id} numaralı liste bulunamadı.")
    for row in store.all_rows("todos"):
        if row["code"] == body.code and row["id"] != ignore_id:
            raise HTTPException(status_code=409, detail=f"{body.code} kodlu bir görev zaten var.")


# ----------------------------------------------------------------------- listeler

@app.get("/lists", operation_id="lists_list", tags=["lists"],
         summary="Listeleri göster", response_model=list[TodoList])
def list_lists() -> list[dict]:
    """Bütün listeleri döndürür."""
    return store.all_rows("lists")


@app.post("/lists", operation_id="lists_create", tags=["lists"],
          summary="Liste oluştur", response_model=TodoList, status_code=201)
def create_list(body: ListCreate) -> dict:
    """Yeni bir liste oluşturur. Liste adı benzersiz olmalıdır."""
    check_list_name_is_free(body.name)
    return store.insert("lists", to_json(body))


@app.put("/lists/{id}", operation_id="lists_update", tags=["lists"],
         summary="Listeyi güncelle", response_model=TodoList)
def update_list(id: int, body: ListUpdate) -> dict:
    """Listenin adını ve rengini değiştirir."""
    check_list_name_is_free(body.name, ignore_id=id)
    row = store.replace("lists", id, to_json(body))
    if row is None:
        raise HTTPException(status_code=404, detail=f"{id} numaralı liste bulunamadı.")
    return row


@app.delete("/lists/{id}", operation_id="lists_delete", tags=["lists"],
            summary="Listeyi sil", response_model=TodoList)
def delete_list(id: int) -> dict:
    """Listeyi siler. İçinde görev olan liste silinemez."""
    if any(todo["list_id"] == id for todo in store.all_rows("todos")):
        raise HTTPException(status_code=409, detail="Bu listede görev var; önce görevleri silin.")
    row = store.remove("lists", id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"{id} numaralı liste bulunamadı.")
    return row


# ------------------------------------------------------------------------ görevler

@app.get("/todos", operation_id="todos_list", tags=["todos"],
         summary="Görevleri göster", response_model=list[Todo])
def list_todos() -> list[dict]:
    """Bütün görevleri döndürür."""
    return store.all_rows("todos")


@app.get("/todos/{id}", operation_id="todos_get", tags=["todos"],
         summary="Görevi göster", response_model=Todo)
def get_todo(id: int) -> dict:
    """Tek bir görevi döndürür."""
    row = store.find("todos", id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"{id} numaralı görev bulunamadı.")
    return row


@app.post("/todos", operation_id="todos_create", tags=["todos"],
          summary="Görev oluştur", response_model=Todo, status_code=201)
def create_todo(body: TodoCreate) -> dict:
    """Yeni bir görev oluşturur. Kod benzersiz olmalı, liste var olmalıdır."""
    check_todo_is_valid(body)
    return store.insert("todos", to_json(body))


@app.put("/todos/{id}", operation_id="todos_update", tags=["todos"],
         summary="Görevi güncelle", response_model=Todo)
def update_todo(id: int, body: TodoUpdate) -> dict:
    """Görevin alanlarını değiştirir."""
    check_todo_is_valid(body, ignore_id=id)
    row = store.replace("todos", id, to_json(body))
    if row is None:
        raise HTTPException(status_code=404, detail=f"{id} numaralı görev bulunamadı.")
    return row


@app.delete("/todos/{id}", operation_id="todos_delete", tags=["todos"],
            summary="Görevi sil", response_model=Todo)
def delete_todo(id: int) -> dict:
    """Görevi siler."""
    row = store.remove("todos", id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"{id} numaralı görev bulunamadı.")
    return row
