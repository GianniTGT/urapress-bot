"""Zeichnet ZaZu und Sara einmal in allen Posen als PNG (comic_assets/sprites/).

Nur nötig, wenn eine neue Pose dazukommt. Der Bot setzt die Comics danach nur noch
aus diesen fertigen Bildern zusammen – darum sieht ZaZu immer gleich aus.

    python tools/zazu/render_sprites.py      (braucht Playwright + Chromium, nicht auf dem Server)
"""
import json
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "comic_assets" / "sprites"
JS = (Path(__file__).parent / "characters.js").read_text()
SCALE = 2          # Pixel pro Zeichen-Einheit
BOX = 700          # Zeichenfläche in Einheiten, Ursprung in der Mitte

# Name → JavaScript-Aufruf mit Ursprung (0,0)
POSES = {
    "zazu-normal":   "zazuSit(0,0,{mode:'flat'})",
    "zazu-gezuar":   "zazuSit(0,0,{mode:'wide',mouth:'w'})",
    "zazu-merzitur": "zazuSit(0,0,{mode:'grumpy'})",
    "zazu-habitur":  "zazuSit(0,0,{mode:'wide',mouth:'o'})",
    "zazu-putra":    "zazuSit(0,0,{mode:'flat',look:1,paw:true})",
    "zazu-shtrire":  "zazuLie(0,0,{mode:'flat'})",
    "zazu-fle":      "zazuSleep(0,0,{})",
    "zazu-ecen":     "zazuWalk(0,0,{mode:'wide',mouth:'w'})",
    # Version 3 – mehr Ausdruck
    "zazu-mbeshtetur": "zazuLean(0,0,{mode:'half',mouth:'flat'})",
    "zazu-mbeshtetur-kenaqur": "zazuLean(0,0,{mode:'half',mouth:'smirk'})",
    "zazu-ide":       "zazuIdea(0,0,{mode:'wide',mouth:'w'})",
    "zazu-ha":        "zazuEat(0,0,{mode:'joy',mouth:'open'})",
    "zazu-kuti":      "zazuBox(0,0,{mode:'half',mouth:'flat'})",
    "zazu-kercen":    "zazuJump(0,0,{mode:'wide',mouth:'o'})",
    "zazu-inat":      "zazuCross(0,0,{mode:'grumpy',mouth:'flat',brows:true})",
    "zazu-shpine":    "zazuBack(0,0,{mode:'joy',mouth:'w'})",
    "zazu-qesh":      "zazuIdea(0,0,{mode:'joy',mouth:'grin'})",
    "gianni-normal":   "gianni(0,0,{})",
    "gianni-merzitur": "gianni(0,0,{mouth:'flat',brow:4})",
    "gianni-habitur":  "gianni(0,0,{mouth:'o',brow:-3})",
    "sara-normal":   "sara(0,0,{ball:false})",
    "sara-merzitur": "sara(0,0,{ball:false,mouth:'flat',brow:3})",
    "sara-habitur":  "sara(0,0,{ball:false,mouth:'o'})",
    "sara-topi":     "sara(0,0,{ball:true})",
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {}
    px = BOX * SCALE
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": px, "height": px})
        for name, call in POSES.items():
            font = (ROOT / "comic_assets" / "fonts" / "ComicNeue-700.ttf").as_uri()
            html = (f'<html><head><style>@font-face{{font-family:"Comic Neue";src:url({font})}}</style></head>'
                    f'<body style="margin:0;background:transparent">'
                    f'<svg xmlns="http://www.w3.org/2000/svg" width="{px}" height="{px}" '
                    f'viewBox="{-BOX/2} {-BOX/2} {BOX} {BOX}" id="s"></svg>'
                    f'<script>{{{JS}\ndocument.getElementById("s").innerHTML={call};}}</script></body></html>')
            pg.set_content(html)
            pg.wait_for_timeout(150)
            raw = OUT / f"{name}.png"
            pg.screenshot(path=str(raw), omit_background=True)
            im = Image.open(raw)
            l, t, r, btm = im.getbbox()
            im.crop((l - 2, t - 2, r + 2, btm + 2)).save(raw, optimize=True)
            # Ursprung (0,0) der Zeichnung im zugeschnittenen Bild, in Pixeln
            meta[name] = {"ox": px / 2 - (l - 2), "oy": px / 2 - (t - 2), "top": (t - px / 2) / SCALE}
            print(name, im.size)
        b.close()
    (OUT / "meta.json").write_text(json.dumps({"scale": SCALE, "poses": meta}, indent=1))


if __name__ == "__main__":
    main()
