"""PNG/ICO/JPG aus den Logo-SVGs erzeugen (braucht Playwright + Chromium und Pillow).

    python3 tools/brand/build.py && python3 tools/brand/render.py
"""
import asyncio
import base64
import io
from pathlib import Path

from PIL import Image
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent / "theme" / "urapress" / "assets" / "brand"
FONT600 = base64.b64encode((HERE / "fonts" / "source-sans-3-latin-600-normal.woff").read_bytes()).decode()


def page(body: str, w: int, h: int, bg: str = "transparent") -> str:
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>"
            f"@font-face{{font-family:SS;font-weight:600;src:url(data:font/woff;base64,{FONT600}) format('woff')}}"
            f"html,body{{margin:0;width:{w}px;height:{h}px;background:{bg};overflow:hidden}}</style></head>"
            f"<body>{body}</body></html>")


async def shot(pg, html: str, w: int, h: int, path: Path | None = None, omit_bg=True) -> bytes:
    await pg.set_viewport_size({"width": w, "height": h})
    await pg.set_content(html)
    await pg.wait_for_timeout(150)
    png = await pg.screenshot(omit_background=omit_bg, clip={"x": 0, "y": 0, "width": w, "height": h})
    if path:
        path.write_bytes(png)
    return png


def svg(name: str) -> str:
    return (OUT / name).read_text()


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        center = "display:flex;align-items:center;justify-content:center;width:100%;height:100%"

        # Logos als PNG (transparent, 2x)
        for name in ("logo", "logo-white", "logo-mono"):
            s = svg(f"{name}.svg").replace('width="636" height="314"', 'width="1272" height="628"')
            await shot(pg, page(s, 1272, 628), 1272, 628, OUT / f"{name}.png")

        # Icons: gross rendern, dann verkleinern (kleine Fenster rendert Chromium nicht sauber)
        big = Image.open(io.BytesIO(await shot(pg, page(svg("icon.svg"), 512, 512), 512, 512)))
        small = Image.open(io.BytesIO(await shot(pg, page(svg("icon-small.svg"), 512, 512), 512, 512)))
        mask = Image.open(io.BytesIO(await shot(pg, page(svg("icon-maskable.svg"), 512, 512), 512, 512)))
        for n in (16, 32, 48, 180, 192, 512):
            src = small if n <= 32 else big
            src.resize((n, n), Image.LANCZOS).save(OUT / f"icon-{n}.png")
        mask.save(OUT / "icon-maskable-512.png")
        # apple-touch: ohne Transparenz, Apple rundet selbst ab
        mask.resize((180, 180), Image.LANCZOS).convert("RGB").save(OUT / "apple-touch-icon.png")
        icos = [Image.open(OUT / f"icon-{n}.png") for n in (16, 32, 48)]
        icos[2].save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)], append_images=icos[:2])

        # Facebook / WhatsApp Vorschaubild 1200x630
        logo = svg("logo.svg").replace('width="636" height="314"', 'width="760" height="375"')
        og = (f"<div style='{center};flex-direction:column;background:#fff'>{logo}"
              "<div style='font:600 32px SS;letter-spacing:.2em;color:#5A5F69;margin-top:18px'>"
              "URA MES ATDHEUT DHE DIJASPORËS</div></div>"
              "<div style='position:absolute;left:0;right:0;bottom:0;height:14px;background:#D7141A'></div>")
        png = await shot(pg, page(og, 1200, 630, "#fff"), 1200, 630, omit_bg=False)
        Image.open(io.BytesIO(png)).convert("RGB").save(OUT.parent / "og-default.jpg", quality=90)

        await b.close()
    print("ok:", sorted(x.name for x in OUT.iterdir()))


asyncio.run(main())
