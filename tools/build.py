"""Build the site from src/.

Sources
  src/page.html       the home page, plus everything shared: head, styles, nav, footer, script
  src/why-ferro.html  the Why Ferro page's <main>

Outputs
  index.html                 /             home
  why-ferro/index.html       /why-ferro/   Why Ferro
  navy/..., navy/why-ferro/  redirects from the retired two-theme URLs
  build/preview.html         the claude.ai preview: both pages in one file, switched with #home / #why-ferro

Host pages use root-absolute asset paths so they work at any depth.
Run from the repo root:  python3 tools/build.py
"""
import json, pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent

# social previews need absolute URLs; change this when the site moves to its own domain
SITE = "https://ferro.rd-bannon.workers.dev"
URLS = {"home": "/", "why-ferro": "/why-ferro/"}
OLD = {"/navy/": "/", "/navy/why-ferro/": "/why-ferro/"}   # retired theme URLs that may still carry review comments
TITLES = {"home": "Ferro — Steel Building Systems", "why-ferro": "Why Ferro — Ferro Steel Building Systems"}
DESCRIPTIONS = {
    "home": "Ferro Building Systems designs and builds custom pre-engineered steel buildings, backed by a five-year workmanship warranty.",
    "why-ferro": "Ferro brings certainty to complex steel building projects: compliance know-how, built-in quality assurance, responsible planning and a proven process.",
}

page = (root / "src" / "page.html").read_text(encoding="utf-8")
why_main = (root / "src" / "why-ferro.html").read_text(encoding="utf-8").strip()
home_main = re.search(r'<main id="top" data-view="home">.*?</main>', page, re.S).group(0)


def compose(main_html: str) -> str:
    return page.replace(home_main, main_html)


# ---- claude.ai preview: both mains, relative assets ----
(root / "build").mkdir(exist_ok=True)
(root / "build" / "preview.html").write_text(page.replace(home_main, home_main + "\n\n" + why_main), encoding="utf-8")
print("wrote build/preview.html")


def host_page(pg: str) -> str:
    body = compose(home_main if pg == "home" else why_main)
    body = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\n?', "", body)
    body = re.sub(r"<title>.*?</title>", f"<title>{TITLES[pg]}</title>", body, count=1)
    # links between pages point at this skin's URLs (the script keeps them in sync after a skin flip)
    body = re.sub(r'data-page="([\w-]+)" href="[^"]*"', lambda m: f'data-page="{m.group(1)}" href="{URLS[m.group(1)]}"', body)
    body = body.replace('<a class="logo" href="#top"', f'<a class="logo" href="{URLS["home"]}"')
    body = re.sub(r'(?<![\w/.])assets/', '/assets/', body)
    attrs = f' data-page="{pg}"' if pg != "home" else ""
    path = URLS[pg]
    pages = json.dumps({"page": pg, "urls": URLS})
    head = f"""<!doctype html>
<html lang="en"{attrs}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{DESCRIPTIONS[pg]}">
<meta name="theme-color" content="#11264a">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Ferro Building Systems">
<meta property="og:title" content="{TITLES[pg]}">
<meta property="og:description" content="{DESCRIPTIONS[pg]}">
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
