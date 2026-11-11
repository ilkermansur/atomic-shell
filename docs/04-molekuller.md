# 4. Moleküller

Molekül, atomların bir kuruma anlam ifade edecek biçimde sıraya dizilmesidir.
Kod değil, veridir. Çalıştırılabilir olan yalnızca moleküldür; tek atomluk iş de
tek adımlı bir moleküldür.

## İki ayrı şey: sıra ve veri bağı

- **Sıra:** adımların hangi düzende çalışacağı. Her molekülde vardır.
- **Veri bağı:** bir adımın bir alanının değerini nereden alacağı. Adım bazında
  değil, alan bazında belirlenir.

Molekül "her atom öncekinden girdi alır" demek değildir. Molekül, sıralı adımlar
ve her adımın her alanı için tek bir sorunun cevabıdır: bu değer nereden gelecek?

## Alan kaynakları

| Kaynak | Anlamı |
|---|---|
| Formda sor | Admin sihirbazda yazar. Tasarımcı etiketi ve yardım metnini değiştirebilir. |
| Sabit değer | Tasarımcı baştan belirler; admin görmez. |
| Önceki adımın kaydı | Daha önceki bir adımın kaydından bir alan. Kayıt, o adımda oluşturulan ya da seçilen kayıttır. |

Aynı adımın farklı alanları farklı kaynaklardan gelebilir. Bir molekül ancak
her adımın her zorunlu alanının kaynağı belirliyse yayınlanabilir.

## Dört örnek

Örnekler `examples/todo` servisindendir.

**1. Yalnızca sıra.** "Standart listeleri aç"

```
1. Liste oluştur   ad = sabit "İş"
2. Liste oluştur   ad = sabit "Ev"
```

Adımlar birbirinden bağımsızdır. Admin hiçbir şey yazmaz.

**2. Çıktı sonraki adımın girdisi.** "Yeni proje"

```
1. Liste oluştur   ad      = formda sor
2. Görev oluştur   liste   = 1. adımın kaydı › id
                   başlık  = sabit "Proje planını yaz"
                   kod     = formda sor
```

Görevin ihtiyaç duyduğu liste henüz yoktur; onu oluşturan adım daha önce durur
ve görevin liste alanı ona bağlanır. Admin'e liste alanı sorulmaz.

**3. Seç ve işle.** "Görevi tamamla"

```
1. Görevleri göster   (tablo; admin bir satır seçer)
2. Görevi güncelle    id         = 1. adımın kaydı › id
                      tamamlandı = sabit evet
                      diğer alanlar = 1. adımın kaydından
```

Güncelleme ve silmede "seçili kayıt" böyle belirlenir.

**4. Girdi istemeyen.** "Görev listesi"

```
1. Görevleri göster
```

Tek adımlı, salt okunur molekül.

## Adım türleri

Bir adım, kaynağın kaydını üç yoldan biriyle ortaya koyar. Sonraki adımlar
hangisi olduğuna bakmadan "o adımın kaydı"na bağlanır; çünkü anayasa gereği
listedeki satır ile oluşturma ucunun döndürdüğü kayıt aynı modeldir.

| Adım türü | Admin ne yapar | Kullandığı atomlar |
|---|---|---|
| Oluştur | Formu doldurur | `create` |
| Seç | Tablodan bir satır seçer | `list` |
| Seç ya da oluştur | Var olanlardan seçer ya da yenisini oluşturur | `list` ve `create` |

"Seç ya da oluştur" adımında admin sihirbazda ikisinden birini tercih eder:

- **Var olanı seçerse** o adım uygulamada hiçbir şey yazmaz; seçilen kayıt
  sonraki adımlara verilir.
- **Yenisini oluşturursa** formu doldurur; kayıt uygulamada oluşturulur ve
  sonraki adımlara verilir.

Böylece "kullanıcı varsa onu kullan, yoksa oluştur" durumu dallanma olmadan,
tek molekülde çözülür.

**Varsayılan budur.** Kaynağının `list` atomu bulunan her oluşturma adımı
"seç ya da oluştur" olarak gelir; tasarımcı isterse adımı yalnızca "oluştur" ya
da yalnızca "seç" olarak daraltır. Dört adımlı bir molekülde admin üç adımda var
olan kaydı seçerse uygulamada yalnızca dördüncü adım çalışır; diğer üçünün
seçilmiş kayıtları ona girdi olarak verilir.

Örnek: "Telefon oluştur"

```
1. Kullanıcı   seç ya da oluştur
2. Dahili      seç ya da oluştur
3. Telefon     oluştur
               kullanıcı = 1. adımın kaydı › kullanıcı adı
               dahili    = 2. adımın kaydı › numara
               model, MAC adresi = formda sor
```

Güncelleme ve silme adımları da aynı düzeni kullanır: önce bir "seç" adımı,
ardından o kayda bağlanan `update` ya da `delete` adımı.

## Admin için: sihirbaz

Molekül admine adım adım ilerleyen bir sihirbaz olarak görünür.

- Her adım kendi başlığıyla ayrı bir ekrandır.
- Adımda yalnızca "formda sor" alanları ve tablo seçimi görünür. Kaynağı sabit
  değer ya da önceki adım olan alanlar gösterilmez.
- Admin'e soracak hiçbir şeyi olmayan adım sihirbazda atlanır.
- Sonda bir özet gelir: hangi adımlar, hangi değerlerle çalışacak.
- Admin "uygula" dediğinde iş başlar.

## Ne zaman ne çalışır

Önce bütün girdiler toplanır, sonra uygulanır.

- **Okuyan adımlar (`list`, `get`) sihirbaz sırasında çalışır.** Tablo
  gösterilir, satır seçilir. Bir şey değiştirmedikleri için güvenlidir.
- **Yazan adımlar (`create`, `update`, `delete`) en sonda, sırayla çalışır.**
  "Önceki adımın kaydı" bağları o anda çözülür: bir adım çalışır, servisin
  döndürdüğü kayıttan değer alınıp sonraki adıma verilir.

## Ön denetim

Geri alma olmadığı için hatalar hiçbir şey değişmeden yakalanmalıdır.

- **Biçim denetimi:** form alanları yazılırken kısıtlara göre denetlenir.
- **Varlık denetimi:** tasarımcı bir alana kural bağlar: "bu değer şu `list`
  atomunun şu kolonunda varsa uyar" ya da "yoksa uyar". Kabuk listeyi sorgular
  ve admin değeri yazdığı anda sonucu gösterir. Bunun için servise yeni uç
  yazmak gerekmez.
- Uyarı kalmadan "uygula" açılmaz.

## Yarıda kalma

Yazan adımlardan biri hata verirse kabuk durur ve sonrakileri denemez. Sonucu
adım adım gösterir:

```
1. Kullanıcı oluştur   yapıldı
2. Dahili oluştur      yapılamadı: 1042 numaralı dahili zaten var
3. Telefon oluştur     denenmedi
```

Yapılan adımlar geri alınmaz; temizlik elle yapılır. Çalıştırma, bütün
adımlarıyla birlikte kayda geçer.

## Yaşam döngüsü

1. **Taslak:** tasarımcı molekülü kurar. Admine görünmez.
2. **Deneme:** tasarımcı sihirbazı kendisi çalıştırıp sonucu görür.
3. **Yayın:** molekül yayınlanır; yetki verilen adminler görür. Her yayın bir
   sürümdür.
4. **Değişiklik:** yayındaki molekül düzenlenince yeniden taslak olur; önceki
   sürüm yayında kalır.

## Tasarım ekranı

- Solda moleküller ve atom paleti, ortada tuval, sağda seçili adımın alanları.
- Tuvalde çizgiler çalışma sırasını gösterir. Her düğümün solu giriş, sağı
  çıkıştır; üzerinde yalnızca neyin girip neyin çıktığının özeti görünür.
- Alan kaynakları tuvalde kablo olarak değil, yan panelde seçilir.
- Kabuk bağ önerir: bir alan başka bir kaynağa bağlantılıysa ve molekülde daha
  önce o kaynağı oluşturan ya da listeleyen bir adım varsa, alanı ona bağlamayı
  teklif eder.
- Altta sihirbazın canlı önizlemesi durur.

## Dışa ve içe aktarma

Her molekül tek bir dosya olarak dışa aktarılır ve başka bir kuruluma içe
aktarılır.

- Dosya adımları, sırayı, alan kaynaklarını, etiketleri, ön denetim kurallarını
  ve molekülün ihtiyaç duyduğu element ile atomları taşır.
- İçe aktarmada eksik element ya da atom varsa neyin eksik olduğu söylenir.
- İçe aktarılan molekül her zaman taslak olarak gelir.

DNA, bir kurulumdaki bütün moleküllerin toplu dışa aktarımıdır.

## İlk sürümün sınırları

Şimdilik yoktur; kabuk oturduktan sonra değerlendirilir:

- Genel koşul ve dallanma. "Seç ya da oluştur" adımı en sık görülen durumu
  karşılar; diğer durumlar için ayrı moleküller kurulur.
- Bir adımı bir listenin her satırı için tekrarlama.
- Molekülün içinde molekül.
- Geri alma.
