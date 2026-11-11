# 3. Atomlar ve içe aktarma

Atom, bir elementin tek bir API ucudur. Kabuk atomları kendisi tanımlamaz;
elementin OpenAPI belgesinden okur.

## İçe aktarma

Mimar bir elementi şu bilgilerle içe aktarır:

- **OpenAPI belgesi:** servisin `/openapi.json` adresi ya da dışa aktarılmış
  dosyası.
- **Servis adresi:** kabuğun uçları çağıracağı temel adres.
- **Erişim anahtarı:** servis istiyorsa.

Kabuk belgeyi okur, FastAPI anayasasına göre denetler ve sonucu gösterir:

- Kurala uyan her uç bir atom olur ve periyodik tabloda belirir.
- Kurala uymayan uç atom olarak alınmaz. Her sorun uç ve alan adıyla, hangi
  kuralı çiğnediğiyle birlikte listelenir: "`POST /todos`: `summary` yok (3.3)".

Arayüzün sorunsuz olmasının güvencesi bu denetimdir; kusurlu bir uç sessizce
bozuk bir form üretmez.

### Yeniden içe aktarma

Servis değiştiğinde belge yeniden içe aktarılır. Kabuk farkı gösterir: eklenen,
kaldırılan ve şeması değişen atomlar. Değişen ya da kaldırılan bir atomu
kullanan moleküller "gözden geçirilmeli" olarak işaretlenir.

### Postman

Postman koleksiyonu içe aktarma ilk sürümde yoktur. Koleksiyon alan tiplerini,
kısıtları ve cevap şemasını taşımadığı için ondan üretilen form denetimsiz
olur. Sonradan "en iyi çabayla" çalışan ayrı bir kapı olarak eklenebilir.

## Atomun adı ve kimliği

| Bilgi | Kaynağı | Örnek |
|---|---|---|
| Element | Belgenin başlığı | Yapılacaklar |
| Kaynak | Ucun etiketi ve yol kökü | `todos` |
| Eylem | `operation_id`'nin son parçası | `create` |
| Atomun adı | `operation_id` | `todos_create` |
| Başlık | `summary` | Görev oluştur |
| Açıklama | Docstring | Yeni bir görev oluşturur. |

## Eyleme göre arayüz

Kabuk her atom için arayüzü eylemine göre üretir.

| Eylem | Uç | Kabuğun ürettiği |
|---|---|---|
| `list` | `GET /{kaynak}` | Tablo |
| `get` | `GET /{kaynak}/{id}` | Tek kaydın ayrıntısı |
| `create` | `POST /{kaynak}` | Boş form |
| `update` | `PUT /{kaynak}/{id}` | Seçili kaydın dolu formu |
| `delete` | `DELETE /{kaynak}/{id}` | Seçili kaydı silme onayı |

### Tablo

- Kolonlar kayıt modelinin alanlarıdır; başlıklar alan başlıklarından gelir.
- Her kolonun kendi arama kutusu vardır.
- Birden çok kolonda arama yapılırsa sonuç bunların kesişimidir.
- Kolona tıklayınca sıralanır.
- O anda süzülmüş ve sıralanmış liste CSV olarak dışa aktarılır.
- Evet/hayır alanları işaretle, bağlantılı alanlar bağlı kaydın adıyla gösterilir.

### Form

Form girdi modelinin alanlarından üretilir.

| Alan türü | Formda |
|---|---|
| Metin | Metin kutusu; uzunluk ve desen denetimi |
| Sayı | Sayı kutusu; aralık denetimi |
| Evet / hayır | Radyo düğmesi |
| Seçenekli | Az seçenekte radyo düğmesi, çokta açılır liste |
| Tarih | Tarih seçici |
| Bağlantılı | Bağlı kaynağın listesinden beslenen seçim listesi |

- Alanın başlığı etiket, açıklaması yardım metni olur.
- Zorunlu alanlar işaretlidir; varsayılan değeri olan alan dolu gelir.
- Kısıtlar yazarken denetlenir: sekiz hane isteniyorsa yedi hane kabul edilmez.
- Form geçerli olmadan gönderilemez.

### Hatalar

- Servisin döndürdüğü girdi hataları ilgili alanın altında gösterilir.
- İş kuralı hataları (kayıt yok, kayıt zaten var) servisin cümlesiyle, formun
  üstünde gösterilir.
- Servise ulaşılamazsa bu açıkça söylenir; ham hata metni kullanıcıya
  gösterilmez, kayda yazılır.

## Atomu doğrudan görmek

Mimar ve tasarımcı periyodik tablodan bir atomu seçtiğinde onun tam arayüzünü
görür: bütün alanlarıyla form ya da bütün kolonlarıyla tablo. Atomu oradan
deneyebilirler.

Admin atomları göremez. Çalıştırılabilir olan yalnızca moleküldür.

## Molekül üret

Her atomun üstünde bir "molekül üret" düğmesi bulunur. Tek adımlı, bütün
alanları formda sorulan bir molekül taslağı oluşturur. Tasarımcı bunu olduğu
gibi yayınlayabilir ya da düzenleyebilir.

## Çalıştırma kaydı

Her atom çağrısı kabuğun kaydına geçer:

| Alan | İçerik |
|---|---|
| Kim | Kullanıcı |
| Ne zaman | Başlangıç ve süre |
| Hangi yoldan | Doğrudan atom denemesi ya da hangi molekülün hangi adımı |
| Atom | Element, atom, uç |
| Girdi | Gönderilen değerler |
| Sonuç | Durum kodu ve dönen kayıt ya da hata |

Geri alma yoktur. Kayıt, neyin yapıldığını sonradan görmek ve yarıda kalan işi
elle temizlemek içindir.
