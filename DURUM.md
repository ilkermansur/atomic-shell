# Proje durumu

Son güncelleme: 2026-11-11

Bu belge, çalışmaya ara verildiğinde nerede kalındığını anlatır. Yeni bir
oturuma başlarken önce bunu okumak yeterlidir; ayrıntılar `docs/` altındadır.

## Tek paragrafta proje

atomic-shell, içine API uçları alan bir kabuktur. Bir servisi FastAPI ile ve
`docs/07-fastapi-anayasasi.md` kurallarına göre yazarsın, OpenAPI belgesini
kabuğa içe aktarırsın. Kabuk her ucu bir **atom** yapar ve onun formunu ya da
tablosunu belgeden kendisi üretir. Atomlar **molekül**lere dönüştürülür;
çalıştırılabilir olan yalnızca moleküldür. Servisi sunan şey bir **element**tir
ve kendi container'ında çalışır. Kabuk hiçbir alanı (santral, CRM ...) tanımaz.

İş iki fazdır:

1. **Faz 1 (şu an):** kabuğu kaya gibi sağlam hale getirmek. Gerçek sistem yok;
   kabuk `examples/todo` adlı yapılacaklar servisiyle sınanıyor.
2. **Faz 2:** gerçek elementleri yazıp takmak. İlki Asterisk santral API'si
   (`atomic-pbx`, ayrı proje, yerelde `~/Desktop/atomic-pbx`, GitHub'da değil).

## Şu an çalışan

Uçtan uca akış tarayıcıda denendi:

1. Kabuk boş açılır.
2. "İçe aktar" ile örnek servisin OpenAPI belgesi alınır; 9 atom oluşur.
   Anayasaya uymayan uçlar kural numarasıyla raporlanır.
3. Periyodik tabloda bir atom seçilir. Liste atomu Excel tarzı tablo
   (başlık altında süzgeç, kolon seçici, CSV), diğerleri form olarak çizilir.
   Form kısıtları (8 hane, 1-5 aralığı, seçenekler) yazarken denetlenir.
4. "Molekül üret" atomdan molekül oluşturur. Güncelleme ve silme atomlarının
   önüne otomatik bir "tablodan seç" adımı konur (iki adımlı molekül).
5. Moleküller ekranından molekül sihirbazla çalıştırılır: adımlar, özet,
   uygulama, adım adım sonuç. Kayıt ekranı bütün çalıştırmaları gösterir.

Ayrıca: koyu/açık tema, TR/EN (kabuğun kendi metinleri), menüler arası geçiş
sayfa yenilemeden.

Sınamalar: `python3 -m unittest discover -s tests` → 92 sınama, hepsi geçiyor.

## Çalıştırma

Proje kökünden, iki ayrı terminalde:

```bash
python3 -m uvicorn main:app --app-dir examples/todo --port 8101
```

```bash
python3 -m uvicorn app:app --port 8100
```

Tarayıcıda `http://localhost:8100`. İçe aktarırken servis adresi
`http://localhost:8101`; istenirse `examples/todo/openapi.json` dosyası yüklenir.

Yerel veriler (git'e girmez): `shell.db` kabuğun kayıtları,
`examples/todo/data.json` örnek servisin verisi, `.nicegui/` kullanıcı
tercihleri. Sıfırdan başlamak için üçü de silinebilir.

## Kod haritası

Bağımlılık tek yönlüdür: `gui` → `api` → `core` → elementler (HTTP).
Arayüz çekirdeği doğrudan çağırmaz; yalnızca `gui/client.py` ile kabuğun
kendi API'sini kullanır.

| Klasör | İçerik |
|---|---|
| `core/` | `openapi_import` belge → atom, anayasa denetimi · `models` veri modelleri · `store` SQLite deposu · `catalog` takılı elementler · `caller` atomu HTTP ile çağırır · `validation` form denetimi · `rows` tablo yardımcıları, CSV · `molecules` molekül modeli, atomdan üretme · `runner` molekül çalıştırma · `runlog` kayıt |
| `api/` | `/api` altındaki uçlar: elementler, atomlar, moleküller, kayıt |
| `gui/` | `shell` tek sayfa ve yönlendirme · `layout` üst çubuk · `theme` renkler · `i18n` TR/EN · `forms` form üretici · `tables` tablo üretici (AG Grid) · `mimar` Elementler ekranı · `molekuller` Moleküller ve sihirbaz · `kayit` Kayıt ekranı |
| `examples/todo/` | Anayasaya göre yazılmış örnek servis (listeler, görevler) |
| `tests/` | İçe aktarıcı, çekirdek, API ve örnek servis sınamaları |
| `prototype/` | İlk tıklanabilir prototip; eski tasarım, atılabilir |
| `docs/` | Tasarım belgeleri 01-07 |

## Verilmiş kararlar

Yeniden tartışmaya gerek olmayanlar:

- Atom = anayasaya uyan bir FastAPI ucu. OpenAPI içe aktarılarak alınır.
  Postman sonraya.
- Uç türü arayüzü belirler: GET liste → tablo, POST → boş form,
  PUT → seçili kaydın dolu formu, DELETE → seçili kaydı silme.
- Çalıştırılabilir olan yalnızca moleküldür; tek atomluk iş de moleküldür.
- Molekül = sıra + alan başına değer kaynağı (formda sor, sabit değer, önceki
  adımın kaydı). Sihirbaz önce bütün girdileri toplar, sonda uygular.
- Varsayılan "var olanı seç ya da oluştur" adımı (tasarımda var, kodda yok).
- Geri alma yok. Yarıda kalan iş adım adım raporlanır, temizlik elle yapılır
  (CUCM'deki gibi).
- Üç rol: mimar (atom yazar, içe aktarır), tasarımcı (molekül kurar, admin
  yetkilerini verir), admin (yalnızca kendisine verilen molekülleri kullanır).
- Atom ve alan başlıkları tek dilli: servis hangi dilde yazdıysa o.
- Tablo AG Grid ile çiziliyor (NiceGUI içinde geliyor). Quasar tablosu,
  başlığı her güncellemede yeniden kurduğu için süzgeç kutusu odak kaybediyordu.
- Kod sade, sığ, tek iş yapan dosyalar; satır satır anlatılabilir olmalı.

## Bilinen pürüzler

- Desen hatası ham ifadeyi gösteriyor: "Beklenen: `^\d{8}$`".
- Sihirbaz özetinde bağlı alan adıyla değil numarasıyla görünüyor
  ("Liste: 1" yerine "Liste: Ev işleri" olmalı).
- AG Grid süzgeç menüsündeki seçenekler İngilizce ("Contains", "Equals").
- Sihirbazdaki satır seçme, tablo AG Grid'e geçtikten sonra tarayıcıda yeniden
  denenmedi.
- Dosya yükleyerek içe aktarma ve CSV indirme düğmesi tarayıcıda denenmedi
  (kodları sınamalarda geçiyor).
- Koyu temada form alanlarının kenarlığı soluk.
- Kullanıcının kendi gördüğü ve henüz not edilmemiş pürüzler: yarın konuşulacak.

## Sıradaki adımlar

Yol haritası `docs/06-yol-haritasi.md` içinde. Kalanlar, önerilen sırayla:

1. Yukarıdaki pürüzler ve kullanıcının notları.
2. Molekül tasarım ekranı: atomları elle birleştirme, alan kaynağı seçme,
   "seç ya da oluştur" adımı, ön denetim ("bu kayıt zaten var" uyarısı).
3. Kullanıcılar ve roller: giriş, mimar/tasarımcı/admin, admin başına molekül
   yetkisi, salt okunur admin.
4. Molekül dışa/içe aktarma, yeniden içe aktarmada fark raporu.
5. Anayasayı bir skill haline getirmek (servisleri yapay zekâyla aynı kalıpta
   yazmak için).

## Açık kararlar

- Lisans: depo herkese açık ama lisans dosyası yok; GPL/AGPL önerildi.
- `atomic-shell` adının marka araştırması yapılmadı.
- Kabuğun kendi API'si şu an kimlik doğrulamasız; roller adımında eklenecek.
