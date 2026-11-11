"""Prototip için sahte veri. Gerçek Asterisk'e ya da veritabanına bağlı değildir."""

ELEMENTS = [
    {"name": "asterisk", "symbol": "As", "title": "Asterisk", "installed": True, "required": True,
     "description": "Sinyal ve medya. Çıkarılamaz."},
    {"name": "email", "symbol": "Ep", "title": "E-posta", "installed": True, "required": False,
     "description": "E-posta gönderimi."},
    {"name": "recording", "symbol": "Sk", "title": "Ses kayıt", "installed": False, "required": False,
     "description": "Çağrı kayıtlarının saklanması ve dinlenmesi."},
    {"name": "crm", "symbol": "Cr", "title": "CRM", "installed": False, "required": False,
     "description": "Müşteri kayıtlarına erişim."},
    {"name": "ai", "symbol": "Ai", "title": "AI", "installed": False, "required": False,
     "description": "Yazıya dökme ve özetleme."},
]


def _f(key, title, type_="metin", ref=None):
    return {"key": key, "title": title, "type": type_, "ref": ref}


ATOMS = [
    {"name": "asterisk.extension.create", "title": "Dahili oluştur", "writes": True, "reversible": True,
     "inputs": [_f("number", "Dahili numara"), _f("display_name", "Görünen ad"),
                _f("codec", "Ses kodeği"), _f("max_contacts", "Azami cihaz sayısı", "sayı")],
     "outputs": [_f("extension", "Dahili")]},
    {"name": "asterisk.extension.list", "title": "Dahilileri listele", "writes": False, "reversible": True,
     "inputs": [], "outputs": [_f("extensions", "Dahililer", "liste")]},
    {"name": "asterisk.voicemail.set", "title": "Sesli mesaj kutusu aç", "writes": True, "reversible": True,
     "inputs": [_f("extension", "Dahili"), _f("pin", "PIN"), _f("notify_email", "Bildirim e-postası")],
     "outputs": [_f("mailbox", "Sesli mesaj kutusu")]},
    {"name": "asterisk.queue.list", "title": "Kuyrukları listele", "writes": False, "reversible": True,
     "inputs": [], "outputs": [_f("queues", "Kuyruklar", "liste")]},
    {"name": "asterisk.queue_member.add", "title": "Kuyruğa üye ekle", "writes": True, "reversible": True,
     "inputs": [_f("queue", "Kuyruk", "seçim", ref="queues"), _f("member", "Üye"),
                _f("priority", "Öncelik", "sayı")],
     "outputs": [_f("membership", "Üyelik")]},
    {"name": "asterisk.schedule.set", "title": "Mesai takvimi ayarla", "writes": True, "reversible": True,
     "inputs": [_f("name", "Takvim adı"), _f("opens", "Açılış saati"), _f("closes", "Kapanış saati"),
                _f("days", "Günler")],
     "outputs": [_f("schedule", "Takvim")]},
    {"name": "asterisk.inbound_route.set", "title": "Gelen yönlendirme ayarla", "writes": True, "reversible": True,
     "inputs": [_f("did", "Dış numara"), _f("schedule", "Takvim"),
                _f("open_target", "Mesai içi hedef", "seçim", ref="queues"),
                _f("closed_target", "Mesai dışı hedef", "seçim", ref="closed_targets")],
     "outputs": [_f("route", "Yönlendirme")]},
    {"name": "asterisk.device.status", "title": "Cihaz durumu getir", "writes": False, "reversible": True,
     "inputs": [_f("extension", "Dahili")], "outputs": [_f("status", "Durum")]},
    {"name": "asterisk.system.reload", "title": "Ayarları yeniden yükle", "writes": True, "reversible": False,
     "inputs": [_f("module", "Modül")], "outputs": [_f("result", "Sonuç")]},
    {"name": "email.message.send", "title": "E-posta gönder", "writes": True, "reversible": False,
     "inputs": [_f("to", "Alıcı"), _f("template", "Şablon")],
     "outputs": [_f("message_id", "İleti kimliği")]},
]

# "seçim" tipindeki alanların sahte seçenekleri
REFS = {
    "queues": ["Satış", "Destek", "Muhasebe"],
    "closed_targets": ["Sesli mesaj", "Nöbetçi cep telefonu", "Kapalı anonsu"],
}


def atom(name):
    return next(a for a in ATOMS if a["name"] == name)


def element_of(atom_name):
    return atom_name.split(".")[0]


def _form(**kw):
    return {"source": "form", **kw}


def _const(value):
    return {"source": "const", "value": value}


def _step(node, output):
    return {"source": "step", "node": node, "output": output}


# Molekül = düğümler + bağlantılar + alan eşlemeleri
MOLECULES = [
    {
        "id": "yeni_personel", "title": "Yeni personel", "status": "Yayında", "version": 2,
        "groups": ["İK", "Santral"],
        "description": "Dahili açar, sesli mesaj kutusu kurar, kuyruğa ekler, hoş geldin e-postası atar.",
        "nodes": [
            {"id": 1, "type": "form", "title": "Form", "x": 20, "y": 120},
            {"id": 2, "type": "atom", "atom": "asterisk.extension.create", "x": 220, "y": 120,
             "bindings": {"number": _form(label="Dahili numara", placeholder="1042"),
                          "display_name": _form(label="Ad soyad", placeholder="Ayşe Yılmaz"),
                          "codec": _const("g722"), "max_contacts": _const("2")}},
            {"id": 3, "type": "atom", "atom": "asterisk.voicemail.set", "x": 470, "y": 120,
             "bindings": {"extension": _step(2, "extension"), "pin": _const("rastgele"),
                          "notify_email": _form(label="E-posta", placeholder="ayse@kurum.example")}},
            {"id": 4, "type": "atom", "atom": "asterisk.queue_member.add", "x": 720, "y": 120,
             "bindings": {"queue": _form(label="Birim"), "member": _step(2, "extension"),
                          "priority": _const("1")}},
            {"id": 5, "type": "atom", "atom": "email.message.send", "x": 970, "y": 120,
             "bindings": {"to": _form(label="E-posta", placeholder="ayse@kurum.example"),
                          "template": _const("hos_geldin")}},
            {"id": 6, "type": "result", "title": "Sonuç", "x": 1220, "y": 120},
        ],
        "edges": [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6)],
    },
    {
        "id": "mesai_disi", "title": "Mesai dışı yönlendirme", "status": "Taslak", "version": 1,
        "groups": ["Santral"],
        "description": "Bir dış numaranın mesai saatlerini ve mesai dışı hedefini ayarlar.",
        "nodes": [
            {"id": 1, "type": "form", "title": "Form", "x": 20, "y": 120},
            {"id": 2, "type": "atom", "atom": "asterisk.schedule.set", "x": 220, "y": 120,
             "bindings": {"name": _const("genel_mesai"),
                          "opens": _form(label="Açılış saati", placeholder="09:00"),
                          "closes": _form(label="Kapanış saati", placeholder="18:00"),
                          "days": _const("hafta içi")}},
            {"id": 3, "type": "atom", "atom": "asterisk.inbound_route.set", "x": 470, "y": 120,
             "bindings": {"did": _form(label="Dış numara", placeholder="0212 555 00 00"),
                          "schedule": _step(2, "schedule"),
                          "open_target": _form(label="Mesai içinde"),
                          "closed_target": _form(label="Mesai dışında")}},
            {"id": 4, "type": "result", "title": "Sonuç", "x": 720, "y": 120},
        ],
        "edges": [(1, 2), (2, 3), (3, 4)],
    },
]

# Çalıştırma kaydı (admin ekranında dolar)
RUNS = [
    {"id": 1, "molecule": "Yeni personel", "actor": "ik.personel", "time": "10:42",
     "summary": "Mehmet Kaya, 1031, Destek", "undone": False},
]


def molecule(mol_id):
    return next(m for m in MOLECULES if m["id"] == mol_id)


def form_fields(mol):
    """Molekülün 'formda sor' alanları: admin ekranı bundan oluşur.
    Aynı etiketli alanlar tek alan olarak gösterilir."""
    fields, seen = [], set()
    for node in mol["nodes"]:
        if node["type"] != "atom":
            continue
        spec = {f["key"]: f for f in atom(node["atom"])["inputs"]}
        for key, b in node["bindings"].items():
            if b["source"] != "form":
                continue
            label = b.get("label") or spec[key]["title"]
            if label in seen:
                continue
            seen.add(label)
            fields.append({"label": label, "placeholder": b.get("placeholder", ""),
                           "type": spec[key]["type"], "ref": spec[key]["ref"]})
    return fields
