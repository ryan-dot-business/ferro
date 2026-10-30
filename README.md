# Ferro Building Systems: home page

A build of the Ferro home page from the Figma file "Ferro", with its nav and motion layer.

## What's in it

- **Nav**: one dropdown box that reshapes between Services, Projects and Company and cross-fades its content. It hangs seamlessly from the hovered button, with a shadow on three sides. In Projects and Company, a caret tracks the hovered link and the photo swaps; Cloverdale plays a drone clip. Links show an arrow on hover.
- **Load**: nav items drop in, the hero photo settles from a slight inset, then the headline, subhead and buttons rise in sequence.
- **Scroll**: the two image bands parallax through their extra height, and the hero copy sinks and fades as it leaves. The services band's columns rise up left to right, and the sector cards and headings rise in.
- **How we build better**: hovering a service slides its photo out of its tile into the slot to its left, unfolds its description and dims the other tiles. On touch screens and narrow layouts, each service shows its own photo and copy instead.
- **Mobile**: a full-screen menu sheet with accordions, stacked services and a swipeable sectors row.

No frameworks or libraries. Respects `prefers-reduced-motion`.

## Run it locally

```sh
python3 -m http.server
# open http://localhost:8000
```

## Edit and rebuild

`index.html` is generated. Edit `src/page.html`, then run:

```sh
python3 tools/build.py
```

| Path | What it is |
|---|---|
| `src/page.html` | markup, styles and page script |
| `assets/` | photos, project clip, icons, favicon, `og-image.jpg` (1200×630 social preview) |
| `source/brand/` | original logo and icon SVGs (gold) |
| `wrangler.jsonc` | Cloudflare Workers static-assets config |

## Still to come

- Commuters Sans and Whitney web fonts (Archivo and Figtree stand in for now)
- Real description copy for each service, and destinations for the nav links
