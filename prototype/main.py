"""Arayüz prototipi: üç profil, sahte veri. Atılabilir kod; gerçek sisteme bağlı değildir.

Çalıştırma:  python3 main.py   ->  http://localhost:8090
"""
import json

from nicegui import app, ui

import data
from i18n import lang, t

PROFILES = [("/mimar", "Mimar"), ("/tasarimci", "Tasarımcı"), ("/admin", "Admin")]
SOURCES = ["form", "const", "step"]
SOURCE_LABELS = {"form": "Formda sor", "const": "Sabit değer", "step": "Önceki adımdan"}

HEAD = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/drawflow@0.0.59/dist/drawflow.min.css">
<script src="https://cdn.jsdelivr.net/npm/drawflow@0.0.59/dist/drawflow.min.js"></script>
<style>
  :root { --bg:#ffffff; --fg:#111111; --muted:#6b6b6b; --line:#e5e5e5; --soft:#f6f5f0; --canvas:#fafafa;
          --dot:#dcdcdc; --nodeline:#cfcfcf; --tag:#f1efe8; --tagfg:#444441;
          --warn:#faeeda; --warnfg:#633806; --ok:#eaf3de; --okfg:#27500a; }
  body.body--dark { --bg:#1b1b19; --fg:#ecece8; --muted:#a3a39b; --line:#3a3a36; --soft:#262623;
          --canvas:#212120; --dot:#3a3a36; --nodeline:#4c4c47; --tag:#33332f; --tagfg:#d3d1c7;
          --warn:#412402; --warnfg:#fac775; --ok:#173404; --okfg:#c0dd97; }
  body, .q-page, .q-layout { background:var(--bg) !important; color:var(--fg); }
  .q-header { background:var(--bg) !important; color:var(--fg) !important; border-bottom:1px solid var(--line); }
  .q-card { background:var(--bg) !important; color:var(--fg) !important; border:1px solid var(--line); box-shadow:none !important; }
  .nav { color:var(--muted); text-decoration:none; font-size:14px; padding:4px 10px; border-radius:8px; }
  .nav.on { color:var(--fg); font-weight:500; background:var(--tag); }
  .muted { color:var(--muted); }
  .box { border:1px solid var(--line); border-radius:12px; background:var(--bg); }
  .soft { background:var(--soft); border-radius:12px; }
  .tile { border:1px solid var(--line); border-radius:10px; padding:12px; width:132px; cursor:pointer; }
  .tile.off { opacity:.4; cursor:default; }
  .tile.on { border:2px solid var(--fg); }
  .sym { font-size:26px; font-weight:500; line-height:1.1; }
  .item { border:1px solid var(--line); border-radius:8px; padding:8px 12px; cursor:pointer; }
  .item:hover { background:var(--soft); }
  .item.on { border:2px solid var(--fg); }
  .tag { font-size:12px; padding:2px 8px; border-radius:6px; background:var(--tag); color:var(--tagfg); }
  .tag.warn { background:var(--warn); color:var(--warnfg); }
  .tag.ok { background:var(--ok); color:var(--okfg); }
  .q-btn.btn-primary { background:var(--fg) !important; color:var(--bg) !important; }
  .q-btn.btn-secondary { color:var(--fg) !important; }
  #drawflow { width:100%; height:420px; background:var(--canvas); border:1px solid var(--line); border-radius:12px;
              background-image:radial-gradient(var(--dot) 1px, transparent 1px); background-size:20px 20px; }
  .drawflow .drawflow-node { background:var(--bg); border:1px solid var(--nodeline); border-radius:8px; width:190px;
              padding:10px 12px; color:var(--fg); box-shadow:none; }
  .drawflow .drawflow-node.selected { background:var(--bg); border:2px solid #378ADD; box-shadow:none; }
  .drawflow .drawflow-node.form, .drawflow .drawflow-node.result { background:var(--soft); width:140px; }
  .drawflow .drawflow-node .input, .drawflow .drawflow-node .output { width:12px; height:12px;
              border:1px solid #888; background:var(--bg); }
  .drawflow .connection .main-path { stroke:#888; stroke-width:2px; }
  body.body--dark .q-field--outlined .q-field__control:before { border-color:var(--nodeline); }
  body.body--dark .q-field__native, body.body--dark .q-field__label, body.body--dark .q-field__marginal,
  body.body--dark .q-item, body.body--dark .q-item__label, body.body--dark .q-icon { color:var(--fg); }
  body.body--dark .q-menu { background:var(--soft); color:var(--fg); }
  .nt { font-size:13px; font-weight:500; }
  .ns { font-size:11px; color:var(--muted); font-family:monospace; }
  .nio { font-size:11px; color:var(--muted); margin-top:6px; line-height:1.4; }
</style>
<script>
  window.dfMap = {};
  window.dfAdd = function (n) {
    dfMap[n.nid] = editor.addNode(n.kind, n.inputs, n.outputs, n.x, n.y, n.kind, {nid: n.nid}, n.html);
  };
  window.dfLoad = function (mol) {
    if (typeof Drawflow === 'undefined') { setTimeout(() => dfLoad(mol), 150); return; }
    const el = document.getElementById('drawflow');
    if (!el) return;
    if (!window.editor || window.editor.container !== el) {
      window.editor = new Drawflow(el);
      editor.start();
      editor.on('nodeSelected', id => emitEvent('df_select', {id: editor.getNodeFromId(id).data.nid}));
      editor.on('nodeUnselected', () => emitEvent('df_select', {id: null}));
    }
    editor.clearModuleSelected();
    dfMap = {};
    mol.nodes.forEach(dfAdd);
    mol.edges.forEach(e => editor.addConnection(dfMap[e[0]], dfMap[e[1]], 'output_1', 'input_1'));
    const z = mol.nodes.length > 4 ? 0.6 : 0.9;
    editor.zoom = z; editor.zoom_last_value = z;
    editor.canvas_x = -(1 - z) * el.clientWidth / 2;
    editor.canvas_y = -(1 - z) * el.clientHeight / 2;
    editor.precanvas.style.transform = `translate(${editor.canvas_x}px, ${editor.canvas_y}px) scale(${z})`;
  };
</script>
"""


def frame(active: str) -> None:
    """Üst çubuk: profil geçişi, tema ve dil düğmeleri. Tercihler kullanıcı başına saklanır."""
    ui.add_head_html(HEAD)
    dark = ui.dark_mode(value=app.storage.user.get("dark", False))

    def toggle_dark():
        dark.value = not dark.value
        app.storage.user["dark"] = dark.value

    def toggle_lang():
        app.storage.user["lang"] = "tr" if lang() == "en" else "en"
        ui.navigate.reload()

    with ui.header().classes("items-center"):
        ui.label("atomic-shell").classes("text-base font-medium")
        ui.label(t("prototip, sahte veri")).classes("muted text-xs")
        ui.space()
        for path, label in PROFILES:
            ui.link(t(label), path).classes("nav on" if path == active else "nav")
        ui.button(icon="contrast", on_click=toggle_dark, color=None).props("flat round dense").classes(
            "btn-secondary").tooltip(t("Koyu / açık tema"))
        ui.button("EN" if lang() == "tr" else "TR", on_click=toggle_lang, color=None).props(
            "outline dense no-caps").classes("btn-secondary").tooltip(t("Dil"))


def primary(text, on_click):
    return ui.button(t(text), on_click=on_click, color=None).props("unelevated no-caps").classes("btn-primary")


def secondary(text, on_click):
    return ui.button(t(text), on_click=on_click, color=None).props("outline no-caps").classes("btn-secondary")


def status_tag(status):
    ui.label(t(status)).classes("tag ok" if status == "Yayında" else "tag warn")


# ----------------------------------------------------------------------------- Mimar

@ui.page("/mimar")
def mimar_page():
    frame("/mimar")
    state = {"element": "asterisk", "atom": None, "envelope": None}

    def pick_element(name):
        state.update(element=name, atom=None, envelope=None)
        table.refresh(); atoms.refresh(); detail.refresh()

    def pick_atom(name):
        state.update(atom=name, envelope=None)
        atoms.refresh(); detail.refresh()

    def try_atom():
        a = data.atom(state["atom"])
        state["envelope"] = {
            "ok": True, "run_id": "deneme-0001",
            "data": {o["key"]: f"<{t(o['title'])}>" for o in a["outputs"]},
            "changes": [{"resource": a["name"].rsplit(".", 1)[0], "before": None, "after": "…"}] if a["writes"] else [],
            "error": None,
        }
        detail.refresh()

    with ui.column().classes("w-full max-w-5xl mx-auto gap-4 p-4"):
        ui.label(t("Periyodik tablo")).classes("text-lg font-medium")
        ui.label(t("Kurulu elementler ve sundukları atomlar. Soluk kutular kurulu değil.")).classes("muted text-sm")

        @ui.refreshable
        def table():
            with ui.row().classes("gap-3"):
                for el in data.ELEMENTS:
                    count = sum(1 for a in data.ATOMS if data.element_of(a["name"]) == el["name"])
                    cls = "tile" + ("" if el["installed"] else " off") + (" on" if el["name"] == state["element"] else "")
                    with ui.element("div").classes(cls) as tile:
                        ui.label(el["symbol"]).classes("sym")
                        ui.label(t(el["title"])).classes("text-sm font-medium")
                        ui.label(f"{count} {t('atom')}" if el["installed"] else t("kurulu değil")).classes("muted text-xs")
                    if el["installed"]:
                        tile.on("click", lambda _, n=el["name"]: pick_element(n))
        table()

        with ui.row().classes("w-full gap-4 no-wrap items-start"):
            with ui.column().classes("gap-2").style("width:340px"):
                @ui.refreshable
                def atoms():
                    ui.label(t("Atomlar")).classes("muted text-xs")
                    for a in data.ATOMS:
                        if data.element_of(a["name"]) != state["element"]:
                            continue
                        cls = "item w-full" + (" on" if a["name"] == state["atom"] else "")
                        with ui.element("div").classes(cls).on("click", lambda _, n=a["name"]: pick_atom(n)):
                            ui.label(t(a["title"])).classes("text-sm font-medium")
                            ui.label(a["name"]).classes("muted text-xs").style("font-family:monospace")
                atoms()

            with ui.column().classes("box p-4 gap-3").style("flex:1"):
                @ui.refreshable
                def detail():
                    if not state["atom"]:
                        ui.label(t("Ayrıntısını görmek için bir atom seç.")).classes("muted text-sm")
                        return
                    a = data.atom(state["atom"])
                    ui.label(t(a["title"])).classes("text-base font-medium")
                    ui.label(a["name"]).classes("muted text-xs").style("font-family:monospace")
                    with ui.row().classes("gap-2"):
                        ui.label(t("yazar") if a["writes"] else t("okur")).classes("tag")
                        if a["writes"]:
                            ui.label(t("geri alınabilir") if a["reversible"] else t("geri alınamaz")).classes(
                                "tag ok" if a["reversible"] else "tag warn")
                    ui.label(t("Girdi")).classes("muted text-xs")
                    if not a["inputs"]:
                        ui.label(t("Girdi almaz.")).classes("text-sm")
                    for f in a["inputs"]:
                        ui.label(f"{t(f['title'])}  ·  {f['key']}  ·  {t(f['type'])}").classes("text-sm")
                    ui.label(t("Çıktı")).classes("muted text-xs")
                    for f in a["outputs"]:
                        ui.label(f"{t(f['title'])}  ·  {f['key']}  ·  {t(f['type'])}").classes("text-sm")
                    secondary("Dene", try_atom)
                    if state["envelope"]:
                        ui.label(t("Zarf (sahte cevap)")).classes("muted text-xs")
                        ui.code(json.dumps(state["envelope"], ensure_ascii=False, indent=2), language="json").classes("w-full")
                detail()


# ----------------------------------------------------------------------------- Tasarımcı

def node_payload(n):
    if n["type"] == "form":
        return {"nid": n["id"], "kind": "form", "inputs": 0, "outputs": 1, "x": n["x"], "y": n["y"],
                "html": f'<div class="nt">{t("Form")}</div><div class="nio">{t("Admine sorulan alanlar")}</div>'}
    if n["type"] == "result":
        return {"nid": n["id"], "kind": "result", "inputs": 1, "outputs": 0, "x": n["x"], "y": n["y"],
                "html": f'<div class="nt">{t("Sonuç")}</div><div class="nio">{t("Admine gösterilir")}</div>'}
    a = data.atom(n["atom"])
    ins = ", ".join(t(f["title"]) for f in a["inputs"]) or t("yok")
    outs = ", ".join(t(f["title"]) for f in a["outputs"]) or t("yok")
    html = (f'<div class="nt">{t(a["title"])}</div><div class="ns">{a["name"]}</div>'
            f'<div class="nio">{t("Girdi")}: {ins}<br>{t("Çıktı")}: {outs}</div>')
    return {"nid": n["id"], "kind": "atom", "inputs": 1, "outputs": 1, "x": n["x"], "y": n["y"], "html": html}


def canvas_payload(mol):
    return {"nodes": [node_payload(n) for n in mol["nodes"]], "edges": [list(e) for e in mol["edges"]]}


def render_form(mol, values=None):
    """Molekülün 'formda sor' alanlarından admin formunu çizer. Etiketler DNA'dır, çevrilmez."""
    values = values if values is not None else {}
    fields = data.form_fields(mol)
    if not fields:
        ui.label(t("Bu molekül admine hiçbir şey sormuyor.")).classes("muted text-sm")
    for f in fields:
        if f["type"] == "seçim":
            ui.select(data.REFS.get(f["ref"], []), label=f["label"]).props("outlined dense").classes(
                "w-full").bind_value(values, f["label"])
        else:
            ui.input(f["label"], placeholder=f["placeholder"]).props("outlined dense").classes(
                "w-full").bind_value(values, f["label"])
    return fields


@ui.page("/tasarimci")
def tasarimci_page():
    frame("/tasarimci")
    state = {"mol": data.MOLECULES[0]["id"], "node": None}

    def mol():
        return data.molecule(state["mol"])

    def load_canvas():
        ui.run_javascript(f"dfLoad({json.dumps(canvas_payload(mol()), ensure_ascii=False)})")

    def pick_molecule(mol_id):
        state.update(mol=mol_id, node=None)
        mols.refresh(); bar.refresh(); panel.refresh(); preview.refresh()
        load_canvas()

    def select_node(nid):
        state["node"] = nid
        panel.refresh()

    ui.on("df_select", lambda e: select_node(e.args["id"]))

    def add_atom(name):
        m = mol()
        nid = max(n["id"] for n in m["nodes"]) + 1
        a = data.atom(name)
        node = {"id": nid, "type": "atom", "atom": name, "x": 120 + 40 * (nid % 5), "y": 290,
                "bindings": {f["key"]: {"source": "form", "label": t(f["title"])} for f in a["inputs"]}}
        m["nodes"].append(node)
        m["status"] = "Taslak"
        ui.run_javascript(f"dfAdd({json.dumps(node_payload(node), ensure_ascii=False)})")
        bar.refresh(); preview.refresh()
        ui.notify(f"{t(a['title'])}: {t('tuvale eklendi. Çizgiyle bağla ve alanlarını ayarla.')}")

    def new_molecule():
        mol_id = f"molekul_{len(data.MOLECULES) + 1}"
        data.MOLECULES.append({
            "id": mol_id, "title": t("Adsız molekül"), "status": "Taslak", "version": 1, "groups": ["Santral"],
            "description": "", "edges": [],
            "nodes": [{"id": 1, "type": "form", "title": "Form", "x": 20, "y": 120},
                      {"id": 2, "type": "result", "title": "Sonuç", "x": 520, "y": 120}]})
        pick_molecule(mol_id)

    def publish():
        m = mol()
        if m["status"] == "Taslak":
            m["version"] += 1
        m["status"] = "Yayında"
        bar.refresh(); mols.refresh()
        ui.notify(f"{m['title']}: {t('yayınlandı. Admin ekranında görünür.')}")

    def export():
        m = mol()
        ui.download.content(json.dumps(m, ensure_ascii=False, indent=2), f"{m['id']}.molekul.json")

    def dry_run():
        m = mol()
        with ui.dialog() as dlg, ui.card().style("min-width:420px"):
            ui.label(t("Deneme çalıştırması")).classes("text-base font-medium")
            ui.label(t("Hiçbir şey değiştirilmez; adımların sırası ve geri alınabilirliği gösterilir.")).classes("muted text-sm")
            for i, n in enumerate([n for n in m["nodes"] if n["type"] == "atom"], 1):
                a = data.atom(n["atom"])
                with ui.row().classes("items-center gap-2"):
                    ui.label(f"{i}. {t(a['title'])}").classes("text-sm")
                    if not a["reversible"]:
                        ui.label(t("geri alınamaz")).classes("tag warn")
            secondary("Kapat", dlg.close)
        dlg.open()

    def set_binding(node, key, **changes):
        node["bindings"][key] = {**node["bindings"].get(key, {}), **changes}
        mol()["status"] = "Taslak"
        bar.refresh(); preview.refresh()

    def change_source(node, key, source, spec):
        node["bindings"][key] = {"source": source, **({"label": t(spec["title"])} if source == "form" else {})}
        mol()["status"] = "Taslak"
        bar.refresh(); panel.refresh(); preview.refresh()

    with ui.row().classes("w-full gap-4 no-wrap items-start p-4"):
        # Sol: moleküller ve atom paleti
        with ui.column().classes("gap-2").style("width:210px"):
            @ui.refreshable
            def mols():
                ui.label(t("Moleküller")).classes("muted text-xs")
                for m in data.MOLECULES:
                    cls = "item w-full" + (" on" if m["id"] == state["mol"] else "")
                    with ui.element("div").classes(cls).on("click", lambda _, i=m["id"]: pick_molecule(i)):
                        ui.label(m["title"]).classes("text-sm font-medium")
                        ui.label(f"{t(m['status'])} · {t('sürüm')} {m['version']}").classes("muted text-xs")
            mols()
            secondary("Yeni molekül", new_molecule).classes("w-full")

            ui.label(t("Atomlar")).classes("muted text-xs q-mt-md")
            for el in data.ELEMENTS:
                if not el["installed"]:
                    continue
                with ui.expansion(f"{el['symbol']}  {t(el['title'])}", value=el["required"]).classes("w-full box").props("dense"):
                    for a in data.ATOMS:
                        if data.element_of(a["name"]) == el["name"]:
                            ui.label(t(a["title"])).classes("text-sm item w-full").on(
                                "click", lambda _, n=a["name"]: add_atom(n))

        # Orta: başlık çubuğu, tuval, form önizlemesi
        with ui.column().classes("gap-3").style("flex:1;min-width:0"):
            @ui.refreshable
            def bar():
                m = mol()
                with ui.row().classes("w-full items-center gap-3"):
                    ui.input(value=m["title"], on_change=lambda e: (m.update(title=e.value), mols.refresh())).props(
                        "dense borderless").classes("text-base font-medium").style("width:260px")
                    status_tag(m["status"])
                    ui.label(f"{t('Gruplar')}: " + ", ".join(m["groups"])).classes("muted text-xs")
                    ui.space()
                    secondary("Dışa aktar", export)
                    secondary("Dene", dry_run)
                    primary("Yayınla", publish)
            bar()

            ui.html('<div id="drawflow"></div>', sanitize=False).classes("w-full")
            ui.label(t("Çizgiler çalışma sırasını gösterir. Düğümün solu giriş, sağı çıkış. "
                       "Alan eşleme için düğüme tıkla.")).classes("muted text-xs")

            with ui.column().classes("w-full p-4 gap-2 soft"):
                ui.label(t("Admin ekranı önizlemesi, otomatik oluşur")).classes("muted text-xs")
                with ui.column().classes("box p-4 gap-2").style("width:360px"):
                    @ui.refreshable
                    def preview():
                        ui.label(mol()["title"]).classes("text-sm font-medium")
                        render_form(mol())
                        secondary("Devam et", lambda: None)
                    preview()

        # Sağ: seçili düğümün alanları
        with ui.column().classes("box p-4 gap-2").style("width:290px"):
            @ui.refreshable
            def panel():
                m = mol()
                node = next((n for n in m["nodes"] if n["id"] == state["node"]), None)
                if node is None:
                    ui.label(t("Alanlarını görmek için tuvalde bir düğüme tıkla.")).classes("muted text-sm")
                    return
                if node["type"] == "form":
                    ui.label(t("Form")).classes("text-sm font-medium")
                    ui.label(t("Admine sorulan alanlar. Atomlarda 'formda sor' seçtikçe dolar.")).classes("muted text-xs")
                    for f in data.form_fields(m):
                        ui.label(f["label"]).classes("text-sm")
                    return
                if node["type"] == "result":
                    ui.label(t("Sonuç")).classes("text-sm font-medium")
                    ui.label(t("Molekül bitince admine gösterilecek özet.")).classes("muted text-xs")
                    return
                a = data.atom(node["atom"])
                ui.label(t(a["title"])).classes("text-sm font-medium")
                ui.label(a["name"]).classes("muted text-xs").style("font-family:monospace")
                sources = {s: t(SOURCE_LABELS[s]) for s in SOURCES}
                earlier = {f"{n['id']}:{o['key']}": f"{t(data.atom(n['atom'])['title'])} › {t(o['title'])}"
                           for n in m["nodes"] if n["type"] == "atom" and n["id"] != node["id"]
                           for o in data.atom(n["atom"])["outputs"]}
                for spec in a["inputs"]:
                    key = spec["key"]
                    b = node["bindings"].setdefault(key, {"source": "form", "label": t(spec["title"])})
                    ui.label(t(spec["title"])).classes("text-sm font-medium q-mt-sm")
                    ui.select(sources, value=b["source"],
                              on_change=lambda e, k=key, s=spec: change_source(node, k, e.value, s)
                              ).props("outlined dense").classes("w-full")
                    if b["source"] == "form":
                        ui.input(t("Formdaki etiket"), value=b.get("label", ""),
                                 on_change=lambda e, k=key: set_binding(node, k, label=e.value)
                                 ).props("outlined dense").classes("w-full")
                    elif b["source"] == "const":
                        ui.input(t("Değer"), value=b.get("value", ""),
                                 on_change=lambda e, k=key: set_binding(node, k, value=e.value)
                                 ).props("outlined dense").classes("w-full")
                    else:
                        current = f"{b.get('node')}:{b.get('output')}"
                        ui.select(earlier, value=current if current in earlier else None, label=t("Kaynak"),
                                  on_change=lambda e, k=key: set_binding(
                                      node, k, node=int(e.value.split(":")[0]), output=e.value.split(":")[1])
                                  ).props("outlined dense").classes("w-full")
            panel()

    ui.timer(0.3, load_canvas, once=True)


# ----------------------------------------------------------------------------- Admin

@ui.page("/admin")
def admin_page():
    frame("/admin")
    state = {"group": "Santral"}

    def run_molecule(m):
        values = {}
        with ui.dialog() as dlg, ui.card().style("min-width:400px"):
            @ui.refreshable
            def body(step="form"):
                ui.label(m["title"]).classes("text-base font-medium")
                if step == "form":
                    fields = render_form(m, values)

                    def next_step():
                        missing = [f["label"] for f in fields if not values.get(f["label"])]
                        if missing:
                            ui.notify(f"{t('Eksik alan')}: " + ", ".join(missing), type="warning")
                            return
                        body.refresh("plan")
                    with ui.row().classes("gap-2"):
                        primary("Devam et", next_step)
                        secondary("Vazgeç", dlg.close)
                else:
                    ui.label(t("Şunlar yapılacak")).classes("muted text-xs")
                    for i, n in enumerate([n for n in m["nodes"] if n["type"] == "atom"], 1):
                        a = data.atom(n["atom"])
                        with ui.row().classes("items-center gap-2"):
                            ui.label(f"{i}. {t(a['title'])}").classes("text-sm")
                            if not a["reversible"]:
                                ui.label(t("geri alınamaz")).classes("tag warn")

                    def apply():
                        data.RUNS.insert(0, {
                            "id": len(data.RUNS) + 1, "molecule": m["title"], "actor": "santral.admin",
                            "time": "şimdi", "summary": ", ".join(str(v) for v in values.values()),
                            "undone": False})
                        dlg.close(); runs.refresh()
                        ui.notify(f"{m['title']}: {t('uygulandı.')}", type="positive")
                    with ui.row().classes("gap-2"):
                        primary("Uygula", apply)
                        secondary("Geri", lambda: body.refresh("form"))
            body()
        dlg.open()

    def request_molecule():
        with ui.dialog() as dlg, ui.card().style("min-width:400px"):
            ui.label(t("Yeni molekül iste")).classes("text-base font-medium")
            ui.textarea(placeholder=t("Yapmak istediğin işi anlat")).props("outlined").classes("w-full")
            with ui.row().classes("gap-2"):
                primary("Gönder", lambda: (dlg.close(), ui.notify(t("Talebin tasarımcıya iletildi."))))
                secondary("Vazgeç", dlg.close)
        dlg.open()

    def undo(run):
        run["undone"] = True
        runs.refresh()
        ui.notify(t("Çalıştırma geri alındı."))

    with ui.column().classes("w-full max-w-4xl mx-auto gap-4 p-4"):
        with ui.row().classes("w-full items-center"):
            ui.label(t("İşlemler")).classes("text-lg font-medium")
            ui.space()
            ui.select(["İK", "Santral"], value=state["group"], label=t("Grup"),
                      on_change=lambda e: (state.update(group=e.value), cards.refresh())
                      ).props("outlined dense").style("width:140px")
            secondary("Yeni molekül iste", request_molecule)

        @ui.refreshable
        def cards():
            visible = [m for m in data.MOLECULES if m["status"] == "Yayında" and state["group"] in m["groups"]]
            if not visible:
                ui.label(t("Bu gruba açılmış yayında molekül yok.")).classes("muted text-sm")
            with ui.row().classes("gap-3"):
                for m in visible:
                    with ui.element("div").classes("box p-4").style("width:280px;cursor:pointer").on(
                            "click", lambda _, mm=m: run_molecule(mm)):
                        ui.label(m["title"]).classes("text-sm font-medium")
                        ui.label(m["description"]).classes("muted text-xs")
        cards()

        ui.label(t("Kayıt")).classes("text-lg font-medium q-mt-md")

        @ui.refreshable
        def runs():
            for r in data.RUNS:
                with ui.row().classes("w-full items-center box p-3 gap-3"):
                    ui.label(t(r["time"])).classes("muted text-xs").style("width:48px")
                    ui.label(r["molecule"]).classes("text-sm font-medium").style("width:170px")
                    ui.label(r["summary"]).classes("text-sm").style("flex:1")
                    ui.label(r["actor"]).classes("muted text-xs")
                    if r["undone"]:
                        ui.label(t("geri alındı")).classes("tag")
                    else:
                        secondary("Geri al", lambda _, rr=r: undo(rr)).props("dense")
        runs()


@ui.page("/")
def index():
    ui.navigate.to("/admin")


ui.run(port=8090, title="atomic-shell prototip", reload=False, show=False,
       storage_secret="prototip-yalnizca-yerel")
