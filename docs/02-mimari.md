# 2. Mimari

## Genel resim

```
   Tarayıcı                         Betik / AI
       \                               /
        ────  atomic-shell (kabuk)  ───          kendi container'ı
        arayüz · katalog · molekül çalıştırıcı
        kayıt · yetki
              |  HTTP: elementin kendi API uçları
     ┌────────┼──────────────┐
     ▼        ▼              ▼
 Element A  Element B     Element C              her biri kendi container'ı
```

- **Kabuk her zaman ayrı bir container'dır** ve hiçbir alanı tanımaz.
- **Her element ayrı bir servistir** ve kendi atomlarını kendi API'siyle sunar.
- Kabuk elementin uçlarını OpenAPI belgesinden öğrenir ve onları doğrudan
  çağırır. Elementin kabuk için özel bir uç sunması gerekmez; yeter ki uçları
  FastAPI anayasasına (`07-fastapi-anayasasi.md`) göre yazılmış olsun.

## Kabuk kapalıyken

Kabuk yönetim tarafıdır. Kapalıyken elementler ve arkalarındaki sistemler
çalışmaya devam eder; yalnızca arayüzden değişiklik yapılamaz.

## Katmanlar

Kabuk tek bir FastAPI uygulamasıdır; arayüz onun üstüne giydirilir.

| Katman | İşi | Neyi tanır |
|---|---|---|
| `core` | Modeller, içe aktarma, katalog, element çağırma, molekül çalıştırma, kayıt, yetki | FastAPI'yi ve NiceGUI'yi tanımaz |
| `api` | Kabuğun kendi ince FastAPI uçları | Yalnızca `core`'u |
| `gui` | NiceGUI ekranları | Yalnızca kabuğun API'sini, `gui/client.py` üzerinden |

Bağımlılık tek yönlüdür: `gui` → `api` → `core` → elementler (HTTP).

Arayüz aynı uygulamanın içinde çalışsa da çekirdeği doğrudan çağırmaz. Bu
sayede arayüzde yapılabilen her şey API'de de vardır ve arayüz değiştirilebilir.

## Klasör yapısı

```
core/
  models.py          element, atom, alan ve sorun modelleri
  openapi_import.py  OpenAPI belgesini okur, anayasaya göre denetler, atomlara çevirir
  store.py           kabuğun kendi veritabanı
  catalog.py         içe aktarılmış elementler ve atomları
  caller.py          bir atomu çağırır: HTTP isteği, hata çevirisi
  molecules.py       molekül modeli ve doğrulaması
  runner.py          molekül yürütme: okuyan adımlar, ön denetim, yazan adımlar
  runlog.py          çalıştırma kaydı
  auth.py            kullanıcı, rol, molekül yetkisi
api/
  elements.py        içe aktarma, listeleme, çıkarma
  atoms.py           katalog, atomu doğrudan çalıştırma (mimar ve tasarımcı için)
  molecules.py       kaydetme, yayınlama, çalıştırma
  runs.py            kayıt
  users.py           kullanıcılar ve yetkiler
gui/
  client.py          arayüzün API'ye konuştuğu tek yer
  theme.py           renkler, koyu/açık tema
  i18n.py            TR/EN sözlüğü
  forms.py           alan listesinden form üretir
  tables.py          kayıt listesinden aranabilir tablo üretir
  mimar.py           periyodik tablo ve atom ekranı
  tasarimci.py       molekül tasarım ekranı
  admin.py           sihirbaz ve kayıt ekranı
examples/
  todo/              anayasaya göre yazılmış örnek element
tests/
main.py              FastAPI uygulamasını kurar, API'yi ve arayüzü bağlar
```

## Kabuğun kendi kayıtları

Kabuk şunları kendi küçük veritabanında tutar: içe aktarılmış elementler ve
atomları, moleküller ve sürümleri, çalıştırma kaydı, kullanıcılar ve yetkileri.

- Varsayılan SQLite'tır; kurulum gerektirmez.
- Bu veritabanı elementlerin arkasındaki sistemlerin verisinden ayrıdır.

## Roller ve yetki

Yetki kabukta denetlenir, elementte değil.

| Rol | Yapabildiği | Yetkisi |
|---|---|---|
| Mimar | Element içe aktarır, atomları inceler ve dener; alttaki rollerin her işini yapar | Standart: her şeye erişir |
| Tasarımcı | Molekül kurar, dener, yayınlar; admin kullanıcılarını ve yetkilerini yönetir | Standart: bütün atom ve moleküllere erişir |
| Admin | Yalnızca kendisine verilen molekülleri çalıştırır | Kişiye özel |

- Admin kullanıcısı oluşturulurken hangi molekülleri kullanabileceği tek tek
  seçilir.
- Yalnızca okuyan moleküller verilmiş bir admin salt okunur bir kullanıcıdır.
- Admin atomları doğrudan göremez ve çalıştıramaz.

## Teknoloji kararları

| Karar | Seçim | Gerekçe |
|---|---|---|
| Dil | Python | Geliştiricinin dili; tek dil hedefi |
| API | FastAPI + Pydantic | Şemadan üretim, tip denetimi |
| Arayüz | NiceGUI | Python içinde; FastAPI uygulamasına doğrudan bağlanır |
| Tuval | Drawflow | Prototipte NiceGUI'ye sorunsuz oturdu; yalnızca çizim için |
| Molekül çalıştırıcı | Kendi kodumuz | İşi dar; hazır akış motoru ikinci bir dil ve bağımlılık getirir |
| Kabuğun veritabanı | SQLite | Sıfır kurulum |
| Kod adları | İngilizce | Açık kaynak; arayüz metinleri TR/EN |

## Kod kuralları

Kod, sonradan satır satır okunup anlatılabilecek sadelikte yazılır.

- Her dosya tek iş yapar ve başında ne yaptığını söyleyen kısa bir açıklama
  taşır.
- Klasör derinliği en çok iki seviyedir.
- İşlevler kısadır ve tek iş yapar; iç içe işlev tanımından kaçınılır.
- Kalıtım zinciri, üst sınıf sihri ve gizli davranış yoktur.
- Her işlevde tip bilgisi bulunur.
- Yorumlar neyi değil, nedenini anlatır.
- Yeni bağımlılık ancak gerçekten gerekiyorsa eklenir.
- Her parça sınamasıyla birlikte yazılır.
