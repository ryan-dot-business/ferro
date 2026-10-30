"""Build index.html from src/page.html.

src/page.html is the page body as published to the claude.ai preview (that host wraps it in a
document skeleton). This adds the same skeleton so the repo's index.html runs on any static host.
Run from the repo root:  python3 tools/build.py
"""
import pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent
page = (root / "src" / "page.html").read_text(encoding="utf-8")

# the preview-only viewport hint isn't needed outside claude.ai
page = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\n?', "", page)

head = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Ferro Building Systems designs and builds custom pre-engineered steel buildings, backed by a five-year workmanship warranty.">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<style>
:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;font:14px/1.4 system-ui,sans-serif}
img{max-width:100%}
[hidden]{display:none!important}
</style>
"""
# <title>, font links and the page <style> belong in <head>; everything from the header on is <body>
split = page.index('<header class="nav"')
out = head + page[:split].rstrip() + "\n</head>\n<body>\n" + page[split:].rstrip() + "\n</body>\n</html>\n"
(root / "index.html").write_text(out, encoding="utf-8")
print("wrote index.html", len(out), "bytes")
