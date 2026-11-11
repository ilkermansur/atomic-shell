# 5. Arayüz

Arayüzün içinde santral mantığı yoktur. Yalnızca dört şeyi tanır: element, atom,
molekül ve çalıştırma. Katalogdan ne gelirse onu çizer; yeni atom ya da molekül
yeni ekran kodu gerektirmez.

Atomlar yazıldıktan sonraki her iş arayüzden yapılır.

## Üç profil

| Profil | Yaptığı iş | Çalıştığı yer |
|---|---|---|
| Mimar | Atom ve element yazar | Kod; arayüzde periyodik tablo ve atom deneme ekranı |
| Tasarımcı | Atomlardan molekül tasarlar, yayınlar, admin gruplarına açar | Molekül tasarım ekranı |
| Admin | Kendisine açılan molekülleri çalıştırarak santral tanımlarını yapar | Moleküllerden otomatik oluşan ekranlar |

- Üst profil alttakinin her işini yapabilir.
- Adminler gruplara ayrılır; tasarımcı her molekülü hangi grupların göreceğini
  belirler.
- Buradaki admin santralin günlük yöneticisidir; sistemin en yetkili profili
  mimardır.

Kurulumun ilk döneminde üç rol de uzmandadır. Eğitimle önce admin, sonra
tasarımcı rolü kurumun personeline geçer.

## Ekranlar

### Mimar: periyodik tablo

- Her element iki harfli simgesi, adı ve atom sayısıyla bir kutudur.
- Kurulu olmayan elementler soluk durur; kurumun neleri ekleyebileceğini
  gösterir.
- Elemente tıklanınca atomları, atoma tıklanınca girdi ve çıktı şeması ile
  etiketleri (okur/yazar, geri alınabilir) görünür.
- "Dene" atomu doğrudan çalıştırır ve dönen zarfı gösterir.

### Tasarımcı: molekül tasarım ekranı

- Solda moleküller ve atom paleti, ortada tuval, sağda seçili düğümün alanları.
- Üstte molekülün adı, durumu, grupları ve düğmeler: dışa aktar, dene, yayınla.
- Altta admin formunun canlı önizlemesi.
- Ayrıntılar `04-molekuller.md` içindedir.

### Admin: işlemler ve kayıt

- Yalnızca yayında olan ve adminin grubuna açılmış moleküller kart olarak
  görünür.
- Karta tıklayınca otomatik form, ardından plan, ardından uygulama gelir.
- Çıktısı liste olan molekül tablo olarak çizilir; tasarımcı satırlara başka
  molekülleri eylem olarak bağlayabilir.
- Kayıt bölümü çalıştırmaları listeler; her satırda geri al düğmesi bulunur.
- "Yeni molekül iste" talebi tasarımcıya iletir.

## Tasarım dili

Arayüz minimalist ve temizdir; üç profilin ekranları aynı dili kullanır.

- Admin ekranı tek sütunlu sade bir formdur.
- Ekranda yalnızca o anda gereken şey görünür; ayrıntı tıklayınca açılır.
- Bileşen takımı küçüktür: kart, form alanı, tablo, düğüm, durum etiketi.
- Periyodik tablo kutusu (büyük simge, küçük ad) arayüzün ve markanın tekrar
  eden görsel öğesidir.

## Tema ve dil

- **Koyu / açık tema:** üst çubuktan değişir. Bütün renkler tek bir değişken
  listesinden gelir.
- **TR / EN:** üst çubuktan değişir; tercih kullanıcı başına saklanır.
  - Çevrilenler: arayüzün kendi metinleri, profil adları, element, atom ve alan
    adları.
  - Çevrilmeyenler: molekül adı ve form etiketleri. Bunlar kurumun DNA'sıdır;
    tasarımcı hangi dilde yazdıysa öyle görünür.

## Sonraki arayüz parçaları

Çekirdek arayüz oturduktan sonra eklenir; olmasalar da sistem kullanılır.

- **Pano:** hazır moleküllerden beslenen tablolar ve kartlar; canlı durum.
- **Çağrı haritası:** veritabanındaki kayıtlardan otomatik çizilen yönlendirme
  görünümü. Kaynak değil, görünümdür. "Bu numarayı ararsam ne olur" simülasyonu
  buraya gelir.
- **Niyet çubuğu:** yazılan isteği mevcut form ve moleküllere çevirir. Cevap
  metin değil, arayüzün kendisidir. AI kapalıyken arama ve komut paleti olarak
  çalışır.
- **AI yardımcısı:** "bu çağrı neden buraya düştü" gibi soruları açıklar,
  tasarımcıya mevcut atomlardan molekül taslağı önerir.

## Prototip

`prototype/` klasöründe üç profilin tıklanabilir bir prototipi bulunur. Sahte
veriyle çalışır; gerçek Asterisk'e ya da veritabanına bağlı değildir.

Prototipin gösterdikleri:

- Üç ekranın yapısı ve tasarım dili uygun bulundu.
- Drawflow, NiceGUI içine yaklaşık 25 satır JavaScript ile oturdu.
- Koyu/açık tema ve TR/EN çalışıyor.

Prototipin eksikleri:

- Koşul ve alt molekül düğümleri yok.
- Tuvalde elle çizilen bağlantılar kaydedilmiyor.
- Veri bellekte durur.
- Kod atılabilirdir: tek dosyada, iç içe işlevlerle yazıldı. Ürüne taşınmaz;
  her ekran kod kurallarına göre `gui/` altında yeniden yazılır. Görsel dil,
  renk değişkenleri ve çeviri sözlüğü taşınır.

## NiceGUI'nin sınırları

- Ekran durumu sunucuda tutulur; onlarca eşzamanlı yönetici için uygundur,
  binlerce kullanıcılı bir portal için değildir.
- Yoğun görsel parçalar (tuval, çağrı haritası) için dış kütüphane sarmak
  gerekir.
- Arayüz API'nin sıradan bir istemcisi olduğu için ileride başka bir
  teknolojiyle yeniden yazılabilir; atomlara ve moleküllere dokunulmaz.
- Dış kütüphaneler ürünle birlikte dağıtılmalıdır; internete kapalı kurumlarda
  dışarıdan yüklenemez.
