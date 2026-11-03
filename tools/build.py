"""Build the site pages from src/page.html.

src/page.html is the page body as published to the claude.ai preview (that host wraps it in a
document skeleton, and switches skins with #navy). This adds the same skeleton and writes one page
per skin, each at its own URL so review tools such as markup.io keep their comments apart:

    /          classic skin (white header)   -> index.html
    /navy/     navy skin                      -> navy/index.html

Asset paths are made root-absolute so the logo can switch skins in place with history.pushState.
Run from the repo root:  python3 tools/build.py
"""
import pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent

# social previews need absolute URLs; change this when the site moves to its own domain
SITE = "https://ferro.rd-bannon.workers.dev"
ROUTES = {"classic": "/", "navy": "/navy/"}

page = (root / "src" / "page.html").read_text(encoding="utf-8")
# the preview-only viewport hint isn't needed outside claude.ai
page = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\n?', "", page)
# root-absolute asset paths (src, srcset, poster, CSS url())
page = re.sub(r'(?<![\w/.])assets/', '/assets/', page)


def build(skin: str) -> str:
    path = ROUTES[skin]
    html_attr = ' data-skin="navy"' if skin == "navy" else ""
    head = f"""<!doctype html>
<html lang="en"{html_attr}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Ferro Building Systems designs and builds custom pre-engineered steel buildings, backed by a five-year workmanship warranty.">
<meta name="theme-color" content="{'#11264a' if skin == 'navy' else '#ffffff'}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Ferro Building Systems">
<meta property="og:title" content="Ferro — Steel Building Systems">
<meta property="og:description" content="Custom pre-engineered steel buildings, backed by a five-year workmanship warranty.">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/assets/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="The Ferro F mark over a blue-toned steel building frame">
<meta name="twitter:card" content="summary_large_image">
<script>window.FERRO_ROUTES = {{"classic": "{ROUTES['classic']}", "navy": "{ROUTES['navy']}"}};</script>
<style>
:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}
body{{margin:0;font:14px/1.4 system-ui,sans-serif}}
img{{max-width:100%}}
[hidden]{{display:none!important}}
</style>
"""
    # <title>, font links and the page <style> belong in <head>; everything from the header on is <body>
    split = page.index('<header class="nav"')
    return head + page[:split].rstrip() + "\n</head>\n<body>\n" + page[split:].rstrip() + "\n</body>\n</html>\n"


for skin, path in ROUTES.items():
    out = root / path.strip("/") / "index.html" if path != "/" else root / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    html = build(skin)
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out.relative_to(root)} ({skin})", len(html), "bytes")
