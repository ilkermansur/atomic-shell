# atomic-shell

İçine API uçları alan bir kabuk. Sistemini "önce API" olarak yazarsın, OpenAPI
belgesini içe aktarırsın; kabuk o uçlardan arayüzü, yetkilendirmeyi, kaydı ve iş
akışlarını kendisi oluşturur.

- Her API ucu bir **atom**dur: girdisi ve çıktısı standarttır.
- Atomlarını sunan servis bir **element**tir; içe aktarılarak takılır.
- Atomlar bir tuvalde sıraya dizilerek **molekül** kurulur.
- Son kullanıcı yalnızca bu moleküllerden otomatik oluşan sade ekranları görür.

Kabuk hiçbir alanı tanımaz. İlk kullanım alanı `atomic-pbx` olacak: Asterisk
için yazılmış santral API'si (ayrı bir proje).

Durum: Faz 1 sürüyor. İçe aktarma, atom ekranları, molekül üretme ve sihirbaz
çalışıyor. Nerede kalındığı ve sıradaki adımlar: [DURUM.md](DURUM.md).

## Kısa sözlük

| Terim | Anlamı |
|---|---|
| Atom | Girdisi ve çıktısı standart tek bir API ucu |
| Element | Atomlarını kendi API'siyle sunan, içe aktarılan servis |
| Periyodik tablo | İçe aktarılmış elementlerin ve atomlarının kataloğu |
| Molekül | Atomlardan kurulan, kuruma özel iş. Çalıştırılabilir olan yalnızca moleküldür |
| DNA | Bir kurulumdaki bütün moleküllerin tanımı |

Üç rol: **mimar** atom yazar ve içe aktarır, **tasarımcı** molekül tasarlar,
**admin** kendisine verilen molekülleri kullanır.

## Belgeler

| Belge | İçerik |
|---|---|
| [1. Felsefe](docs/01-felsefe.md) | Amaç, benzetme, üç rol, ilkeler, kabuğun sınırı |
| [2. Mimari](docs/02-mimari.md) | Kabuk ve elementler, katmanlar, klasör yapısı, roller, kod kuralları |
| [3. Atomlar](docs/03-atomlar.md) | İçe aktarma, eyleme göre arayüz, tablo ve form, kayıt |
| [4. Moleküller](docs/04-molekuller.md) | Sıra ve veri bağı, alan kaynakları, sihirbaz, ön denetim, yarıda kalma |
| [5. Arayüz](docs/05-arayuz.md) | Rollere göre ekranlar, tasarım dili, tema ve dil |
| [6. Yol haritası](docs/06-yol-haritasi.md) | İki faz, adımlar, bitiş ölçütü, açık kararlar |
| [7. FastAPI anayasası](docs/07-fastapi-anayasasi.md) | Bir servisin kabuğa sorunsuz içe aktarılması için kurallar |

## Örnek element ve sınamalar

`examples/todo/` anayasaya göre yazılmış küçük bir yapılacaklar servisidir;
kabuk onunla geliştirilir ve sınanır.

```bash
python3 -m unittest discover -s tests
```

## Çalıştırma

İki ayrı süreç gerekir: örnek servis ve kabuk. Proje kökünden:

```bash
python3 -m uvicorn main:app --app-dir examples/todo --port 8101
```

```bash
python3 -m uvicorn app:app --port 8100
```

Ardından `http://localhost:8100` açılır. Kabuk boş başlar:

1. "İçe aktar"a bas. Servis adresi `http://localhost:8101` olarak gelir; belge
   oradan okunur ya da `examples/todo/openapi.json` dosyası yüklenir.
2. Periyodik tabloda bir atom seç; formu ya da tablosu belgeden üretilir.
3. "Molekül üret" ile atomu moleküle çevir.
4. "Moleküller" ekranından molekülü çalıştır.

## Prototip

Üç rolün ekranlarını sahte veriyle gösterir; tasarımın önceki halidir ve gerçek
bir elemente bağlı değildir.

```bash
python3 prototype/main.py
```

Ardından tarayıcıda `http://localhost:8090` açılır. NiceGUI kurulu olmalıdır.

## Teknoloji

Python, FastAPI, NiceGUI.
