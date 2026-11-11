# 4. Moleküller

Molekül, atomların bir kuruma anlam ifade edecek biçimde bir araya
getirilmesidir. Kod değil, veridir: veritabanında bir çizge olarak saklanır.

## Molekül türleri

| Tür | Tetikleyen | Özellik |
|---|---|---|
| İşlem molekülü | İnsan veya AI | Deneme çalıştırması, onay, geri alma |
| Akış molekülü | Gelen çağrı | Dallanma, adım başına süre sınırı, varsayılan yol; onay yok |
| Olay molekülü | Sistem olayı (çağrı bitti, cihaz düştü) | Arka planda çalışır; hata çağrıyı etkilemez |

İlk sürümde yalnızca işlem molekülleri yazılır. Yapı diğer ikisini taşıyacak
şekilde kurulur.

Akış molekülleri kuyruk, sesli mesaj, konferans gibi hazır Asterisk
uygulamalarını yeniden yazmaz; çağrıyı onlara teslim eden atomları kullanır.

## Molekülün yapısı

Molekül şunlardan oluşur:

- **Düğümler:** form, atom, koşul, sonuç, alt molekül.
- **Bağlantılar:** düğümler arasındaki çalışma sırası.
- **Alan eşlemeleri:** her atom girdisinin nereden geleceği.
- **Tuval konumları:** düğümlerin ekrandaki yeri.
- **Kimlik bilgileri:** ad, açıklama, durum, sürüm, açıldığı gruplar.

### Düğüm türleri

| Düğüm | İşi | Giriş / çıkış |
|---|---|---|
| Form | Molekülün başlangıcı; admine sorulan alanları taşır | Çıkış: 1 |
| Atom | Periyodik tablodan seçilen tek işlem | Giriş: 1, çıkış: 1 |
| Koşul | Tek bir karşılaştırma | Giriş: 1, çıkış: 2 (evet, hayır) |
| Alt molekül | Yayınlanmış başka bir molekül, tek düğüm olarak | Giriş: 1, çıkış: 1 |
| Sonuç | Admine gösterilecek özet | Giriş: 1 |

### Alan kaynakları

Her atom düğümünün her girdi alanı üç kaynaktan birine bağlanır:

- **Formda sor:** alan admin formunda görünür. Tasarımcı etiketini ve yardım
  metnini yazar.
- **Sabit değer:** tasarımcı değeri belirler; admin görmez.
- **Önceki adımdan:** daha önceki bir düğümün çıktısı kullanılır. Tip uyumu
  tasarım anında denetlenir.

Admin ekranı "formda sor" alanlarından otomatik oluşur. Esneklik buradan gelir:
tasarımcı ne kadar çok alanı sabitlerse admin ekranı o kadar sadeleşir. Aynı
atomlardan bir kurumda 3 alanlı, diğerinde 15 alanlı bir "yeni personel" çıkar.

### Alt molekül

- Yayınlanmış bir molekül başka bir molekülde tek düğüm olarak kullanılabilir.
- Dışarıdan bakıldığında molekül de atom gibidir: girdisi formu, çıktısı
  sonucudur.
- Bir molekül kendisini doğrudan ya da dolaylı içeremez.
- İç içe derinlik en çok iki seviyedir.

### Yasaklar

- Döngü yoktur; geriye dönen bağlantı çizilemez.
- Karmaşık mantık molekülde kurulmaz; mimarın yazacağı yeni bir atom olur.

## Tuval

Molekül tasarım ekranı bir akış tuvalidir ve geniş, ayrıntılı akışları taşıyacak
şekilde kurulur.

- **Çizgiler çalışma sırasını ve dallanmayı gösterir.** Alan eşleme tuvalde
  kablo olarak değil, düğüme tıklayınca açılan yan panelde yapılır.
- Her düğümün solunda giriş, sağında çıkış noktası bulunur.
- Düğümün üzerinde alanlar tek tek değil, yalnızca neyin girip neyin çıktığının
  özeti gösterilir. Bu bilgi katalogdan gelir.
- Bir düğüm seçildiğinde veri aldığı ve verdiği düğümler vurgulanır.
- Büyük akışlar için: yakınlaştırma ve kaydırma, küçük harita, düğümleri
  adlandırılmış çerçevelerde gruplayıp daraltma, düğüm arama, otomatik
  yerleşim, not ekleme ve hataları listeleyen bir denetim paneli.

## Yaşam döngüsü

1. **Taslak:** tasarımcı molekülü kurar. Admine görünmez.
2. **Deneme:** hiçbir şey değiştirmeden adımların sırası ve geri alınabilirliği
   gösterilir.
3. **Yayın:** molekül seçilen admin gruplarına açılır. Her yayın bir sürümdür.
4. **Değişiklik:** yayındaki molekül düzenlenince yeniden taslak olur; önceki
   sürüm yayında kalır. Önceki sürüme dönülebilir.

## Çalıştırma

İşlem molekülü admin tarafından şöyle çalıştırılır:

1. Admin formu doldurur.
2. Sistem "şunlar yapılacak" planını gösterir; geri alınamayan adımlar
   işaretlidir.
3. Admin onaylar; adımlar sırayla uygulanır.
4. Sonuç gösterilir ve çalıştırma kayda geçer.

Bir adım hata verirse o ana kadar uygulanan geri alınabilir adımlar ters sırayla
geri alınır. Kayıttaki bir çalıştırma sonradan da geri alınabilir.

## Akış motoru

Molekül çalıştırıcı projenin kendi kodudur; hazır bir akış motoru (n8n,
Node-RED vb.) kullanılmaz.

- Hazır motorlarda plan, onay ve zincirleme geri alma kavramları yoktur; bunlar
  bu ürünün temel vaadidir.
- Hazır motor ikinci bir dil ve çalışma ortamı getirir; her satıra hâkim olma
  hedefiyle çelişir. Bazılarının lisansı açık kaynak ve ticari kullanım
  modeliyle de bağdaşmayabilir.
- Çalıştırıcının işi dardır (sıra, koşul, alt molekül, geri alma) ve küçük bir
  Python modülü olarak yazılır.
- Hazır kütüphane yalnızca tuvalin çizimi için kullanılır.

## Dışa ve içe aktarma

Her molekül tek bir dosya olarak dışa aktarılır ve başka bir kuruluma içe
aktarılır.

- Dosya şunları taşır: düğümler, bağlantılar, alan eşlemeleri, form etiketleri
  ve molekülün ihtiyaç duyduğu elementler ile atom sürümleri.
- İçe aktarmada uyumluluk denetlenir: eksik element, eksik atom ya da sürüm
  uyuşmazlığı varsa neyin eksik olduğu söylenir.
- Kuruma özgü sabit değerler (belirli bir kuyruk, belirli bir trunk) hedef
  kurulumda yoksa "yeniden bağlanması gereken alan" olarak işaretlenir.
- Parola ve anahtar gibi gizli değerler dosyaya yazılmaz.
- İçe aktarılan molekül her zaman taslak olarak gelir.

## DNA

DNA, kurumun tüm moleküllerinin ve ayarlarının dışa ve içe aktarılabilen
halidir. Tek molekül dosyasıyla aynı biçimi kullanır, kapsamı farklıdır.

Kullanım yerleri:

- Yedekleme ve sürümleme.
- Yeni bir kuruma başlangıç seti taşımak.
- Kurumun sistemi başka bir uzmana ya da kendi personeline devretmesi.

## Örnek: yeni personel

```
Form ─▶ Dahili oluştur ─▶ Sesli mesaj kutusu aç ─▶ Kuyruğa üye ekle ─▶ E-posta gönder ─▶ Sonuç
```

Dört atomun toplam 12 girdi alanı vardır. Tasarımcı bunlardan 5'ini forma
bağlar (ad soyad, dahili numara, birim ve iki atomda ortak kullanılan e-posta),
5'ini sabitler (kodek, azami cihaz sayısı, PIN, öncelik, e-posta şablonu), 2'sini
önceki adımdan bağlar. Aynı etiketli alanlar formda tek alan olarak göründüğü
için admin yalnızca 4 alanlı bir form görür.
