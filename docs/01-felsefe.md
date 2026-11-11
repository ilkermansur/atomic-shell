# 1. Felsefe ve benzetme

## Amaç

atomic-shell, içine API uçları alan bir kabuktur. Bir sistemi "önce API" olarak
yazarsın; kabuk o uçlardan arayüzü, yetkilendirmeyi, kaydı ve iş akışlarını
kendisi oluşturur. Arayüzle bir daha uğraşılmaz.

Kabuk hiçbir alanı tanımaz. İçinde santral, ağ cihazı ya da müşteri kaydı gibi
bir kavram yoktur; yalnızca element, atom, molekül ve çalıştırmayı bilir.

İlk kullanım alanı `atomic-pbx`'tir: Asterisk için yazılmış santral API'si
kabuğa takılan ilk elementtir.

## Benzetme

Kabuğun dili, markası ve felsefesi kimya üzerine kuruludur. Fizikte atomun
elektron kabuğuna "atomic shell" denir; ad buradan gelir.

| Terim | Kabukta | Örnek |
|---|---|---|
| Atom altı parçacık | Bir elementin arkasındaki sistemin iç işleyişi. Kabuk bu seviyeyi görmez. | SIP mesajı, SQL sorgusu |
| Atom | Girdisi ve çıktısı standart tek bir API ucu. Kabuğun gördüğü en alt seviye. | `asterisk.extension.create` |
| Element | Atomlarını kendi API'siyle sunan, ayrı çalışan servis. Takılır ve çıkarılır. | Santral API'si, CRM, e-posta |
| Periyodik tablo | Takılı elementlerin ve atomlarının kataloğu. | Yeni element takılınca tabloya bir kutu eklenir |
| Molekül | Farklı elementlerin atomlarından kurulan, kuruma anlam ifade eden iş. | Yeni personel |
| DNA | Bir kurumun molekül ve ayar tanımlarının tamamı. | Dışa aktarılabilen tanım seti |
| Kabuk | Katalog, molekül çalıştırıcı, kayıt, yetki ve arayüz. | Her kurulumda aynı kod |

Benzetmenin taşıdığı fikirler:

- **Atom altına inilmez.** Karmaşıklık atomun içinde kapalı kalır. Molekül
  kuran kişi arkadaki sistemi bilmek zorunda değildir.
- **Yeni moleküller kurulur.** Aynı atomlardan her kurumda farklı işler çıkar.
- **Her kurumun DNA'sı farklıdır.** Kabuk ve elementler ortaktır; kurumu özgün
  yapan DNA'sıdır. DNA okunabilir, kopyalanabilir ve kuruma aittir.

## Üç profil

| Profil | Yaptığı iş |
|---|---|
| Mimar | Atom ve element yazar; yani API uçlarını |
| Tasarımcı | Arayüzde atomlardan molekül tasarlar ve yayınlar |
| Admin | Kendisine açılan molekülleri kullanır |

Atomlar yazıldıktan sonraki her iş arayüzden yapılır.

## İlkeler

1. **Kabuk alan bilmez.** İçinde hiçbir sisteme özgü kod bulunmaz.
2. **Atomlar tek kalıptadır.** Her atom aynı biçimde girdi alır, aynı zarfla
   cevap verir.
3. **Her element kendi atomlarıyla gelir.** Element ayrı bir servistir; kabuğa
   adresiyle takılır.
4. **Atom başka atomu çağırmaz, element başka elementi tanımaz.** Birleştirme
   yalnızca moleküllerde olur.
5. **Molekülleri yalnızca kabuk çalıştırır.**
6. **Arayüzde yapılabilen her şey kabuğun API'sinde de vardır.**
7. **Her değişiklik kayıtlıdır ve mümkünse geri alınabilir.** Geri alınamayan
   işlem bunu önceden bildirir.
8. **Kabuk kapalıyken elementler çalışmaya devam eder.** Kabuk yönetim
   tarafıdır; arkadaki sistemler ona bağımlı değildir.
9. **En yalın API de takılabilir.** Plan ve geri alma isteğe bağlıdır; yalnızca
   katalog ve uygulama sunan bir element de arayüzünü alır.
10. **Molekül dili küçük kalır.** Sıra, alan eşleme, koşul ve alt molekül.
    Döngü ve karmaşık mantık yeni bir atomdur.
11. **AI sessizce uygulamaz ve sistem AI olmadan da tam çalışır.**
12. **Kod sade ve anlatılabilir yazılır.** Bkz. `02-mimari.md`.

## Sınır: kabuk neyi yapmaz

- Bir alanın iş mantığını içermez; o iş elementindir.
- Arkadaki sistemlere (veritabanı, santral, cihaz) doğrudan bağlanmaz; yalnızca
  elementin API'sine konuşur.
- Genel amaçlı bir programlama aracı değildir. İlk kullanım alanının gerçekten
  ihtiyaç duyduğu kadar genel yazılır; ikinci bir kullanım alanı ortaya
  çıkmadan onun için özellik eklenmez.
