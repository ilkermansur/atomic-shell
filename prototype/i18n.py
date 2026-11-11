"""Arayüz dili. Kaynak dil Türkçe; EN sözlüğünde karşılığı olmayan metin Türkçe kalır.

Yalnızca arayüzün kendi metinleri ve atom/element adları çevrilir. Molekül adı ve
form etiketleri kurumun DNA'sıdır; tasarımcı hangi dilde yazdıysa öyle görünür.
"""
from nicegui import app

EN = {
    # çerçeve
    "prototip, sahte veri": "prototype, fake data",
    "Mimar": "Architect", "Tasarımcı": "Designer", "Admin": "Admin",
    "Koyu / açık tema": "Dark / light theme", "Dil": "Language",
    # mimar
    "Periyodik tablo": "Periodic table",
    "Kurulu elementler ve sundukları atomlar. Soluk kutular kurulu değil.":
        "Installed elements and the atoms they provide. Dimmed tiles are not installed.",
    "atom": "atoms", "kurulu değil": "not installed", "Atomlar": "Atoms",
    "Ayrıntısını görmek için bir atom seç.": "Pick an atom to see its details.",
    "yazar": "writes", "okur": "reads",
    "geri alınabilir": "reversible", "geri alınamaz": "irreversible",
    "Girdi": "Input", "Çıktı": "Output", "Girdi almaz.": "Takes no input.",
    "Dene": "Try", "Zarf (sahte cevap)": "Envelope (fake response)",
    "yok": "none",
    # tasarımcı
    "Moleküller": "Molecules", "Yeni molekül": "New molecule", "sürüm": "version",
    "Yayında": "Published", "Taslak": "Draft", "Gruplar": "Groups",
    "Dışa aktar": "Export", "Yayınla": "Publish",
    "Çizgiler çalışma sırasını gösterir. Düğümün solu giriş, sağı çıkış. Alan eşleme için düğüme tıkla.":
        "Lines show execution order. Left of a node is input, right is output. Click a node to map its fields.",
    "Admin ekranı önizlemesi, otomatik oluşur": "Admin screen preview, generated automatically",
    "Devam et": "Continue",
    "Alanlarını görmek için tuvalde bir düğüme tıkla.": "Click a node on the canvas to see its fields.",
    "Form": "Form", "Sonuç": "Result",
    "Admine sorulan alanlar": "Fields asked to the admin",
    "Admine gösterilir": "Shown to the admin",
    "Admine sorulan alanlar. Atomlarda 'formda sor' seçtikçe dolar.":
        "Fields asked to the admin. Filled as you choose 'ask in form' on atoms.",
    "Molekül bitince admine gösterilecek özet.": "Summary shown to the admin when the molecule finishes.",
    "Formda sor": "Ask in form", "Sabit değer": "Fixed value", "Önceki adımdan": "From earlier step",
    "Formdaki etiket": "Label in form", "Değer": "Value", "Kaynak": "Source",
    "Deneme çalıştırması": "Dry run",
    "Hiçbir şey değiştirilmez; adımların sırası ve geri alınabilirliği gösterilir.":
        "Nothing is changed; shows the order of steps and whether they are reversible.",
    "Kapat": "Close",
    "Bu molekül admine hiçbir şey sormuyor.": "This molecule asks the admin nothing.",
    "tuvale eklendi. Çizgiyle bağla ve alanlarını ayarla.": "added to the canvas. Connect it and map its fields.",
    "yayınlandı. Admin ekranında görünür.": "published. It is now visible on the admin screen.",
    "Adsız molekül": "Untitled molecule",
    # admin
    "İşlemler": "Actions", "Grup": "Group", "Yeni molekül iste": "Request a molecule",
    "Bu gruba açılmış yayında molekül yok.": "No published molecule is open to this group.",
    "Kayıt": "Log", "Geri al": "Undo", "geri alındı": "undone",
    "Vazgeç": "Cancel", "Geri": "Back", "Uygula": "Apply",
    "Şunlar yapılacak": "This will be done",
    "Eksik alan": "Missing field", "uygulandı.": "applied.",
    "Çalıştırma geri alındı.": "Run undone.",
    "Yapmak istediğin işi anlat": "Describe what you want to do",
    "Gönder": "Send", "Talebin tasarımcıya iletildi.": "Your request was sent to the designer.",
    "şimdi": "now",
    # elementler
    "E-posta": "Email", "Ses kayıt": "Recording",
    "Sinyal ve medya. Çıkarılamaz.": "Signalling and media. Cannot be removed.",
    "E-posta gönderimi.": "Sending email.",
    "Çağrı kayıtlarının saklanması ve dinlenmesi.": "Storing and playing call recordings.",
    "Müşteri kayıtlarına erişim.": "Access to customer records.",
    "Yazıya dökme ve özetleme.": "Transcription and summarisation.",
    # atomlar
    "Dahili oluştur": "Create extension", "Dahilileri listele": "List extensions",
    "Sesli mesaj kutusu aç": "Set up voicemail box", "Kuyrukları listele": "List queues",
    "Kuyruğa üye ekle": "Add queue member", "Mesai takvimi ayarla": "Set schedule",
    "Gelen yönlendirme ayarla": "Set inbound route", "Cihaz durumu getir": "Get device status",
    "Ayarları yeniden yükle": "Reload configuration", "E-posta gönder": "Send email",
    # alanlar
    "Dahili numara": "Extension number", "Görünen ad": "Display name", "Ses kodeği": "Audio codec",
    "Azami cihaz sayısı": "Max devices", "Dahili": "Extension", "Dahililer": "Extensions",
    "PIN": "PIN", "Bildirim e-postası": "Notification email", "Sesli mesaj kutusu": "Voicemail box",
    "Kuyruklar": "Queues", "Kuyruk": "Queue", "Üye": "Member", "Öncelik": "Priority", "Üyelik": "Membership",
    "Takvim adı": "Schedule name", "Açılış saati": "Opening time", "Kapanış saati": "Closing time",
    "Günler": "Days", "Takvim": "Schedule", "Dış numara": "External number",
    "Mesai içi hedef": "Open-hours target", "Mesai dışı hedef": "Closed-hours target",
    "Yönlendirme": "Route", "Durum": "Status", "Modül": "Module", "Alıcı": "Recipient",
    "Şablon": "Template", "İleti kimliği": "Message ID",
    "metin": "text", "sayı": "number", "seçim": "choice", "liste": "list",
}


def lang() -> str:
    return app.storage.user.get("lang", "tr")


def t(text: str) -> str:
    return EN.get(text, text) if lang() == "en" else text
