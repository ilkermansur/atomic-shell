# 2. Mimari

## Genel resim

```
   Tarayıcı        AI / MCP        Betik
       \              |             /
        ────  atomic-shell (kabuk)  ────        kendi container'ı
        arayüz · katalog · molekül çalıştırıcı
        kayıt · geri alma · yetki
              |  HTTP: atom sözleşmesi
     ┌────────┼──────────────┐
     ▼        ▼              ▼
 Element A  Element B     Element C             her biri kendi container'ı
 (santral)   (CRM)        (e-posta)
     |
 arkadaki sistemler (Asterisk, veritabanı …)
```

- **Kabuk her zaman ayrı bir container'dır** ve hiçbir alanı tanımaz.
- **Her element ayrı bir servistir** ve kendi atomlarını kendi API'siyle sunar.
- Kabuk ile element arasındaki tek bağ HTTP üzerinden atom sözleşmesidir
  (`03-atom-sozlesmesi.md`).

## Element takmak ve çıkarmak

- **Takmak:** kabuğa elementin adresi ve erişim anahtarı verilir. Kabuk
  elementin kataloğunu okur; atomları periyodik tabloda belirir.
- **Çıkarmak:** adres silinir. O elementin atomlarını kullanan moleküller
  "eksik element" olarak işaretlenir; silinmez.
- **Güncellemek:** element yeni sürümüyle yeniden başlar; kabuk kataloğu
  yeniden okur ve sürüm farklarını bildirir.

Element herhangi bir dille yazılabilir; sözleşmeye uyan her HTTP servisi takılır.
Python ve FastAPI ile yazanlar için küçük bir yardımcı modül sunulur.

## Kabuk kapalıyken

Kabuk yönetim tarafıdır. Kapalıyken elementler ve arkalarındaki sistemler
çalışmaya devam eder; yalnızca arayüzden değişiklik yapılamaz.

## Kabuğun katmanları

Kabuk tek bir FastAPI uygulamasıdır; arayüz onun üstüne giydirilir.

| Katman | İşi | Neyi tanır |
|---|---|---|
| `core` | Sözleşme modelleri, element istemcisi, katalog, molekül çalıştırıcı, kayıt, yetki | FastAPI'yi ve NiceGUI'yi tanımaz |
| `api` | Kabuğun kendi ince FastAPI uçları | Yalnızca `core`'u |
| `gui` | NiceGUI ekranları | Yalnızca kabuğun API'sini, `gui/client.py` üzerinden |

Bağımlılık tek yönlüdür: `gui` → `api` → `core` → elementler (HTTP).

Arayüz aynı uygulamanın içinde çalışsa da çekirdeği doğrudan çağırmaz. Bu
sayede arayüzde yapılabilen her şey API'de de vardır ve arayüz değiştirilebilir.

## Klasör yapısı

```
core/
  contract.py    sözleşme modelleri: katalog, atom, zarf, hata kodları
  elements.py    takılı elementler, HTTP istemcisi
  catalog.py     periyodik tablo: elementlerden okunan atomlar
  runner.py      atom ve molekül yürütme, zincirleme geri alma
  molecules.py   molekül modeli, doğrulama, sürümleme, dışa/içe aktarma
  runlog.py      çalıştırma kaydı
  auth.py        kullanıcı, profil, grup, yetki
  store.py       kabuğun kendi veritabanı
api/
  elements.py    element takma, çıkarma, katalog
  atoms.py       atom planlama, uygulama
  molecules.py   molekül kaydetme, yayınlama, çalıştırma
  runs.py        kayıt ve geri alma
gui/
  client.py      arayüzün API'ye konuştuğu tek yer
  theme.py       renkler, koyu/açık tema
  i18n.py        TR/EN sözlüğü
  mimar.py       periyodik tablo ekranı
  tasarimci.py   molekül tasarım ekranı
  admin.py       admin ekranı
kit/
  element.py     FastAPI ile element yazmayı kolaylaştıran yardımcı
examples/
  demo_element/  denemeler için sahte bir element
tests/
main.py          FastAPI uygulamasını kurar, API'yi ve arayüzü bağlar
```

## Kabuğun kendi kayıtları

Kabuk şunları kendi küçük veritabanında tutar: takılı elementler, moleküller ve
sürümleri, çalıştırma kaydı, kullanıcılar ve gruplar.

- Varsayılan SQLite'tır; kurulum gerektirmez. Gerekirse PostgreSQL kullanılır.
- Bu veritabanı elementlerin arkasındaki sistemlerin verisinden ayrıdır.

## Yetki

Yetki kabukta denetlenir, elementte değil.

- Üç profil vardır: mimar, tasarımcı, admin. Üst profil alttakinin her işini
  yapabilir.
- Adminler gruplara ayrılır; tasarımcı her molekülü hangi grupların göreceğini
  belirler.
- Admin atomları doğrudan çalıştıramaz; yalnızca kendisine açılan molekülleri
  kullanır.
- Kabuk elemente her istekte kimin adına çalıştığını bildirir; element bunu
  kendi kaydı için kullanabilir.

## Teknoloji kararları

| Karar | Seçim | Gerekçe |
|---|---|---|
| Dil | Python | Geliştiricinin dili; tek dil hedefi |
| API | FastAPI + Pydantic | Şemadan üretim, tip denetimi, eşzamansız çalışma |
| Arayüz | NiceGUI | Python içinde; FastAPI uygulamasına doğrudan bağlanır |
| Tuval | Drawflow | Prototipte NiceGUI'ye sorunsuz oturdu; yalnızca çizim için |
| Akış motoru | Kendi kodumuz | Bkz. `04-molekuller.md` |
| Kabuğun veritabanı | SQLite, isteğe bağlı PostgreSQL | Sıfır kurulum |
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
- FastAPI'nin yalnızca kullanılan parçaları iskelete alınır.
