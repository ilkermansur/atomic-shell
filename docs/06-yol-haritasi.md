# 6. Yol haritası ve açık kararlar

## İki faz

1. **Faz 1: atomic-shell.** Kabuk tek başına, kaya gibi sağlam hale getirilir.
   Bu fazda santral yoktur; kabuk örnek bir elementle geliştirilir ve sınanır.
2. **Faz 2: bütünleştirme.** `atomic-pbx` kabuğa takılan ilk gerçek element
   olur. Santral için yapılan tasarım (`../atomic-pbx/docs/`) olduğu gibi
   durmaktadır ve bu fazda kabuğun sözleşmesine göre uyarlanacaktır.

Bu belge Faz 1'i anlatır.

## Alt projeler

| No | Alt proje | İçerik | Durum |
|---|---|---|---|
| 0 | Arayüz prototipi | Üç profil, sahte veri | Tamamlandı, yapı onaylandı |
| 1 | Sözleşme ve çekirdek | Atom sözleşmesi, element takma, katalog, atom çalıştırma, kayıt ve geri alma, örnek element, mimar ekranı | Tasarım yazıldı (`02`, `03`) |
| 2 | Moleküller | Molekül modeli, çalıştırıcı, deneme, zincirleme geri alma, sürümleme, dışa/içe aktarma | Tasarım yazıldı (`04`); ayrıntı planı yazılacak |
| 3 | Tasarımcı ve admin ekranları | Tuval, alan paneli, otomatik formlar, gruplar, tema, dil | Tasarım yazıldı (`05`); ayrıntı planı yazılacak |
| 4 | MCP ve AI | Atom ve moleküllerin araç olarak sunulması, açıklama, molekül taslağı, niyet çubuğu | Sonra |
| 5 | Bağdaştırıcılar | OpenAPI içe aktarma, MCP köprüsü | Sonra |
| 6 | Eklenti noktaları | Alana özel görünümler, yayın anında elemente bildirim | Sonra |

## v1.0'ın tanımı

Alt proje 1, 2 ve 3 birlikte kullanılabilir ilk sürümü oluşturur:

- Bir element adresiyle takılıyor; atomları periyodik tabloda görünüyor.
- Tasarımcı tuvalde molekül kuruyor ve yayınlıyor.
- Admin moleküllerden otomatik oluşan ekranları kullanıyor.
- Her çalıştırma kayıtlı; geri alınabilir olanlar geri alınabiliyor.

Kabuğun v1.0'ı `atomic-pbx` ile birlikte sınanır; ilk gerçek element odur.

## İlk uygulama adımı

Çalışan en küçük dikey dilim:

1. Örnek element: FastAPI ile yazılmış, iki sahte atom sunan küçük bir servis.
2. Kabuk çekirdeği: elementi adresinden okuyup kataloğa alan kod.
3. Kabuk API'si: katalog ve atom uygulama uçları, çalıştırma kaydı.
4. Mimar ekranı: periyodik tablo, atom ayrıntısı, deneme.

Amaç, iskeletin tamamını küçük ve okunur haldeyken görmek ve sözleşmeyi gerçek
bir HTTP sınırı üzerinden sınamaktır.

## Açık kararlar

### İş ve hukuk

1. **Lisans türü.** GPL/AGPL önerildi, kesinleşmedi. Kabuk ve santral ayrı
   projeler olduğu için lisansları ayrı ayrı seçilebilir.
2. **Ad ve marka.** `atomic-shell` adını kullanan başka ürün olup olmadığı
   araştırılmadı.
3. **Benzer araçlar.** API'lerden iç araç arayüzü üreten ürünler ve akış
   araçları bu alanda. Kabuğu ayıran yanlar: plan ve geri alma içeren atom
   sözleşmesi, üç profil, DNA, sade Python çekirdeği. Başlamadan önce birkaçına
   göz atılması önerilir.

### Tasarımı eksik olanlar

4. **Giriş ve kullanıcı yönetimi.** Arayüz girişi, parola politikası, AD/LDAP
   ya da tek oturum açma belirlenmedi.
5. **Molekülde geri alınamayan adımlar.** Geri alınamayan bir adımdan sonra
   hata olursa ne olacağı; bu adımların sona zorlanıp zorlanmayacağı.
6. **Eşzamanlı değişiklik.** İki adminin aynı kaynağı aynı anda değiştirmesi.
7. **İki dilli molekül.** Molekül adı ve form etiketleri tek dilde. Dil başına
   etiket gerekip gerekmediği.
8. **Alana özel görünümler.** Bir elementin kabuğa kendi ekranını (örneğin
   santralin çağrı haritası) nasıl ekleyeceği.
9. **Yayın anında elemente bildirim.** Bazı moleküllerin yayınlanınca element
   tarafında derlenmesi gerekir (santralin çağrı anı akışları). Kabuğun bunu
   nasıl bildireceği.
10. **Olaylar.** Elementten kabuğa olay akışı (canlı ekranlar ve olayla
    tetiklenen moleküller için) sözleşmede henüz yok.
11. **Element sürümü değişince moleküller.** Atomun şeması değiştiğinde ona
    bağlı moleküllerin nasıl işaretleneceği ve güncelleneceği.
12. **AI.** Bulut modeli mi, yerel model mi; MCP sunucusunun yetki modeli.

### İşletim

13. **Kabuk ile element arası güvenlik.** Erişim anahtarının saklanması,
    şifreli bağlantı.
14. **Yedekleme ve yükseltme.** Kabuğun veritabanı yedeği ve sürüm yükseltme
    yolu.

### Doğrulanması gerekenler

15. **Tuval kütüphanesi.** Drawflow prototipte çalıştı; küçük harita, gruplama
    ve büyük akışlardaki davranışı sınanmadı.
16. **Kendi sunucusuna HTTP isteği.** Arayüzün kabuğun API'sini HTTP ile
    çağırması prototipte denenmedi.
