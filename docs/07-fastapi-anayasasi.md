# 7. FastAPI anayasası

Kabuk, bir servisin OpenAPI belgesini içe aktararak her ucu bir atoma çevirir.
Arayüzün sorunsuz oluşması için uçların bu kurallara göre yazılması gerekir.

Kabuk içe aktarırken belgeyi bu kurallara göre denetler ve her eksikliği uç ve
alan adıyla bildirir. Kurala uymayan uç atom olarak alınmaz.

Çalışan bir örnek: `examples/todo/`.

## 1. Servis

| Kural | Açıklama |
|---|---|
| 1.1 | `FastAPI(title=..., description=..., version=...)` üçü de doludur. `title` elementin adı olur. |
| 1.2 | Servis OpenAPI belgesini `/openapi.json` adresinde sunar (FastAPI'nin varsayılanı). |

## 2. Kaynak düzeni

Uçlar kaynaklar etrafında toplanır. Kaynak, çoğul bir adla anılan kayıt
türüdür: `todos`, `lists`, `extensions`.

| Kural | Açıklama |
|---|---|
| 2.1 | Bir kaynağın bütün uçları aynı yol kökünü paylaşır: `/todos`. |
| 2.2 | Her kaydın `id` adında bir kimlik alanı vardır. |
| 2.3 | Tek kayda dokunan uçların yolu `/{kaynak}/{id}` biçimindedir; yol parametresinin adı `id`'dir. |

Bir kaynak için izin verilen uçlar:

| Uç | Eylem | Kabukta |
|---|---|---|
| `GET /{kaynak}` | `list` | Aranabilir tablo, CSV dışa aktarma |
| `POST /{kaynak}` | `create` | Boş girdi formu |
| `PUT /{kaynak}/{id}` | `update` | Seçili kaydın dolu formu |
| `DELETE /{kaynak}/{id}` | `delete` | Seçili kaydı silme, onayla |
| `GET /{kaynak}/{id}` | `get` | Tek kaydın ayrıntısı (isteğe bağlı) |

Bir kaynak bunların hepsini sunmak zorunda değildir. Yalnızca `GET` sunan bir
kaynak salt okunur olur.

## 3. Her uç

| Kural | Açıklama |
|---|---|
| 3.1 | `operation_id` zorunludur ve `{kaynak}_{eylem}` biçimindedir: `todos_list`, `todos_create`. Atomun adı buradan gelir. |
| 3.2 | `tags` tam olarak bir etiket taşır: kaynağın adı. |
| 3.3 | `summary` zorunludur: atomun kısa başlığı. |
| 3.4 | Docstring zorunludur: atomun açıklaması. |
| 3.5 | `response_model` zorunludur. `list` ucu kayıt modelinin düz listesini, `create`, `update` ve `get` uçları kayıt modelini döndürür. |
| 3.6 | `delete` ucu silinen kaydı döndürür. |
| 3.7 | `create` ucu `201`, diğerleri `200` döndürür. |

## 4. Modeller

Her kaynak için en çok üç model yazılır:

| Model | Kullanıldığı yer |
|---|---|
| Kayıt modeli (`Todo`) | Cevaplar; tablonun kolonları buradan gelir |
| Oluşturma modeli (`TodoCreate`) | `create` ucunun girdisi |
| Güncelleme modeli (`TodoUpdate`) | `update` ucunun girdisi |

| Kural | Açıklama |
|---|---|
| 4.1 | Her alanda `title` (etiket) ve `description` (yardım metni) zorunludur. |
| 4.2 | Girdi modelleri düzdür: iç içe model ya da liste alanı içermez. |
| 4.3 | Kısıtlar modelde tanımlanır; kabuk formu bunlara göre denetler. |
| 4.4 | Kayıt modeli de düzdür; her alan tablonun bir kolonudur. |

### Desteklenen alan türleri

| Python türü | Formda | Kullanılan kısıtlar |
|---|---|---|
| `str` | Metin kutusu | `min_length`, `max_length`, `pattern` |
| `int`, `float` | Sayı kutusu | `ge`, `le`, `gt`, `lt` |
| `bool` | Evet / hayır | |
| `Literal[...]` ya da `Enum` | Seçenek sayısı azsa radyo düğmesi, çoksa açılır liste | |
| `date`, `datetime` | Tarih seçici | |
| `X | None` | İsteğe bağlı alan | |

Varsayılan değeri olan alan formda o değerle dolu gelir.

### Bağlantılı alan

Değeri başka bir kaynağın kaydına işaret eden alan bunu bildirir; kabuk metin
kutusu yerine o kaynağın listesinden beslenen bir seçim listesi çizer.

```python
list_id: int = Field(
    title="Liste",
    description="Görevin ait olduğu liste.",
    json_schema_extra={"x-ref": "lists_list", "x-ref-label": "name"},
)
```

- `x-ref`: seçeneklerin geleceği `list` ucunun `operation_id`'si.
- `x-ref-label`: seçenek olarak gösterilecek alan. Değer olarak `id` gönderilir.

## 5. Hatalar

| Kural | Açıklama |
|---|---|
| 5.1 | Girdi hataları FastAPI'nin varsayılan `422` cevabıyla döner; kabuk hatayı ilgili alanın altında gösterir. |
| 5.2 | İş kuralı hataları `HTTPException` ile döner; `detail` kullanıcıya gösterilecek düz bir cümledir. |
| 5.3 | Kayıt yoksa `404`, kayıt zaten varsa ya da çakışma olursa `409` kullanılır. |

## 6. İlk sürümün sınırları

Bunlar şimdilik desteklenmez; içe aktarma denetimi bildirir.

- `list` ucunda zorunlu sorgu parametresi. Kabuk listenin tamamını alır ve
  aramayı kendisi yapar.
- Sayfalama.
- `PATCH` uçları ve kaynak düzenine uymayan özel uçlar.
- İç içe modeller, liste alanları, dosya yükleme.
- Uç başına farklı kimlik doğrulama. Servis ya açıktır ya da tek bir erişim
  anahtarı başlığı ister; anahtar element içe aktarılırken verilir.

## Örnek

```python
class TodoCreate(BaseModel):
    title: str = Field(title="Başlık", description="Görevin kısa adı.",
                       min_length=3, max_length=80)
    code: str = Field(title="Kod", description="Sekiz haneli iş kodu.",
                      pattern=r"^\d{8}$")
    priority: int = Field(default=3, title="Öncelik",
                          description="1 en düşük, 5 en yüksek.", ge=1, le=5)
    done: bool = Field(default=False, title="Tamamlandı",
                       description="Görev bitti mi.")


@app.post("/todos", operation_id="todos_create", tags=["todos"],
          summary="Görev oluştur", response_model=Todo, status_code=201)
def create_todo(body: TodoCreate) -> Todo:
    """Yeni bir görev oluşturur."""
    ...
```
