# 3. Atom sözleşmesi

Kabuk ile element arasındaki tek bağ bu sözleşmedir. Sözleşmeye uyan her HTTP
servisi kabuğa takılabilir.

Atom, girdisi ve çıktısı standart bir API ucudur. Kimi zaman arkadaki sistemin
hazır bir ucunu sarar, kimi zaman sıfırdan yazılır; kabuk için fark yoktur.

## Elementin sunduğu uçlar

| Uç | İşi | Zorunlu |
|---|---|---|
| `GET /element` | Katalog: elementin kimliği ve atomlarının tanımları | Evet |
| `POST /atoms/{name}/apply` | Atomu çalıştırır, zarfı döndürür | Evet |
| `POST /atoms/{name}/plan` | Değiştirmeden ne yapacağını söyler | Hayır |
| `POST /atoms/{name}/undo` | Bir çalıştırmayı tersine çevirir | Hayır |
| `GET /health` | Element ayakta mı | Evet |

### Üç seviye

Element ne kadarını sunarsa kabuk o kadarını kullanır.

| Seviye | Sunulan | Kabukta kazanılan |
|---|---|---|
| 1 | Katalog ve uygula | Periyodik tablo, formlar, moleküller, yetki, kayıt |
| 2 | + planla | Uygulamadan önce "şunlar yapılacak" ekranı |
| 3 | + geri al | Geri al düğmesi ve molekülde zincirleme geri alma |

Seviye atom başına bildirilir; aynı elementte farklı seviyede atomlar olabilir.

## Katalog

`GET /element` şunu döndürür:

**Element kimliği**

| Alan | Açıklama |
|---|---|
| `name` | Atom adlarının ön eki. Örnek: `asterisk` |
| `symbol` | Periyodik tablo için iki harfli simge |
| `title`, `description` | Arayüzde görünen ad ve açıklama; dil başına verilebilir |
| `version` | Element sürümü |
| `contract` | Uyduğu sözleşme sürümü |

**Her atom için**

| Alan | Açıklama |
|---|---|
| `name` | `element.nesne.eylem`, küçük harf, İngilizce |
| `title`, `description` | Arayüzde ve AI araç tanımında kullanılır |
| `version` | Girdi ya da çıktı şemasını bozan değişiklikte artar |
| `input_schema` | Girdinin JSON Schema'sı |
| `output_schema` | Başarılı sonucun JSON Schema'sı |
| `writes` | Sistemde değişiklik yapar ya da bir etki doğurur |
| `has_plan` | Planlama ucunu sunar |
| `reversible` | Geri alma ucunu sunar |
| `idempotent` | Aynı girdiyle tekrar çalıştırmak güvenlidir |
| `timeout_ms` | Azami çalışma süresi. Varsayılan 5000 |

### Alan ipuçları

Girdi şemasındaki alanlar arayüzü yönlendiren ek bilgiler taşıyabilir:

| İpucu | Anlamı |
|---|---|
| Başlık ve yardım metni | Formda görünen etiket ve açıklama |
| Bağlantılı alan | Seçenekleri başka bir atomun çıktısından gelir. Örnek: kuyruk alanı `asterisk.queue.list` ile dolar |
| Gizli alan | Parola gibi değerler; arayüzde ve kayıtta maskelenir |
| Gelişmiş alan | Varsayılan olarak daraltılmış bölümde durur |

## İstek

Kabuk her istekte girdinin yanında bağlamı da gönderir:

```json
{
  "input": {"number": "1042", "display_name": "Ayşe Yılmaz"},
  "context": {"run_id": "…", "actor": "santral.admin", "molecule": "yeni_personel"}
}
```

Bağlam elemente bilgi içindir; yetki kararı kabukta verilir.

## Zarf

Her atom çağrısının cevabı aynı biçimdedir:

```json
{
  "ok": true,
  "data": {},
  "changes": [],
  "error": null
}
```

Hata durumunda `ok` yanlış, `data` boş olur ve `error` dolar:

```json
{"code": "already_exists", "message": "…", "retryable": false}
```

### Değişiklik kaydı

Yazan atom ne değiştirdiğini aynı biçimde bildirir:

```json
{"resource": "asterisk.extension", "id": "1042", "before": null, "after": {}}
```

- Oluşturmada `before` boş, silmede `after` boştur.
- Element çalıştırma geçmişi tutmaz. Geri alma istendiğinde kabuk kayıttaki
  değişiklik listesini elemente geri gönderir; element yalnızca onu kullanır.

### Hata kodları

| Kod | Anlamı | Yeniden denenebilir |
|---|---|---|
| `invalid_input` | Girdi şemaya uymuyor | Hayır |
| `not_found` | Hedef kaynak yok | Hayır |
| `already_exists` | Kaynak zaten var | Hayır |
| `forbidden` | Element işlemi reddetti | Hayır |
| `timeout` | Süre sınırı aşıldı | Evet |
| `upstream_error` | Elementin arkasındaki sistem hata verdi | Evet |
| `internal_error` | Atom kodunda beklenmeyen hata | Hayır |

Kabuk, elemente ulaşamadığında ya da cevap zarfa uymadığında kendisi
`upstream_error` üretir.

## Planlama

`POST /atoms/{name}/plan` hiçbir şeyi değiştirmez ve şunu döndürür:

- Yapılacak işin kısa özeti.
- Yapılacak değişikliklerin listesi.

Geri alınamayan atom bunu planında açıkça söyler; arayüz uyarı olarak gösterir.

## Kabuk ile element arasında güven

- Kabuk elemente her istekte bir erişim anahtarı gönderir. Anahtar, element
  takılırken belirlenir.
- Element yalnızca kabuktan gelen istekleri kabul edecek şekilde kurulur.
- Yetki ve kullanıcı yönetimi kabuktadır; element kullanıcı tanımaz.

## Kabuğun doğrulaması

Element takılırken ve katalog her okunduğunda kabuk şunları denetler:

- Atom adları elementin ön ekiyle başlıyor ve tekrar etmiyor.
- Her atomun girdi ve çıktı şeması var.
- `has_plan` ya da `reversible` bildirilen atomların ilgili uçları cevap veriyor.

Kurala uymayan atom kataloğa alınmaz; nedeni mimar ekranında gösterilir.

## Çalıştırma kaydı

Kayıt kabukta tutulur ve yalnızca eklenir.

| Alan | İçerik |
|---|---|
| Kimlik | Çalıştırma kimliği |
| Atom ve sürümü | Hangi atom |
| Aktör ve yol | Kim ve hangi yoldan: arayüz, API, AI, molekül |
| Girdi | Gizli alanlar maskelenmiş olarak |
| Zarf | Dönen cevap, değişikliklerle birlikte |
| Zaman | Başlangıç ve süre |
| Geri alma bağı | Bu kayıt bir geri alma ise hedef çalıştırma |

Geri alma kuralları:

- Yalnızca başarılı ve geri alınabilir bir çalıştırma geri alınır.
- Bir çalıştırma en çok bir kez geri alınır.
- Geri alma yeni bir kayıt üretir; eski kayıt değişmez.
- Geri alma başarısız olursa hata gösterilir ve kayda geçer.

## Element yazma yardımcısı

Python ve FastAPI ile element yazanlar için `kit/element.py` küçük bir yardımcı
sunar. Atom yazarı girdi ve çıktı modelini, uygulama işlevini ve isteğe bağlı
olarak plan ve geri alma işlevlerini yazar; yardımcı bunlardan sözleşme uçlarını
ve katalog kaydını üretir.

```python
class Input(BaseModel):
    number: str = Field(title="Extension number")
    display_name: str = Field(title="Display name")

class Output(BaseModel):
    extension: str

@element.atom(name="asterisk.extension.create", writes=True)
class CreateExtension:
    """Creates a new SIP extension."""

    async def plan(self, inp: Input) -> Plan: ...
    async def apply(self, inp: Input) -> Result[Output]: ...
    async def undo(self, changes: list[Change]) -> None: ...
```

`plan` ve `undo` yazılmazsa atom seviye 1 olarak yayınlanır. Yardımcı
zorunlu değildir; sözleşmeye uyan elle yazılmış uçlar da aynı şekilde çalışır.

## Sonraya bırakılan kapılar

- **OpenAPI içe aktarma:** sözleşmeyi bilmeyen hazır bir REST API'yi belge
  dosyasından okuyup seviye 1 atomlara çeviren bağdaştırıcı.
- **MCP köprüsü:** bir MCP sunucusunun araçlarını atom olarak almak ve kabuğun
  atomlarını MCP aracı olarak sunmak.
