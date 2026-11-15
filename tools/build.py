"""Build the site from src/.

Sources
  src/page.html          the home page, plus everything shared: head, styles, nav, footer, script
  src/why-ferro.html     the Why Ferro page's <main>
  src/pages/*.html       the other inside pages' <main>s; line 1 is <!--page {json}--> with key, url, title, desc
  src/sector.html        template for the eight sector pages, filled from SECTORS + src/sector-copy.json
  src/projects.json      the project gallery (from Ferro's "Project Gallery" sheet)

Inside the page sources, build-time blocks are written as HTML comments:
  <!--@cta h="" p="" btn="" img="" -->   the closing call to action band
  <!--@shelf sector="slug" -->           sideways project cards for one sector (falls back to all projects)
  <!--@projects-grid-->                  the filterable grid on /projects/
  <!--@sector-rows-->                    the linked list of sectors on the Pre-Engineered page

Outputs
  index.html, <url>/index.html   one host page per page
  navy/..., navy/why-ferro/      redirects from the retired two-theme URLs
  build/preview.html             the claude.ai preview: every page in one file, switched with #<key>

Host pages use root-absolute asset paths so they work at any depth.
Run from the repo root:  python3 tools/build.py
"""
import html, json, pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent
src = root / "src"

# social previews need absolute URLs; change this when the site moves to its own domain
SITE = "https://ferro.rd-bannon.workers.dev"
SUFFIX = " — Ferro Steel Building Systems"
URLS = {"home": "/", "why-ferro": "/why-ferro/"}
OLD = {"/navy/": "/", "/navy/why-ferro/": "/why-ferro/"}   # retired theme URLs that may still carry review comments
TITLES = {"home": "Ferro — Steel Building Systems", "why-ferro": "Why Ferro" + SUFFIX}
DESCRIPTIONS = {
    "home": "Ferro Building Systems designs and builds custom pre-engineered steel buildings, backed by a five-year workmanship warranty.",
    "why-ferro": "Ferro brings certainty to complex steel building projects: compliance know-how, built-in quality assurance, responsible planning and a proven process.",
}

# slug, name (as HTML), banner photo, alt, placeholder photo?, closing-band photo
SECTORS = [
    ("energy-utilities", "Energy &amp; Utilities", "proj-19-685-0.jpg", "BC Hydro truck storage building in Williams Lake at sunset", False, "wf-site.jpg"),
    ("waste-water", "Waste &amp; Water", "broll-0.jpg", "Steel framework against a sunset sky", True, "wf-quality.jpg"),
    ("aviation-transport", "Aviation &amp; Transport", "proj-20-316-0.jpg", "A business jet inside the Advance Aerospace hangar at Boundary Bay Airport", False, "svc-integrated.jpg"),
    ("public-spaces-recreation", "Public Spaces &amp; Recreation", "proj-21-384-0.jpg", "Queen Margaret’s Sports Dome with its timber entry canopy", False, "project-feature.jpg"),
    ("civic-buildings-facilities", "Civic Buildings &amp; Facilities", "proj-21-378-0.jpg", "Vernon Search and Rescue Centre", False, "wf-compliance.jpg"),
    ("commercial", "Commercial", "proj-21-466-0.jpg", "Greenrock Industrial Commercial Centre in Nanaimo", False, "prj-kal-tire.jpg"),
    ("agricultural", "Agricultural", "broll-1.jpg", "Steel framework against a clear blue sky", True, "svc-core.jpg"),
    ("industrial", "Industrial", "proj-18-382-0.jpg", "The Axton fabrication facility in Delta", False, "int-crane-wide.jpg"),
]
SECTOR_NAMES = {s[0]: s[1] for s in SECTORS}
# no copy yet for Public Spaces: it borrows the Government & Institutional copy (filed under Civic) and says so
SECTOR_COPY = json.loads((src / "sector-copy.json").read_text(encoding="utf-8"))
SECTOR_COPY["public-spaces-recreation"] = SECTOR_COPY["civic-buildings-facilities"]
PROJECTS = json.loads((src / "projects.json").read_text(encoding="utf-8"))

page = (src / "page.html").read_text(encoding="utf-8")
why_main = (src / "why-ferro.html").read_text(encoding="utf-8").strip()
home_main = re.search(r'<main id="top" data-view="home">.*?</main>', page, re.S).group(0)
sector_tpl = (src / "sector.html").read_text(encoding="utf-8").strip()
NOTE = ('<aside class="wf-note" aria-label="Placeholder image"><p class="wf-note-h"><span class="mask" aria-hidden="true" style="--m:url(assets/camera.svg);width:20px;height:16px"></span>'
        '<span class="mask wf-note-site" role="img" aria-label="Site." style="--m:url(assets/site.svg);width:37px;height:14px"></span><span class="wf-note-tag">Placeholder</span></p>'
        '<p>FINAL IMAGE TO BE PROVIDED BY FERRO</p></aside>')
ARR = '<span class="arr" aria-hidden="true"></span>'
plain = lambda s: html.unescape(re.sub(r"<[^>]+>", " ", s)).replace("  ", " ").strip()


# ---------- build-time blocks ----------
def cta(h, p, btn, img, to="contact"):
    return f'''<section class="x-cta" aria-label="{html.escape(plain(h))}">
    <div class="x-cta-copy" data-stagger=".h-xl,.wf-p,.btn" data-step="80">
      <h2 class="h-xl">{h}</h2>
      <p class="wf-p">{p}</p>
      <a class="btn btn-solid" data-page="{to}" href="#{to}">{btn} {ARR}</a>
    </div>
    <figure class="wf-media plx"><img class="img" src="assets/{img}" alt="" loading="lazy" decoding="async"></figure>
  </section>'''


def card(p):
    sec = p["sectors"][0]
    loc = f'{p["city"]}, {p["prov"]}'
    return (f'<article class="x-pcard" data-project="{p["id"]}" data-sectors="{" ".join(p["sectors"])}" data-service="{html.escape(p["service"])}" data-prov="{p["prov"]}">'
            f'<div class="x-thumb"><span class="x-chip">{SECTOR_NAMES[sec]}</span><img src="assets/{p["img"]}" alt="" loading="lazy" decoding="async"></div>'
            f'<h3><button class="x-open" type="button" aria-haspopup="dialog">{html.escape(p["name"])}</button></h3>'
            f'<p class="x-meta">{loc} · {html.escape(p["service"])}</p></article>')


def shelf(sector=None):
    picks = [p for p in PROJECTS if sector in p["sectors"]] if sector else []
    note = ""
    if len(picks) < 3:   # thin sectors fill out with other work so the slider never looks empty
        if not picks:
            note = '<p class="x-flag-row"><span class="x-flag">No projects filed under this sector yet · showing recent work</span></p>'
        picks += [p for p in PROJECTS if p not in picks][: max(0, 6 - len(picks))]
    cards = "\n        ".join(card(p) for p in picks)
    return f'''<div class="x-shelf" data-shelf>
      <div class="wf-wrap x-shelf-head" data-stagger=".eyebrow,.h-xl,.x-shelf-nav" data-step="70">
        <div><p class="eyebrow">Projects</p><h2 class="h-xl">The Proof is in<br>Our Projects</h2></div>
        <div class="x-shelf-nav"><button type="button" data-dir="-1" aria-label="Previous projects"><svg width="9" height="14" viewBox="0 0 9 14" aria-hidden="true"><path d="M7.5 1.5 2 7l5.5 5.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button><button type="button" data-dir="1" aria-label="Next projects"><svg width="9" height="14" viewBox="0 0 9 14" aria-hidden="true"><path d="M1.5 1.5 7 7l-5.5 5.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button></div>
      </div>
      {note}
      <div class="x-track" data-stagger=".x-pcard" data-step="70">
        {cards}
      </div>
      <div class="wf-wrap"><a class="btn btn-line" data-page="projects" href="#projects">See Our Work {ARR}</a></div>
    </div>'''


def select(name, label, options):
    opts = "".join(f'<option value="{html.escape(v)}">{t}</option>' for v, t in options)
    return f'<label class="x-select"><span class="sr">{label}</span><select data-filter="{name}"><option value="">{label}: All</option>{opts}</select></label>'


def projects_grid():
    used = sorted({s for p in PROJECTS for s in p["sectors"]}, key=lambda s: [x[0] for x in SECTORS].index(s))
    services = sorted({x.strip() for p in PROJECTS for x in re.split(r",", p["service"])})
    provs = sorted({p["prov"] for p in PROJECTS})
    prov_names = {"BC": "British Columbia", "AB": "Alberta"}
    filters = (select("sector", "Sector", [(s, SECTOR_NAMES[s]) for s in used]) +
               select("service", "Service", [(s, html.escape(s)) for s in services]) +
               select("prov", "Location", [(p, prov_names.get(p, p)) for p in provs]))
    cards = "\n      ".join(card(p) for p in PROJECTS)
    return f'''<div class="wf-wrap x-filters" role="group" aria-label="Filter projects" data-filters>
      {filters}
      <span class="x-count" aria-live="polite" data-count>{len(PROJECTS)} projects</span>
      <button class="x-clear" type="button" data-clear hidden>Clear</button>
    </div>
    <div class="wf-wrap x-grid" data-grid data-stagger=".x-pcard" data-step="50">
      {cards}
      <p class="x-empty" hidden>No projects match those filters yet.</p>
    </div>'''


def sector_rows():
    rows = []
    for slug, name, *_ in SECTORS:
        desc = re.search(r'<h3><a class="sec-go" data-page="sector-' + slug + r'"[^>]*>.*?</a></h3></div><p>(.*?)</p>', page)
        rows.append(f'<li><a class="x-row" data-page="sector-{slug}" href="#sector-{slug}"><img src="assets/sector-{slug}.svg" width="34" height="30" alt=""><span><b>{name}</b><span>{desc.group(1) if desc else ""}</span></span>{ARR}</a></li>')
    return '<ul class="x-rows" data-stagger="li" data-step="50">\n        ' + "\n        ".join(rows) + "\n      </ul>"


def attrs(s):
    return dict(re.findall(r'(\w+)="([^"]*)"', s))


def blocks(h):
    h = re.sub(r"<!--@cta (.*?)-->", lambda m: cta(**attrs(m.group(1))), h, flags=re.S)
    h = re.sub(r"<!--@shelf ?(.*?)-->", lambda m: shelf(attrs(m.group(1)).get("sector")), h)
    h = h.replace("<!--@projects-grid-->", projects_grid()).replace("<!--@sector-rows-->", sector_rows())
    return h


# ---------- pages ----------
MAINS = {"home": home_main, "why-ferro": why_main}

for slug, name, img, alt, ph, ctaimg in SECTORS:
    c = SECTOR_COPY[slug]
    desc = re.search(r'<h3><a class="sec-go" data-page="sector-' + slug + r'"[^>]*>.*?</a></h3></div><p>(.*?)</p>', page).group(1)
    services = "\n      ".join(f'<li class="x-card"><span class="x-num">{i + 1:02d}</span><h3>{html.escape(t)}</h3><p>{html.escape(b)}</p></li>'
                               for i, (t, b) in enumerate(c["services"]))
    flag = ('<p class="x-flag-row"><span class="x-flag">Draft · no copy for this sector yet, showing Government &amp; Institutional copy</span></p>'
            if slug == "public-spaces-recreation" else "")
    key = f"sector-{slug}"
    fill = {"slug": slug, "name": name, "desc": desc, "img": f"assets/{img}", "alt": alt, "note": NOTE if ph else "",
            "challenges": html.escape(c["challenges"]), "solutions": html.escape(c["solutions"]),
            "svc_head": "<br>".join(html.escape(x) for x in c["svc_head"]), "svc_body": html.escape(c["svc_body"]),
            "services": services, "flag": flag, "ctaimg": ctaimg}
    MAINS[key] = re.sub(r"\{\{(\w+)\}\}", lambda m: fill[m.group(1)], sector_tpl)
    URLS[key] = f"/sectors/{slug}/"
    TITLES[key] = plain(name) + SUFFIX
    DESCRIPTIONS[key] = plain(desc)

for f in sorted((src / "pages").glob("*.html")):
    text = f.read_text(encoding="utf-8")
    meta = json.loads(re.match(r"<!--page (\{.*?\})-->", text).group(1))
    k = meta["key"]
    MAINS[k] = text[text.index("-->") + 3:].strip()
    URLS[k], TITLES[k], DESCRIPTIONS[k] = meta["url"], meta["title"] + SUFFIX, meta["desc"]

MAINS = {k: blocks(v) for k, v in MAINS.items()}

# every page's "show this main" rule, the preview's page list, and the project data the dialog reads
views = "\n".join(f'[data-page="{k}"] main[data-view="{k}"]{{display:block}}' for k in MAINS if k != "home")
page = page.replace("/* @page-views: build.py writes one \"show this page's main\" rule per page here */", views)
page = page.replace("/*@views*/[]", json.dumps([k for k in MAINS if k != "home"]))
pdata = {p["id"]: {**p, "sectorNames": [plain(SECTOR_NAMES[s]) for s in p["sectors"]]} for p in PROJECTS}
page = page.replace("<!--@project-data-->", '<script type="application/json" id="projectData">' + json.dumps(pdata, ensure_ascii=False).replace("</", "<\\/") + "</script>")
page = blocks(page)
home_main = MAINS["home"]
page = page.replace(re.search(r'<main id="top" data-view="home">.*?</main>', page, re.S).group(0), home_main)

missing = sorted({m for m in re.findall(r'data-page="([\w-]+)"', page + "".join(MAINS.values())) if m not in URLS})
if missing:
    raise SystemExit(f"links to pages that don't exist: {missing}")


def compose(main_html: str) -> str:
    return page.replace(home_main, main_html)


# ---- claude.ai preview: every main, relative assets ----
(root / "build").mkdir(exist_ok=True)
(root / "build" / "preview.html").write_text(page.replace(home_main, "\n\n".join(MAINS.values())), encoding="utf-8")
print("wrote build/preview.html")


def host_page(pg: str) -> str:
    body = compose(MAINS[pg])
    body = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\n?', "", body)
    body = re.sub(r"<title>.*?</title>", f"<title>{html.escape(TITLES[pg], quote=False)}</title>", body, count=1)
    # links between pages point at real URLs
    body = re.sub(r'data-page="([\w-]+)" href="[^"]*"', lambda m: f'data-page="{m.group(1)}" href="{URLS[m.group(1)]}"', body)
    body = re.sub(r'data-to="([\w-]+)" data-page="([\w-]+)" href="[^"]*"', lambda m: f'data-to="{m.group(1)}" data-page="{m.group(2)}" href="{URLS[m.group(2)]}#{m.group(1)}"', body)
    body = body.replace('<a class="logo" href="#top"', f'<a class="logo" href="{URLS["home"]}"')
    body = re.sub(r'(?<![\w/.])assets/', '/assets/', body)
    page_attr = f' data-page="{pg}"' if pg != "home" else ""
    path = URLS[pg]
    pages = json.dumps({"page": pg, "urls": URLS})
    t, d = html.escape(TITLES[pg]), html.escape(DESCRIPTIONS[pg])
    head = f"""<!doctype html>
<html lang="en"{page_attr}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{d}">
<meta name="theme-color" content="#11264a">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Ferro Building Systems">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/assets/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="The Ferro F mark over a blue-toned steel building frame">
<meta name="twitter:card" content="summary_large_image">
<script>window.FERRO_PAGES = {pages};</script>
<style>
:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}
body{{margin:0;font:14px/1.4 system-ui,sans-serif}}
img{{max-width:100%}}
[hidden]{{display:none!important}}
</style>
"""
    split = body.index('<header class="nav"')
    return head + body[:split].rstrip() + "\n</head>\n<body>\n" + body[split:].rstrip() + "\n</body>\n</html>\n"


for pg, path in URLS.items():
    out = root / path.strip("/") / "index.html" if path != "/" else root / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(host_page(pg), encoding="utf-8")
    print(f"wrote {out.relative_to(root)}")

for old, new in OLD.items():
    out = root / old.strip("/") / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f'<!doctype html><meta charset="utf-8"><title>Ferro</title><link rel="canonical" href="{SITE}{new}">'
                   f'<meta http-equiv="refresh" content="0; url={new}"><a href="{new}">Continue to Ferro</a>\n', encoding="utf-8")
    print(f"wrote {out.relative_to(root)} (redirect)")
