# 5. Arayüz

Arayüzün içinde alan mantığı yoktur. Yalnızca element, atom, molekül ve
çalıştırmayı tanır; katalogdan ne gelirse onu çizer. Yeni atom ya da molekül
yeni ekran kodu gerektirmez.

## Rollere göre ekranlar

### Mimar

- **Periyodik tablo:** her element iki harfli simgesi, adı ve atom sayısıyla
  bir kutudur.
- **İçe aktarma:** OpenAPI belgesi, servis adresi ve erişim anahtarıyla element
  ekler; anayasa denetiminin sonucunu görür.
- **Atom ekranı:** seçilen atomun tam arayüzü. Bütün alanlarıyla form ya da
  bütün kolonlarıyla tablo; oradan denenebilir.
- **Molekül üret:** atomdan tek adımlı bir molekül taslağı oluşturur.

### Tasarımcı

- **Molekül tasarım ekranı:** palet, tuval, alan paneli ve sihirbaz önizlemesi.
  Ayrıntı `04-molekuller.md` içindedir.
- **Kullanıcılar:** admin kullanıcısı oluşturur ve hangi molekülleri
  kullanabileceğini seçer.

### Admin

- **İşlemler:** yalnızca kendisine verilen, yayındaki moleküller kart olarak
  görünür.
- **Sihirbaz:** karta tıklayınca molekülün adımları sırayla gelir; sonda özet
  ve uygulama.
- **Kayıt:** kendi çalıştırmaları, adım adım sonuçlarıyla.

## Üretilen iki parça

Arayüzün bütün işini iki üretici yapar; ikisi de alan listesinden beslenir.

- **Form üretici:** alan türüne ve kısıtlarına göre girdi alanlarını çizer ve
  denetler.
- **Tablo üretici:** kayıt listesini kolon aramalı, sıralanabilir, CSV olarak
  dışa aktarılabilir tabloya çevirir.

Mimarın atom ekranı, tasarımcının önizlemesi ve adminin sihirbazı aynı iki
üreticiyi kullanır.

## Tasarım dili

- Minimalist ve temiz; üç rolün ekranları aynı dili kullanır.
- Ekranda yalnızca o anda gereken şey görünür; ayrıntı tıklayınca açılır.
- Bileşen takımı küçüktür: kart, form alanı, tablo, düğüm, durum etiketi.
- Periyodik tablo kutusu (büyük simge, küçük ad) arayüzün ve markanın tekrar
  eden görsel öğesidir.

## Tema ve dil

- **Koyu / açık tema:** üst çubuktan değişir. Bütün renkler tek bir değişken
  listesinden gelir.
- **TR / EN:** üst çubuktan değişir; tercih kullanıcı başına saklanır.
  - Çevrilenler: arayüzün kendi metinleri.
  - Çevrilmeyenler: element, atom ve alan başlıkları (servis hangi dilde
    yazdıysa) ile molekül adı ve form etiketleri (tasarımcı hangi dilde
    yazdıysa).

## Prototip

`prototype/` klasöründe üç rolün tıklanabilir bir prototipi bulunur. Sahte
veriyle çalışır ve tasarımın önceki halini gösterir.

- Uygun bulunanlar: üç ekranın yapısı, tasarım dili, periyodik tablo, tuval,
  tema ve dil.
- Güncel tasarımdan farkları: admin tek form görür (sihirbaz yok), tablo yok,
  içe aktarma yok.
- Kod atılabilirdir; ürüne taşınmaz. Görsel dil, renk değişkenleri ve çeviri
  sözlüğü taşınır.

## Sonraki arayüz parçaları

- **Pano:** okuyan moleküllerden beslenen tablolar ve kartlar.
- **Niyet çubuğu ve AI yardımcısı:** yazılan isteği mevcut moleküllere çevirir;
  tasarımcıya molekül taslağı önerir.
- **Alana özel görünümler:** bir elementin kabuğa kendi ekranını eklemesi.

## NiceGUI'nin sınırları

- Ekran durumu sunucuda tutulur; onlarca eşzamanlı yönetici için uygundur.
- Yoğun görsel parçalar (tuval) için dış kütüphane sarmak gerekir.
- Dış kütüphaneler ürünle birlikte dağıtılmalıdır; internete kapalı
  kurulumlarda dışarıdan yüklenemez.
- Arayüz kabuğun API'sinin sıradan bir istemcisi olduğu için ileride başka bir
  teknolojiyle yeniden yazılabilir.
