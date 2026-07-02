#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Renderer bilingvniho POVIDANI O PRAZE (CZ + EN side-by-side).
Cte data/*.json (vystup workflow) a generuje:
  index.html        - hlavni bilingvni dokument (prepinac CZ/EN/oboji)
  skripty.html      - jen souvisle mistrovske vyklady pro teren
  povidani.md       - textova verze
PDF se generuje zvlast pres Chrome headless.
Defenzivni: chybejici klice/soubory preskoci.
"""
import json, os, glob, html

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
OUT = BASE

def esc(x):
    return html.escape(str(x if x is not None else ""))

def as_list(x):
    if x is None: return []
    if isinstance(x, list): return x
    return [x]

def load(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        if os.path.exists(path):
            print("  ! chyba JSON %s: %s" % (os.path.basename(path), e))
        return None

def load_glob(prefix):
    out = []
    for p in sorted(glob.glob(os.path.join(DATA, prefix + "*.json"))):
        d = load(p)
        if d is not None:
            out.append(d)
    return out

print("Nacitam data z:", DATA)
segments = sorted(load_glob("seg-"), key=lambda d: d.get("order", 999))
intro_d = load(os.path.join(DATA, "intro.json")) or {}
sign_d = load(os.path.join(DATA, "signatures.json")) or {}
masters = []
for mid in ["master-05", "master-10", "master-30", "spot-most", "spot-staromak"]:
    d = load(os.path.join(DATA, mid + ".json"))
    if d: masters.append(d)
audits = load_glob("_audit-")
all_flags = []
for a in audits:
    for fl in as_list(a.get("flags")):
        if isinstance(fl, dict):
            all_flags.append(fl)

print("  kapitol=%d mistr.skriptu=%d audit_flags=%d signatures=%s intro=%s" % (
    len(segments), len(masters), len(all_flags), bool(sign_d), bool(intro_d)))

# ---------------------------------------------------------------- CSS / JS
CSS = """
:root{
  --bg:#f7f4ee; --ink:#1d1a16; --muted:#6b6256; --line:#e3dac9;
  --card:#fffdf8; --accent:#7a1f2b; --accent2:#b1843a; --gold:#b1843a;
  --cz:#7a1f2b; --en:#1f4e79; --czbg:#fbf1ee; --enbg:#eef3fa;
  --legend:#5b3a8a; --legendbg:#f1ecf8; --warn:#9a2a1a; --warnbg:#fbeae6;
  --ok:#1f6b4a; --okbg:#eef7f1;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;line-height:1.62;font-size:17px}
.topbar{position:sticky;top:0;z-index:50;background:#fffdf8ee;backdrop-filter:blur(6px);
  border-bottom:1px solid var(--line);padding:10px 22px;display:flex;gap:16px;align-items:center;flex-wrap:wrap}
.topbar .brand{font-weight:700;color:var(--accent);font-size:18px;margin-right:auto}
.langbtns button{font-family:inherit;font-size:14px;border:1px solid var(--line);background:#fff;
  border-radius:20px;padding:5px 14px;cursor:pointer;margin-left:6px}
.langbtns button.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.tnav a{font-size:13px;color:var(--accent2);margin-left:14px;text-decoration:none}
.tnav a:hover{color:var(--accent)}
.wrap{max-width:1180px;margin:0 auto;padding:28px 26px 120px}
.cover,.toc-print{display:none}
header.hero{border-bottom:3px double var(--gold);padding-bottom:16px;margin-bottom:10px}
header.hero h1{font-size:40px;margin:0;letter-spacing:-.01em}
header.hero .sub{color:var(--muted);font-size:16px;margin-top:6px}
section.block{scroll-margin-top:64px;margin:42px 0}
section.block>h2{font-size:27px;color:var(--accent);border-bottom:1px solid var(--line);padding-bottom:6px}
.card{background:var(--card);border:1px solid var(--line);border-radius:13px;padding:22px 24px;margin:20px 0;
  box-shadow:0 1px 3px rgba(0,0,0,.04)}
.card h3{font-size:22px;margin:0 0 2px}
.card h3 .en-t{color:var(--muted);font-style:italic;font-weight:400;font-size:17px}
.where{font-size:13px;color:var(--accent2);margin:2px 0 12px}
.where b{color:var(--accent2)}
/* bilingual grid */
.bilang{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:10px 0}
.col{position:relative;border-radius:10px;padding:14px 16px}
.col.cz{background:var(--czbg);border-left:4px solid var(--cz)}
.col.en{background:var(--enbg);border-left:4px solid var(--en)}
.col .flag{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;opacity:.7}
.col.cz .flag{color:var(--cz)} .col.en .flag{color:var(--en)}
.col .cp{position:absolute;top:10px;right:10px;font-size:11px;border:none;border-radius:6px;padding:3px 9px;
  cursor:pointer;font-family:inherit;background:#0002}
.col .cp:hover{background:#0003}
.col p{margin:0 0 10px}
.sub{font-weight:700;color:var(--accent);font-size:13px;letter-spacing:.04em;text-transform:uppercase;margin:18px 0 6px}
.story{border:1px solid var(--line);border-radius:9px;padding:10px 14px;margin:8px 0;background:#fff}
.story .pair{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.story .pair .cz{color:var(--ink)} .story .pair .en{color:#26344a;font-style:italic}
.pill{display:inline-block;font-size:11px;font-weight:700;padding:1px 8px;border-radius:6px;margin-bottom:6px}
.pill.dolozeno{background:var(--okbg);color:var(--ok)}
.pill.legenda{background:var(--legendbg);color:var(--legend)}
.pill.tradicni{background:#fbf3e0;color:#9a6a00}
.pill.nejiste{background:#fbf3e0;color:#9a6a00}
.note{font-size:13px;color:var(--muted)}
.story .note{margin-top:6px}
table.phr{width:100%;border-collapse:collapse;margin-top:8px;font-size:15px}
table.phr td{border:1px solid var(--line);padding:8px 11px;vertical-align:top;width:50%}
table.phr td.cz{background:var(--czbg)} table.phr td.en{background:var(--enbg);font-style:italic}
.trans{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:10px;font-size:15px}
.trans .cz{color:var(--cz)} .trans .en{color:var(--en);font-style:italic}
.flagbox{background:var(--warnbg);border-left:4px solid var(--warn);border-radius:8px;padding:10px 14px;margin:8px 0}
.flagbox .corr{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:5px;font-size:14px}
details{border:1px solid var(--line);border-radius:10px;margin:10px 0;background:#fffdf8}
details>summary{cursor:pointer;padding:9px 14px;font-weight:700;color:var(--muted);list-style:none}
details>summary::-webkit-details-marker{display:none}
details>summary::before{content:"\\25B8 ";color:var(--accent2)}
details[open]>summary::before{content:"\\25BE "}
details .body{padding:2px 16px 12px}
a.src{color:var(--en);word-break:break-all;font-size:13px}
/* master script reader */
.master{background:#fffdf8;border:1px solid var(--line);border-radius:13px;padding:20px 24px;margin:18px 0}
.master h3{margin:0 0 2px;font-size:21px;color:var(--accent)}
.master .meta{font-size:13px;color:var(--accent2);margin-bottom:10px}
.scriptcols{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.scriptcol{position:relative;border-radius:10px;padding:14px 16px}
.scriptcol.cz{background:var(--czbg)} .scriptcol.en{background:var(--enbg);font-style:italic;color:#26344a}
.scriptcol .cp{position:absolute;top:10px;right:10px;font-size:11px;border:none;border-radius:6px;padding:3px 10px;
  cursor:pointer;font-family:inherit;background:#0002}
.scriptcol p{margin:0 0 12px}
/* language toggle behaviour */
body.show-cz .en,body.show-cz .col.en,body.show-cz .scriptcol.en{display:none}
body.show-cz .bilang,body.show-cz .scriptcols,body.show-cz .story .pair,body.show-cz .trans,body.show-cz .flagbox .corr{grid-template-columns:1fr}
body.show-cz table.phr td.en{display:none}
body.show-en .cz,body.show-en .col.cz,body.show-en .scriptcol.cz{display:none}
body.show-en .bilang,body.show-en .scriptcols,body.show-en .story .pair,body.show-en .trans,body.show-en .flagbox .corr{grid-template-columns:1fr}
body.show-en table.phr td.cz{display:none}
body.show-en .col.en,body.show-en .scriptcol.en{font-style:normal}
@media(max-width:820px){
  .bilang,.scriptcols,.story .pair,.trans,.flagbox .corr{grid-template-columns:1fr}
  table.phr td{display:block;width:auto}
  header.hero h1{font-size:30px}
}
@media print{
  @page{margin:17mm 15mm}
  html,body{background:#fff}
  .topbar{display:none}
  header.hero{display:none}
  body{font-size:10.8pt;line-height:1.5;color:#1a1713}
  .wrap{max-width:none;padding:0}
  /* ---- cover ---- */
  .cover{display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;
    height:225mm;overflow:hidden;border:none}
  .cover .kicker{font-size:11.5pt;letter-spacing:.36em;text-transform:uppercase;color:var(--accent2)}
  .cover h1{font-size:48pt;margin:16pt 0 4pt;color:var(--accent);letter-spacing:-.6pt;line-height:1.0}
  .cover .en-title{font-style:italic;font-size:19pt;color:var(--muted);margin:0}
  .cover .rule{width:120pt;height:2.2pt;background:var(--gold);margin:24pt 0}
  .cover .tagline{font-size:12.5pt;color:#1a1713;max-width:340pt;line-height:1.55}
  .cover .foot{margin-top:34pt;font-size:9.5pt;color:var(--muted);letter-spacing:.12em;text-transform:uppercase}
  /* ---- print TOC ---- */
  .toc-print{display:block;break-before:page}
  .toc-print h2{font-size:22pt;color:var(--accent);border-bottom:1.5pt solid var(--gold);padding-bottom:8pt;margin:0 0 6pt}
  .toc-print ol{list-style:none;padding:0;margin:6pt 0 0}
  .toc-print li{padding:4.5pt 0;border-bottom:.5pt dotted var(--line);font-size:11.5pt;
    display:flex;justify-content:space-between;gap:14pt}
  .toc-print li .en{font-style:italic;color:var(--muted);font-size:10pt;text-align:right;flex:0 0 auto}
  .toc-print .grp{font-weight:700;color:var(--accent2);text-transform:uppercase;letter-spacing:.1em;
    font-size:9.5pt;margin:16pt 0 2pt}
  /* ---- chapters: keep two columns (short, fit a page) ---- */
  .bilang,.story .pair,.trans,.flagbox .corr{grid-template-columns:1fr 1fr !important;gap:12pt}
  .col.en,.scriptcol.en,.col.cz,.scriptcol.cz{display:block !important}
  /* ---- master scripts: STACK CZ then EN full-width so they paginate cleanly ---- */
  .scriptcols{display:block !important}
  .scriptcol{break-inside:auto;padding:12pt 14pt}
  .scriptcol.en{font-style:normal;margin-top:10pt}
  .scriptcol.cz::before{content:"Cesky / Czech";display:block;font-size:8.5pt;letter-spacing:.12em;
    text-transform:uppercase;color:var(--cz);font-weight:700;margin-bottom:6pt}
  .scriptcol.en::before{content:"Anglicky / English";display:block;font-size:8.5pt;letter-spacing:.12em;
    text-transform:uppercase;color:var(--en);font-weight:700;margin-bottom:6pt}
  table.phr td.cz,table.phr td.en{display:table-cell !important}
  .cp{display:none}
  .col .flag{opacity:.85}
  details{border:none;background:none}
  details>summary{color:var(--accent);padding:0;font-size:10.5pt}
  details>summary::before{content:""}
  details .body{padding:4pt 0 0}
  /* ---- book structure: each section/chapter on fresh page ---- */
  section.block{break-before:page;margin:0;padding:0}
  section.block>h2{font-size:19pt;color:var(--accent);break-after:avoid;margin:0 0 4pt;
    border-bottom:1pt solid var(--gold);padding-bottom:5pt}
  section.block>.note,section.block>p.note{font-size:9.5pt;color:var(--muted);margin:0 0 8pt}
  .master{break-inside:auto;break-after:page;border:none;box-shadow:none;padding:0;margin:0}
  .master:last-of-type{break-after:auto}
  .master h3{font-size:15pt;color:var(--accent);margin:0 0 1pt}
  .master .meta{font-size:9pt;color:var(--accent2);margin-bottom:8pt}
  section#kapitoly{counter-reset:chap}
  section#kapitoly .card{break-before:page;break-inside:auto;border:none;box-shadow:none;padding:0;margin:0;
    counter-increment:chap}
  section#kapitoly .card:first-of-type{break-before:avoid}
  section#kapitoly .card>h3{font-size:16pt;margin:0 0 2pt}
  section#kapitoly .card>h3::before{content:counter(chap) ".\\00a0\\00a0";color:var(--accent2);font-weight:700}
  .card,.master{box-shadow:none}
  .col,.scriptcol{border-left-width:3px;padding:10pt 12pt}
  .col p,.scriptcol p{margin:0 0 8pt}
  .sub{font-size:9.5pt;margin:14pt 0 4pt}
  .story,.flagbox,.where{break-inside:avoid}
  table.phr td{padding:6pt 9pt}
  /* drop caps on continuous master scripts */
  .scriptcol.cz .txt>p:first-child::first-letter,
  .scriptcol.en .txt>p:first-child::first-letter{
    float:left;font-size:33pt;line-height:.8;padding:3pt 6pt 0 0;color:var(--accent);font-weight:700}
  h2,h3{page-break-after:avoid}
  a.src{color:#444;text-decoration:none}
}
"""

JS = """
function setLang(m){
  document.body.classList.remove('show-cz','show-en','show-both');
  document.body.classList.add('show-'+m);
  document.querySelectorAll('.langbtns button').forEach(function(b){b.classList.remove('active')});
  document.getElementById('lb-'+m).classList.add('active');
}
function cp(btn){
  var t=btn.parentElement.querySelector('.txt');
  if(!t)return;
  navigator.clipboard.writeText(t.innerText).then(function(){
    var o=btn.innerText;btn.innerText='OK';setTimeout(function(){btn.innerText=o},1100);
  });
}
window.addEventListener('DOMContentLoaded',function(){setLang('both')});
"""

# ---------------------------------------------------------------- helpers
def col(lang, label, text):
    cls = "cz" if lang == "cz" else "en"
    return ('<div class="col %s"><div class="flag">%s</div>'
            '<button class="cp" onclick="cp(this)">Kopirovat</button>'
            '<div class="txt">%s</div></div>') % (cls, esc(label), esc(text))

def paras(textlist):
    return "".join("<p>%s</p>" % esc(p) for p in as_list(textlist) if p)

def src_list(sources):
    items = []
    for s in as_list(sources):
        if isinstance(s, dict) and s.get("url"):
            t = esc(s.get("title", s.get("url")))
            d = (" — " + esc(s.get("date"))) if s.get("date") else ""
            items.append('<li><a class="src" href="%s" target="_blank" rel="noopener">%s</a>%s</li>' % (esc(s["url"]), t, d))
        elif isinstance(s, dict):
            items.append("<li>%s</li>" % esc(s.get("title", "")))
        else:
            items.append("<li>%s</li>" % esc(s))
    return "<ul>%s</ul>" % "".join(items) if items else ""

PILL = {"dolozeno": "dolozeno", "legenda": "legenda", "tradicni historka": "tradicni",
        "tradicni": "tradicni", "nejiste": "nejiste", "interpretace": "tradicni"}

def status_pill(st):
    s = (st or "nejiste").lower().strip()
    cls = PILL.get(s, "nejiste")
    return '<span class="pill %s">%s</span>' % (cls, esc(st or "nejiste"))

# ---------------------------------------------------------------- renderers
def render_intro():
    if not intro_d: return ""
    h = ['<div class="card" id="uvod">']
    h.append('<div class="bilang">')
    h.append(col("cz", "Filozofie", intro_d.get("philosophy_cz", "")))
    h.append(col("en", "Philosophy", intro_d.get("philosophy_en", "")))
    h.append('</div>')
    hc = as_list(intro_d.get("howto_cz")); he = as_list(intro_d.get("howto_en"))
    if hc or he:
        h.append('<div class="bilang">')
        h.append('<div class="col cz"><div class="flag">Jak používat</div><ul>%s</ul></div>' % "".join("<li>%s</li>" % esc(x) for x in hc))
        h.append('<div class="col en"><div class="flag">How to use</div><ul>%s</ul></div>' % "".join("<li>%s</li>" % esc(x) for x in he))
        h.append('</div>')
    if intro_d.get("legend_key_cz") or intro_d.get("legend_key_en"):
        h.append('<div class="trans"><div class="cz"><b>Klíč statusů:</b> %s</div><div class="en"><b>Status key:</b> %s</div></div>'
                 % (esc(intro_d.get("legend_key_cz", "")), esc(intro_d.get("legend_key_en", ""))))
    h.append('</div>')
    return "".join(h)

def render_master(d):
    h = ['<div class="master" id="%s">' % esc(d.get("id", ""))]
    h.append('<h3>%s</h3>' % esc(d.get("label", d.get("id", ""))))
    meta = []
    if d.get("length"): meta.append(esc(d["length"]))
    if d.get("where_cz"): meta.append(esc(d["where_cz"]))
    if meta: h.append('<div class="meta">%s</div>' % " · ".join(meta))
    h.append('<div class="scriptcols">')
    h.append('<div class="scriptcol cz"><button class="cp" onclick="cp(this)">Kopirovat CZ</button><div class="txt">%s</div></div>' % paras(d.get("script_cz")))
    h.append('<div class="scriptcol en"><button class="cp" onclick="cp(this)">Copy EN</button><div class="txt">%s</div></div>' % paras(d.get("script_en")))
    h.append('</div></div>')
    return "".join(h)

def render_segment(d):
    h = ['<article class="card" id="%s">' % esc(d.get("id", ""))]
    h.append('<h3>%s <span class="en-t">/ %s</span></h3>' % (esc(d.get("title_cz", "")), esc(d.get("title_en", ""))))
    if d.get("where_cz") or d.get("where_en"):
        h.append('<div class="where"><b>Kde:</b> %s &nbsp;·&nbsp; <i>%s</i></div>' % (esc(d.get("where_cz", "")), esc(d.get("where_en", ""))))
    # narration
    h.append('<div class="bilang">')
    h.append(col("cz", "Povídání", d.get("narration_cz", "")))
    h.append(col("en", "Narration", d.get("narration_en", "")))
    h.append('</div>')
    # guide stories
    st = as_list(d.get("guide_stories"))
    if st:
        body = []
        for s in st:
            if not isinstance(s, dict): continue
            body.append('<div class="story">%s<div class="pair"><div class="cz">%s</div><div class="en">%s</div></div>%s</div>' % (
                status_pill(s.get("status")), esc(s.get("cz", "")), esc(s.get("en", "")),
                ('<div class="note">%s</div>' % esc(s.get("note_cz", ""))) if s.get("note_cz") else ""))
        h.append('<div class="sub">Průvodcovské historky / Guide stories</div>' + "".join(body))
    # key phrases
    kp = as_list(d.get("key_phrases"))
    if kp:
        rows = "".join('<tr><td class="cz">%s</td><td class="en">%s</td></tr>' % (esc(p.get("cz", "")), esc(p.get("en", ""))) for p in kp if isinstance(p, dict))
        h.append('<div class="sub">Podpisové věty / Signature lines</div><table class="phr"><tbody>%s</tbody></table>' % rows)
    # transition
    if d.get("transition_cz") or d.get("transition_en"):
        h.append('<div class="sub">Přechod / Transition</div><div class="trans"><div class="cz">%s</div><div class="en">%s</div></div>'
                 % (esc(d.get("transition_cz", "")), esc(d.get("transition_en", ""))))
    # fact flags
    ff = as_list(d.get("fact_flags"))
    if ff:
        body = []
        for f in ff:
            if not isinstance(f, dict): continue
            body.append('<div class="flagbox"><b>Mýtus:</b> %s<div class="corr"><div class="cz">%s</div><div class="en"><i>%s</i></div></div></div>' % (
                esc(f.get("claim_cz", "")), esc(f.get("correction_cz", "")), esc(f.get("correction_en", ""))))
        h.append('<div class="sub">Pozor na mýtus / Myths to correct</div>' + "".join(body))
    # sources
    h.append(details_block("Zdroje / Sources", src_list(d.get("sources"))))
    h.append('</article>')
    return "".join(h)

def details_block(summary, inner):
    if not inner: return ""
    return '<details><summary>%s</summary><div class="body">%s</div></details>' % (esc(summary), inner)

def render_signatures():
    if not sign_d: return ""
    h = []
    def pairtable(title, items, kcz="cz", ken="en", note=False):
        rows = []
        for it in as_list(items):
            if not isinstance(it, dict): continue
            extra = ""
            if it.get("where"): extra = '<div class="note">%s</div>' % esc(it["where"])
            if note and it.get("note"): extra = '<div class="note">%s</div>' % esc(it["note"])
            rows.append('<tr><td class="cz">%s%s</td><td class="en">%s</td></tr>' % (esc(it.get(kcz, "")), extra, esc(it.get(ken, ""))))
        if not rows: return ""
        return '<div class="sub">%s</div><table class="phr"><tbody>%s</tbody></table>' % (esc(title), "".join(rows))
    h.append(pairtable("Podpisové věty / Signature lines", sign_d.get("signature_lines")))
    h.append(pairtable("Přechody / Transitions", sign_d.get("transitions")))
    h.append(pairtable("Vtipy / Jokes", sign_d.get("jokes"), note=True))
    h.append(pairtable("Opravy mýtů / Myth corrections", sign_d.get("myth_corrections")))
    return '<div class="card">%s</div>' % "".join(h)

def render_audit():
    if not all_flags: return '<p class="note">Audit nenahlásil žádné sporné tvrzení.</p>'
    by = {"vysoka": [], "stredni": [], "nizka": []}
    other = []
    for f in all_flags:
        sev = (f.get("severity") or "").lower()
        (by.get(sev, other)).append(f)
    h = []
    for sev, label in [("vysoka", "Vysoká závažnost"), ("stredni", "Střední"), ("nizka", "Nízká")]:
        fl = by.get(sev) or []
        if not fl: continue
        h.append('<div class="sub">%s (%d)</div>' % (label, len(fl)))
        for f in fl:
            h.append('<div class="flagbox"><b>%s</b> — %s <span class="note">(%s; doporučeno: %s)</span></div>' % (
                esc(f.get("claim", "")), esc(f.get("issue", "")), esc(f.get("seg_id", "")), esc(f.get("suggested_label", ""))))
    return "".join(h)

# ---------------------------------------------------------------- assemble
def page(title, body, css=CSS, js=JS, topbar=True):
    tb = ""
    if topbar:
        tb = ('<div class="topbar"><span class="brand">Povídání o Praze</span>'
              '<span class="tnav">'
              '<a href="#uvod">Úvod</a><a href="#skripty">Skripty</a><a href="#kapitoly">Kapitoly</a>'
              '<a href="#tahak">Tahák</a><a href="#overeni">K ověření</a></span>'
              '<span class="langbtns">'
              '<button id="lb-both" class="active" onclick="setLang(\'both\')">CZ + EN</button>'
              '<button id="lb-cz" onclick="setLang(\'cz\')">Česky</button>'
              '<button id="lb-en" onclick="setLang(\'en\')">English</button></span></div>')
    return ("<!doctype html><html lang='cs'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>%s</title><style>%s</style></head><body class='show-both'>%s%s<script>%s</script></body></html>"
            % (esc(title), css, tb, body, js))

# print-only cover
cover_html = ('<div class="cover">'
    '<div class="kicker">Průvodcovský materiál &middot; Guide material</div>'
    '<h1>Povídání o Praze</h1>'
    '<p class="en-title">Prague &mdash; the Living Narration</p>'
    '<div class="rule"></div>'
    '<p class="tagline">Souvislé mluvené povídání o celé Praze z reálné průvodcovské tradice &mdash; '
    'česky i anglicky. Fakta, legendy a historky jasně oddělené.</p>'
    '<div class="foot">Verze 1 &middot; 2026 &middot; CZ / EN</div></div>')

# print-only table of contents
def build_toc():
    p = ['<div class="toc-print"><h2>Obsah / Contents</h2>']
    if masters:
        p.append('<div class="grp">Mistrovské výklady / Master scripts</div><ol>')
        for m in masters:
            p.append('<li><span>%s</span><span class="en">%s</span></li>' % (esc(m.get("label", "")), esc(m.get("length", ""))))
        p.append('</ol>')
    if segments:
        p.append('<div class="grp">Vyprávěcí kapitoly / Chapters</div><ol>')
        for i, d in enumerate(segments, 1):
            p.append('<li><span>%d. %s</span><span class="en">%s</span></li>' % (i, esc(d.get("title_cz", "")), esc(d.get("title_en", ""))))
        p.append('</ol>')
    p.append('<div class="grp">Další / More</div><ol>'
             '<li><span>Tahák průvodce</span><span class="en">Guide cheat-sheet</span></li>'
             '<li><span>K ověření</span><span class="en">Fact-check</span></li></ol>')
    p.append('</div>')
    return "".join(p)

body = ['<div class="wrap">',
        cover_html,
        '<header class="hero"><h1>Povídání o Praze</h1>'
        '<div class="sub">Souvislé mluvené povídání o celé Praze z reálné průvodcovské tradice — česky i anglicky vedle sebe. '
        'Fakta, legendy a historky jasně odděleny. Verze 1.</div></header>',
        build_toc()]

if intro_d:
    body.append('<section class="block"><h2>Úvod / Introduction</h2>%s</section>' % render_intro())

if masters:
    body.append('<section class="block" id="skripty"><h2>Mistrovské výklady / Master scripts</h2>'
                '<p class="note">Souvislé skripty k přednesu: základní povídání (5/10/30 min) a on-location na konkrétních místech. Tlačítka kopírují text.</p>')
    # order: 05,10,30, spots
    for d in masters:
        body.append(render_master(d))
    body.append('</section>')

body.append('<section class="block" id="kapitoly"><h2>Vyprávěcí kapitoly / Narrative chapters</h2>'
            '<p class="note">Stavební kameny velkého příběhu Prahy napříč časem. U každé: povídání CZ+EN, průvodcovské historky (se statusem), podpisové věty, přechod a mýty k uvedení na pravou míru.</p>')
for d in segments:
    body.append(render_segment(d))
body.append('</section>')

if sign_d:
    body.append('<section class="block" id="tahak"><h2>Tahák průvodce / Guide cheat-sheet</h2>%s</section>' % render_signatures())

body.append('<section class="block" id="overeni"><h2>K ověření / Fact-check</h2>%s</section>' % render_audit())
body.append('</div>')

with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
    f.write(page("Povídání o Praze — CZ/EN", "".join(body)))

# skripty.html - jen mistrovske vyklady (terenni verze)
skripty_cover = ('<div class="cover">'
    '<div class="kicker">Průvodcovské skripty &middot; Master scripts</div>'
    '<h1>Pražské skripty</h1>'
    '<p class="en-title">Prague &mdash; Master Scripts</p>'
    '<div class="rule"></div>'
    '<p class="tagline">Souvislé výklady k přednesu &mdash; 5 / 10 / 30 minut a on-location '
    'na Karlově mostě a Staroměstském náměstí. Česky i anglicky.</p>'
    '<div class="foot">Verze 1 &middot; 2026 &middot; CZ / EN</div></div>')
sb = ['<div class="wrap">', skripty_cover,
      '<header class="hero"><h1>Pražské skripty</h1>'
      '<div class="sub">Souvislé výklady k přednesu (CZ + EN)</div></header>'
      '<section class="block" id="skripty">']
for d in masters:
    sb.append(render_master(d))
sb.append('</section></div>')
with open(os.path.join(OUT, "skripty.html"), "w", encoding="utf-8") as f:
    f.write(page("Pražské skripty", "".join(sb)))

# povidani.md
md = ["# Povídání o Praze (CZ/EN)\n"]
for d in masters:
    md.append("## %s" % d.get("label", d.get("id", "")))
    md.append("**CZ:**")
    for p in as_list(d.get("script_cz")): md.append(p)
    md.append("\n**EN:**")
    for p in as_list(d.get("script_en")): md.append(p)
    md.append("")
md.append("\n# Kapitoly\n")
for d in segments:
    md.append("## %s / %s" % (d.get("title_cz", ""), d.get("title_en", "")))
    md.append("**CZ:** " + str(d.get("narration_cz", "")))
    md.append("\n**EN:** " + str(d.get("narration_en", "")))
    md.append("")
with open(os.path.join(OUT, "povidani.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md))

print("\nHOTOVO. Vygenerovano do:", OUT)
for fn in ["index.html", "skripty.html", "povidani.md"]:
    p = os.path.join(OUT, fn)
    print("  %-18s %9d B" % (fn, os.path.getsize(p)) if os.path.exists(p) else "  %-18s CHYBI" % fn)
