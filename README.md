# atomic-shell

İçine API uçları alan bir kabuk. Sistemini "önce API" olarak yazarsın; kabuk o
uçlardan arayüzü, yetkilendirmeyi, kaydı ve iş akışlarını kendisi oluşturur.

- Her API ucu bir **atom**dur: girdisi ve çıktısı standarttır.
- Atomlarını sunan servis bir **element**tir; kabuğa adresiyle takılır.
- Atomlar bir tuvalde bir araya getirilerek **molekül** kurulur.
- Son kullanıcı yalnızca bu moleküllerden otomatik oluşan sade ekranları görür.

Kabuk hiçbir alanı tanımaz. İlk kullanım alanı `atomic-pbx` olacak: Asterisk
için yazılmış santral API'si (ayrı bir proje).

Durum: tasarım aşaması. Tasarım belgeleri ve tıklanabilir bir arayüz prototipi
var; ürün kodu henüz yazılmadı.

## Kısa sözlük

| Terim | Anlamı |
|---|---|
| Atom | Girdisi ve çıktısı standart tek bir API ucu |
| Element | Atomlarını kendi API'siyle sunan, takılıp çıkarılan servis |
| Periyodik tablo | Takılı elementlerin ve atomlarının kataloğu |
| Molekül | Atomlardan kurulan, kuruma özel iş |
| DNA | Kurumun tüm molekül ve ayar tanımları |

Üç profil: **mimar** atom yazar, **tasarımcı** molekül tasarlar, **admin**
molekülleri kullanır.

## Belgeler

| Belge | İçerik |
|---|---|
| [1. Felsefe](docs/01-felsefe.md) | Amaç, benzetme, üç profil, ilkeler, kabuğun sınırı |
| [2. Mimari](docs/02-mimari.md) | Kabuk ve elementler, katmanlar, klasör yapısı, yetki, teknoloji, kod kuralları |
| [3. Atom sözleşmesi](docs/03-atom-sozlesmesi.md) | Elementin sunduğu uçlar, üç seviye, katalog, zarf, hata kodları, kayıt ve geri alma |
| [4. Moleküller](docs/04-molekuller.md) | Molekül yapısı, tuval, yaşam döngüsü, dışa/içe aktarma, DNA |
| [5. Arayüz](docs/05-arayuz.md) | Ekranlar, tasarım dili, tema ve dil, prototip |
| [6. Yol haritası](docs/06-yol-haritasi.md) | Alt projeler, v1.0 tanımı, ilk adım, açık kararlar |

Belge 4 ve 5'teki örnekler santralden alınmıştır; kabuğun kendisi santrale özgü
değildir.

## Prototip

Üç profilin ekranlarını sahte veriyle gösterir. Gerçek bir elemente bağlı
değildir.

```bash
python3 prototype/main.py
```

Ardından tarayıcıda `http://localhost:8090` açılır. NiceGUI kurulu olmalıdır.

## Teknoloji

Python, FastAPI, NiceGUI.
