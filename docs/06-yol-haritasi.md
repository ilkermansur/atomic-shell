# 6. Yol haritası ve açık kararlar

## İki faz

1. **Faz 1: atomic-shell.** Kabuk tek başına, kaya gibi sağlam hale getirilir.
   Gerçek bir sistem yoktur; kabuk `examples/todo` servisiyle geliştirilir ve
   her köşesi onunla sınanır.
2. **Faz 2: bütünleştirme.** Gerçek elementler yazılır ve kabuğa takılır. İlki
   Asterisk için yazılacak santral API'sidir (`atomic-pbx`, ayrı proje).

Bu belge Faz 1'i anlatır. Güncel durum ve bilinen pürüzler için kökteki
`DURUM.md`.

## Faz 1'in adımları

Her adım kendi sınamalarıyla birlikte yazılır ve bir öncekinin üstüne kurulur.

| No | Adım | İçerik | Durum |
|---|---|---|---|
| 0 | Prototip | Üç rolün ekranları, sahte veri | Tamamlandı |
| 1 | Anayasa ve örnek element | FastAPI kuralları; yapılacaklar servisi | Tamamlandı |
| 2 | İçe aktarıcı | OpenAPI belgesini okuma, anayasa denetimi, atom modelleri | Tamamlandı |
| 3 | Atom çağırma ve kayıt | Kabuğun veritabanı, katalog, atomu HTTP ile çağırma, hata çevirisi, çalıştırma kaydı | Tamamlandı |
| 4 | Kabuğun API'si | İçe aktarma, katalog, atom çalıştırma ve kayıt uçları | Tamamlandı |
| 5 | Mimar ekranı | Periyodik tablo, içe aktarma, form ve tablo üreticileri, atom ekranı | Tamamlandı |
| 6 | Moleküller | Model, doğrulama, çalıştırıcı, ön denetim, yarıda kalma raporu, "molekül üret" | Kısmen: çalıştırıcı, yarıda kalma ve "molekül üret" var; ön denetim yok |
| 7 | Admin ekranı | Sihirbaz, özet, uygulama, kayıt | Kısmen: sihirbaz ve kayıt var; rollere göre görünürlük yok |
| 8 | Tasarım ekranı | Tuval, alan paneli, bağ önerisi, önizleme, yayınlama | |
| 9 | Kullanıcılar | Giriş, üç rol, admin başına molekül yetkisi | |
| 10 | Tamamlayıcılar | Tema, dil, molekül dışa/içe aktarma, yeniden içe aktarma farkı | Kısmen: tema ve dil var |

Adım 5'in sonunda gösterilebilir ilk şey ortaya çıkar: bir servis içe aktarılır
ve her ucunun formu ya da tablosu kendiliğinden oluşur.

## Faz 1 ne zaman biter

- Yapılacaklar servisi içe aktarılıyor; dokuz ucunun hepsi sorunsuz arayüz
  alıyor.
- Anayasaya uymayan bir belge, her sorunu adıyla söyleyen bir raporla
  reddediliyor.
- Dört örnek molekül (`04-molekuller.md`) kuruluyor, yayınlanıyor ve admin
  tarafından çalıştırılıyor.
- Ön denetim ve yarıda kalma raporu doğru çalışıyor.
- Admin yalnızca kendisine verilen molekülleri görüyor.
- Her çalıştırma kayıtta.

## Açık kararlar

### İş ve hukuk

1. **Lisans.** Depo herkese açık ama lisans dosyası yok. GPL/AGPL önerildi,
   kesinleşmedi.
2. **Ad ve marka.** `atomic-shell` adını kullanan başka ürün olup olmadığı
   araştırılmadı.

### Tasarımı sonraya bırakılanlar

3. **Geri alma.** Şimdilik yok; yarıda kalan iş elle temizlenir.
4. **Koşul, tekrar ve iç içe molekül.** İlk sürümde yok.
5. **Postman içe aktarma.** İlk sürümde yok.
6. **Giriş yöntemi.** Kullanıcı adı ve parola ile başlanacak; AD/LDAP ya da tek
   oturum açma sonra.
7. **Eşzamanlı değişiklik.** İki kişinin aynı kaydı aynı anda değiştirmesi.
8. **İki dilli etiketler.** Molekül adı ve form etiketleri tek dilde.
9. **Büyük listeler.** Kabuk listenin tamamını alıp aramayı kendisi yapıyor;
   on binlerce kayıtta sayfalama ve sunucu tarafı arama gerekecek.
10. **Olaylar.** Elementten kabuğa olay akışı (canlı ekranlar için) yok.
11. **Alana özel görünümler.** Bir elementin kabuğa kendi ekranını eklemesi.
12. **AI ve MCP.** Atom ve moleküllerin AI'a araç olarak sunulması.

### Doğrulanması gerekenler

13. **Tuval kütüphanesi.** Drawflow prototipte çalıştı; büyük akışlardaki
    davranışı sınanmadı.
14. **Arayüzün kendi sunucusunu HTTP ile çağırması.** Henüz denenmedi.
