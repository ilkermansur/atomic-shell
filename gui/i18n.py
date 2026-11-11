"""Arayüz dili: Türkçe ve İngilizce.

Kaynak dil Türkçedir; EN sözlüğünde karşılığı olmayan metin Türkçe kalır.
Yalnızca kabuğun kendi metinleri çevrilir. Atom ve alan başlıkları servisten,
molekül adları tasarımcıdan geldiği dilde gösterilir.
"""
from nicegui import app

EN = {
    "Elementler": "Elements", "Moleküller": "Molecules", "Kayıt": "Log",
    "Koyu / açık tema": "Dark / light theme", "Dil": "Language",
    "Periyodik tablo": "Periodic table", "İçe aktar": "Import",
    "Henüz element yok. Bir servisin OpenAPI belgesini içe aktararak başla.":
        "No elements yet. Start by importing a service's OpenAPI document.",
    "Element içe aktar": "Import element", "Servis adresi": "Service address",
    "Erişim anahtarı (isteğe bağlı)": "API key (optional)",
    "OpenAPI dosyası (isteğe bağlı)": "OpenAPI file (optional)",
    "Dosya verilmezse belge servis adresinden okunur.":
        "If no file is given, the document is read from the service address.",
    "Vazgeç": "Cancel", "Kapat": "Close", "Elementi çıkar": "Remove element",
    "İçe aktarma sonucu": "Import result", "atom alındı": "atoms imported",
    "Anayasaya uymayan yerler": "Constitution violations",
    "Hiçbir uç anayasaya uymadığı için element takılmadı.":
        "The element was not installed because no endpoint follows the constitution.",
    "atom": "atoms", "Atomlar": "Atoms",
    "Arayüzünü görmek için bir atom seç.": "Pick an atom to see its interface.",
    "Molekül üret": "Generate molecule", "Molekül üretildi": "Molecule generated",
    "Çalıştır": "Run", "Yenile": "Refresh", "Kayıt numarası": "Record number",
    "Yapıldı": "Done", "Yapılamadı": "Failed", "Formda hata var.": "The form has errors.",
    "Süz": "Filter", "Kolonlar": "Columns", "CSV indir": "Download CSV", "kayıt": "records",
    "Henüz molekül yok. Elementler ekranında bir atom seçip molekül üret.":
        "No molecules yet. Pick an atom on the Elements screen and generate a molecule.",
    "adım": "steps", "Sil": "Delete", "Molekül bulunamadı.": "Molecule not found.",
    "Adım": "Step", "İleri": "Next", "Geri": "Back", "Uygula": "Apply",
    "Bir satır seç.": "Select a row.", "Özet": "Summary",
    "Şunlar yapılacak": "This will be done", "Seçilen kayıt": "Selected record",
    "Sonuç": "Result", "Yeniden çalıştır": "Run again", "Moleküllere dön": "Back to molecules",
    "seçildi": "selected", "yapıldı": "done", "yapılamadı": "failed", "denenmedi": "not attempted",
    "Henüz çalıştırma yok.": "No runs yet.", "tamamlandı": "completed", "yarıda kaldı": "stopped",
    "Evet": "Yes", "Hayır": "No",
}


def lang() -> str:
    return app.storage.user.get("lang", "tr")


def t(text: str) -> str:
    """Metni seçili dile çevirir."""
    return EN.get(text, text) if lang() == "en" else text
