#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Renderer of "Prague - A Guide's Storybook" (English-only).
Reads stories/cat-*.json and generates:
  storybook.html          - the storybook (screen + print)
PDF is produced separately via Chrome headless.
Defensive: skips missing keys/files.
"""
import json, os, glob, html

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "stories")
OUT = BASE

def esc(x): return html.escape(str(x if x is not None else ""))
def as_list(x):
    if x is None: return []
    return x if isinstance(x, list) else [x]

def load_glob(prefix):
    out = []
    for p in sorted(glob.glob(os.path.join(DATA, prefix + "*.json"))):
        try:
            with open(p, encoding="utf-8") as f:
                out.append(json.load(f))
        except Exception as e:
            print("  ! bad JSON %s: %s" % (os.path.basename(p), e))
    return out

print("Reading stories from:", DATA)
cats = load_glob("cat-")
total = sum(len(as_list(c.get("stories"))) for c in cats)
print("  categories=%d  stories=%d" % (len(cats), total))

CSS = """
:root{
  --bg:#f7f4ee; --ink:#1d1a16; --muted:#6b6256; --line:#e3dac9; --card:#fffdf8;
  --accent:#7a1f2b; --accent2:#b1843a; --gold:#b1843a;
  --doc:#1f6b4a; --docbg:#eef7f1; --leg:#5b3a8a; --legbg:#f1ecf8;
  --tale:#9a6a00; --talebg:#fbf3e0;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;line-height:1.6;font-size:17px}
.topbar{position:sticky;top:0;z-index:9;background:#fffdf8ee;backdrop-filter:blur(6px);
  border-bottom:1px solid var(--line);padding:10px 22px;display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.topbar .brand{font-weight:700;color:var(--accent);font-size:17px;margin-right:auto}
.topbar a{font-size:12.5px;color:var(--accent2);text-decoration:none}
.topbar a:hover{color:var(--accent)}
.wrap{max-width:940px;margin:0 auto;padding:28px 26px 120px}
header.hero{border-bottom:3px double var(--gold);padding-bottom:16px;margin-bottom:10px}
header.hero h1{font-size:40px;margin:0}
header.hero .sub{color:var(--muted);font-size:16px;margin-top:6px}
.cover,.toc-print{display:none}
section.cat{scroll-margin-top:60px;margin:40px 0}
section.cat>h2{font-size:26px;color:var(--accent);border-bottom:1px solid var(--gold);padding-bottom:6px;margin-bottom:4px}
section.cat>.cnote{color:var(--muted);font-style:italic;margin:0 0 14px}
.story{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 20px;margin:14px 0;
  box-shadow:0 1px 3px rgba(0,0,0,.04)}
.story .head{display:flex;align-items:baseline;gap:12px;margin-bottom:6px}
.story h3{font-size:19px;margin:0;color:var(--ink);flex:1}
.story h3 .num{color:var(--accent2);font-weight:700;margin-right:6px}
.pill{display:inline-block;font-size:10.5px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;
  padding:2px 9px;border-radius:20px;white-space:nowrap}
.pill.documented{background:var(--docbg);color:var(--doc)}
.pill.legend{background:var(--legbg);color:var(--leg)}
.pill.tale{background:var(--talebg);color:var(--tale)}
.pill.uncertain{background:var(--talebg);color:var(--tale)}
.story .tale{margin:6px 0 10px}
.story .foot{border-top:1px dotted var(--line);padding-top:8px;font-size:13px;color:var(--muted);
  display:flex;flex-wrap:wrap;gap:16px}
.story .foot b{color:var(--accent2);text-transform:uppercase;font-size:11px;letter-spacing:.06em}
@media(max-width:640px){ header.hero h1{font-size:30px} .story .foot{flex-direction:column;gap:4px} }
@media print{
  @page{margin:17mm 16mm}
  html,body{background:#fff}
  .topbar{display:none}
  header.hero{display:none}
  body{font-size:11pt;line-height:1.5;color:#1a1713}
  .wrap{max-width:none;padding:0}
  .cover{display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;
    height:225mm;overflow:hidden;border:none}
  .cover .kicker{font-size:11.5pt;letter-spacing:.34em;text-transform:uppercase;color:var(--accent2)}
  .cover h1{font-size:46pt;margin:16pt 0 4pt;color:var(--accent);letter-spacing:-.5pt;line-height:1.02}
  .cover .subt{font-style:italic;font-size:18pt;color:var(--muted);margin:0}
  .cover .rule{width:120pt;height:2.2pt;background:var(--gold);margin:22pt 0}
  .cover .tagline{font-size:12.5pt;color:#1a1713;max-width:340pt;line-height:1.5}
  .cover .foot{margin-top:30pt;font-size:9.5pt;color:var(--muted);letter-spacing:.12em;text-transform:uppercase}
  .toc-print{display:block;break-before:page}
  .toc-print h2{font-size:22pt;color:var(--accent);border-bottom:1.5pt solid var(--gold);padding-bottom:8pt;margin:0 0 6pt}
  .toc-print ol{list-style:none;padding:0;margin:6pt 0 0}
  .toc-print li{padding:5pt 0;border-bottom:.5pt dotted var(--line);font-size:12.5pt;
    display:flex;justify-content:space-between;gap:14pt}
  .toc-print li .n{color:var(--accent2);font-size:10.5pt}
  section.cat{break-before:page;margin:0}
  section.cat:first-of-type{break-before:avoid}
  section.cat>h2{font-size:19pt;break-after:avoid;margin:0 0 3pt}
  section.cat>.cnote{margin:0 0 10pt}
  .story{break-inside:avoid;border:none;border-bottom:.6pt solid var(--line);border-radius:0;
    box-shadow:none;padding:0 0 9pt;margin:11pt 0}
  .story h3{font-size:14pt}
  h2,h3{page-break-after:avoid}
}
"""

def pill(st):
    s = (st or "traditional tale").lower().strip()
    if "document" in s:   cls, lab = "documented", "documented"
    elif "legend" in s:   cls, lab = "legend", "legend"
    elif "tale" in s or "tradition" in s: cls, lab = "tale", "traditional tale"
    elif "uncert" in s:   cls, lab = "uncertain", "uncertain"
    else:                 cls, lab = "tale", s
    return '<span class="pill %s">%s</span>' % (cls, esc(lab))

def render_story(s, n):
    if not isinstance(s, dict): return ""
    h = ['<article class="story">']
    h.append('<div class="head"><h3><span class="num">%d</span>%s</h3>%s</div>' % (n, esc(s.get("title","")), pill(s.get("status"))))
    h.append('<p class="tale">%s</p>' % esc(s.get("tale","")))
    foot = []
    if s.get("where"): foot.append('<span><b>Where</b> &nbsp;%s</span>' % esc(s["where"]))
    if s.get("tell_tip"): foot.append('<span><b>Tip</b> &nbsp;%s</span>' % esc(s["tell_tip"]))
    if foot: h.append('<div class="foot">%s</div>' % "".join(foot))
    h.append('</article>')
    return "".join(h)

def anchor(c): return "cat-" + str(c.get("id","")).replace("cat-","")

# cover + toc
cover = ('<div class="cover">'
  '<div class="kicker">A Prague Guide\'s Companion</div>'
  '<h1>Prague</h1>'
  '<p class="subt">A Guide&#39;s Storybook</p>'
  '<div class="rule"></div>'
  '<p class="tagline">Tales to tell on the walk &mdash; funny history, legends, ghosts and curiosities. '
  'Every tale tagged for truth: documented, legend or traditional tale.</p>'
  '<div class="foot">Version 1 &middot; 2026 &middot; English</div></div>')

def build_toc():
    p = ['<div class="toc-print"><h2>Contents</h2><ol>']
    for c in cats:
        p.append('<li><span>%s</span><span class="n">%d tales</span></li>' % (esc(c.get("category_en","")), len(as_list(c.get("stories")))))
    p.append('</ol></div>')
    return "".join(p)

# topbar
tb = ['<div class="topbar"><span class="brand">Prague &mdash; A Guide&#39;s Storybook</span>']
for c in cats:
    tb.append('<a href="#%s">%s</a>' % (anchor(c), esc(c.get("category_en",""))))
tb.append('</div>')

body = ['<div class="wrap">', cover,
  '<header class="hero"><h1>Prague &mdash; A Guide&#39;s Storybook</h1>'
  '<div class="sub">Tales to tell on the walk: funny history, legends, ghosts and curiosities. '
  '%d stories across %d chapters, each tagged for truth.</div></header>' % (total, len(cats)),
  build_toc()]

n = 0
for c in cats:
    body.append('<section class="cat" id="%s"><h2>%s</h2>' % (anchor(c), esc(c.get("category_en",""))))
    if c.get("category_note"):
        body.append('<p class="cnote">%s</p>' % esc(c["category_note"]))
    for s in as_list(c.get("stories")):
        n += 1
        body.append(render_story(s, n))
    body.append('</section>')
body.append('</div>')

pagehtml = ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
  "<meta name='viewport' content='width=device-width,initial-scale=1'>"
  "<title>Prague - A Guide's Storybook</title><style>%s</style></head>"
  "<body>%s%s</body></html>" % (CSS, "".join(tb), "".join(body)))

with open(os.path.join(OUT, "storybook.html"), "w", encoding="utf-8") as f:
    f.write(pagehtml)

print("\nDONE. Wrote:", os.path.join(OUT, "storybook.html"), "(%d B)" % os.path.getsize(os.path.join(OUT,"storybook.html")))
print("  total stories:", total)
