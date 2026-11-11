"""Arayüzün görünümü: renkler ve ortak sınıflar.

Bütün renkler aşağıdaki değişkenlerden gelir; koyu tema yalnızca bu değişkenleri
değiştirir. Ekran kodunda renk yazılmaz.
"""
from nicegui import app, ui

LIGHT = "--bg:#ffffff; --fg:#111111; --muted:#6b6b6b; --line:#e5e5e5; --soft:#f6f5f0; --tag:#f1efe8; --tagfg:#444441; --warn:#faeeda; --warnfg:#633806; --ok:#eaf3de; --okfg:#27500a; --bad:#fcebeb; --badfg:#791f1f;"
DARK = "--bg:#1b1b19; --fg:#ecece8; --muted:#a3a39b; --line:#3a3a36; --soft:#262623; --tag:#33332f; --tagfg:#d3d1c7; --warn:#412402; --warnfg:#fac775; --ok:#173404; --okfg:#c0dd97; --bad:#501313; --badfg:#f7c1c1;"

STYLE = """
<style>
  :root { """ + LIGHT + """ }
  body.body--dark { """ + DARK + """ }
  body, .q-page, .q-layout { background:var(--bg) !important; color:var(--fg); }
  .q-header { background:var(--bg) !important; color:var(--fg) !important; border-bottom:1px solid var(--line); }
  .q-card { background:var(--bg) !important; color:var(--fg) !important; border:1px solid var(--line);
            box-shadow:none !important; }
  .nav { color:var(--muted); text-decoration:none; font-size:14px; padding:4px 10px; border-radius:8px; }
  .nav.on { color:var(--fg); font-weight:500; background:var(--tag); }
  .muted { color:var(--muted); }
  .box { border:1px solid var(--line); border-radius:12px; background:var(--bg); }
  .soft { background:var(--soft); border-radius:12px; }
  .ag-root-wrapper { border-radius:8px; }
  .tile { border:1px solid var(--line); border-radius:10px; padding:12px; width:132px; cursor:pointer; }
  .tile.on { border:2px solid var(--fg); }
  .sym { font-size:26px; font-weight:500; line-height:1.1; }
  .item { border:1px solid var(--line); border-radius:8px; padding:8px 12px; cursor:pointer; }
  .item:hover { background:var(--soft); }
  .item.on { border:2px solid var(--fg); }
  .mono { font-family:monospace; }
  .tag { font-size:12px; padding:2px 8px; border-radius:6px; background:var(--tag); color:var(--tagfg); }
  .tag.warn { background:var(--warn); color:var(--warnfg); }
  .tag.ok { background:var(--ok); color:var(--okfg); }
  .tag.bad { background:var(--bad); color:var(--badfg); }
  .q-btn.btn-primary { background:var(--fg) !important; color:var(--bg) !important; }
  .q-btn.btn-secondary { color:var(--fg) !important; }
  body.body--dark .q-field--outlined .q-field__control:before { border-color:var(--line); }
  body.body--dark .q-field__native, body.body--dark .q-field__label, body.body--dark .q-field__marginal,
  body.body--dark .q-item, body.body--dark .q-item__label, body.body--dark .q-icon,
  body.body--dark .q-radio__label, body.body--dark .q-table th, body.body--dark .q-table td { color:var(--fg); }
  body.body--dark .q-menu { background:var(--soft); color:var(--fg); }
</style>
"""

# Koyu temayı seçmiş kullanıcıda sayfa ilk çizimden itibaren koyu olsun diye eklenir.
# Bu olmadan sayfa bir an açık renkle çizilir, tema sonradan uygulanır ve ekran parlar.
DARK_FIRST = """
<style>
  :root { """ + DARK + """ }
  body.body--light { """ + LIGHT + """ }
  html { background:#1b1b19; }
</style>
"""


def apply() -> ui.dark_mode:
    """Sayfaya stilleri ekler ve kullanıcının seçtiği temayı uygular."""
    prefers_dark = app.storage.user.get("dark", False)
    ui.add_head_html(STYLE)
    if prefers_dark:
        ui.add_head_html(DARK_FIRST)
    return ui.dark_mode(value=prefers_dark)


def toggle(dark: ui.dark_mode) -> None:
    """Temayı değiştirir ve tercihi kullanıcı için saklar."""
    dark.value = not dark.value
    app.storage.user["dark"] = dark.value
