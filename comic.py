"""ZaZu-Comic: setzt aus Text-Zeilen einen Comic-Streifen zusammen.

Eingabe (eine Zeile = ein Bild):
    Sara: ZaZu, hajde të luajmë bowling!
    ZaZu (putra): Një… dy… tre… katër.
    ZaZu (mërzitur): S'ka shans. Gishta të vegjël.

Die Figuren kommen als fertige Bilder aus comic_assets/sprites – sie werden nie neu
gezeichnet, darum sieht ZaZu immer gleich aus. Neue Posen: tools/zazu/render_sprites.py.
"""
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).parent / "comic_assets"
S = 2                      # Pixel pro Einheit (Bild in doppelter Grösse, scharf auf dem Handy)
PANEL = 396
GAP = 6
MAX_PANELS = 4
BG, GROUND, LINE, INK = "#FBE3D6", "#8FB8A6", "#3B312C", "#1a1a1a"

# Stimmung (ohne Akzente, klein) → Pose
MOODS = {
    "zazu": {"": "normal", "normal": "normal", "qete": "normal",
             "gezuar": "gezuar", "lumtur": "gezuar", "qesh": "gezuar",
             "merzitur": "merzitur", "inatosur": "merzitur", "nervoz": "merzitur", "ofenduar": "merzitur",
             "habitur": "habitur", "shokuar": "habitur",
             "putra": "putra", "gishta": "putra", "kemba": "putra",
             "shtrire": "shtrire", "shtrihet": "shtrire", "shtrire ne divan": "shtrire",
             "fle": "fle", "flen": "fle", "gjume": "fle", "ne gjume": "fle",
             "ecen": "ecen", "vrapon": "ecen", "shetit": "ecen", "shkon": "ecen",
             # Version 3
             "mbeshtetur": "mbeshtetur", "ulur": "mbeshtetur", "relaks": "mbeshtetur", "filozof": "mbeshtetur",
             "kenaqur": "mbeshtetur-kenaqur", "dinak": "mbeshtetur-kenaqur", "buzeqesh": "mbeshtetur-kenaqur",
             "ide": "ide", "e kam": "ide", "gisht": "ide",
             "qesh me ze": "qesh", "qeshet": "qesh", "gezim": "qesh", "fiton": "qesh",
             "ha": "ha", "byrek": "ha", "uri": "ha", "ushqim": "ha",
             "kuti": "kuti", "fshehur": "kuti", "fshihet": "kuti",
             "kercen": "kercen", "frikesuar": "kercen", "tmerruar": "kercen", "panik": "kercen",
             "inat": "inat", "krahet kryq": "inat", "ofenduar keq": "inat", "xheloz": "inat",
             "shpine": "shpine", "dembel": "shpine", "lodhur": "shpine", "i vdekur": "shpine"},
    "gianni": {"": "normal", "normal": "normal", "gezuar": "normal", "lumtur": "normal",
               "merzitur": "merzitur", "serioz": "merzitur", "inatosur": "merzitur",
               "habitur": "habitur", "shokuar": "habitur"},
    "sara": {"": "normal", "normal": "normal", "gezuar": "normal", "lumtur": "normal",
             "merzitur": "merzitur", "serioz": "merzitur", "inatosur": "merzitur",
             "habitur": "habitur", "shokuar": "habitur",
             "topi": "topi", "bowling": "topi"},
}
NAMES = {"zazu": "ZaZu", "sara": "Sara", "gianni": "Gianni"}
THINK = ["mendon", "mendim", "mendoj", "ne mendje", "heshtur"]
# Farbiger Hintergrund pro Bild (Wand, Schatten, Boden) – wechselt von Bild zu Bild
PALETTES = [("#C9DCEB", "#B3CBDD", "#7E9FB8"), ("#F5DC8A", "#EBCB6A", "#C9A24A"),
            ("#D9C7E6", "#C7B1D8", "#9A80B3"), ("#BFE0C4", "#A8D0AE", "#7AAE84"),
            ("#F6CDBE", "#EDB7A4", "#C98670")]
ORDER = ["gianni", "sara", "zazu"]   # links → rechts

# Platz im Bild (Einheiten): (Mitte x, Grösse, max. Breite) je nach Anzahl Figuren.
# Alle Figuren stehen auf der gleichen Bodenlinie, egal ob sitzend, liegend oder laufend.
PLACE = {
    1: {"sara": (198, 1.0, 330), "zazu": (198, .9, 340)},
    2: {"sara": (100, .85, 170), "gianni": (100, .85, 170), "zazu": (282, .78, 205)},
    3: {"gianni": (70, .66, 130), "sara": (190, .66, 120), "zazu": (318, .62, 150)},
}
GROUND_Y = 362


class ComicError(ValueError):
    pass


def _plain(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c)).strip()


def parse(text: str) -> list[dict]:
    """Zeilen → [{'who': 'zazu', 'pose': 'putra', 'text': '…'}]. Wirft ComicError mit Hinweis auf Albanisch."""
    panels = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("/"):
            continue
        m = re.match(r"^([^:(]+?)\s*(?:\(([^)]*)\))?\s*:\s*(.+)$", line)
        if not m:
            raise ComicError(f"Nuk e kuptoj rreshtin: «{line}». Shkruaj p.sh. «ZaZu (mërzitur): teksti»")
        who, said = _plain(m.group(1)), m.group(3).strip()
        if who not in MOODS:
            raise ComicError(f"«{m.group(1).strip()}» nuk njihet. Personazhet: ZaZu, Sara, Gianni")
        # «mendon» = Gedankenblase; kann mit einer Pose kombiniert werden: (mbështetur, mendon)
        parts = [_plain(x) for x in (m.group(2) or "").split(",")]
        think = any(x in THINK for x in parts)
        parts = [x for x in parts if x and x not in THINK]
        mood = parts[0] if parts else ""
        if mood not in MOODS[who]:
            known = ", ".join(sorted({k for k in MOODS[who] if k} | set(THINK[:1])))
            raise ComicError(f"Gjendja «{m.group(2)}» nuk njihet për {NAMES[who]}. Mundësitë: {known}")
        panels.append({"who": who, "pose": MOODS[who][mood], "text": said, "think": think})
    if not panels:
        raise ComicError("Mungon teksti. Një rresht = një foto, p.sh. «Sara: ZaZu, hajde!»")
    if len(panels) > MAX_PANELS:
        raise ComicError(f"Maksimum {MAX_PANELS} foto (rreshta) për një skicë.")
    return panels


def _sprites() -> dict:
    return json.loads((ASSETS / "sprites" / "meta.json").read_text())["poses"]


def _font(size: float, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(ASSETS / "fonts" / f"ComicNeue-{700 if bold else 400}.ttf"), int(size * S))


def _wrap(text: str, font, width_px: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        test = f"{cur} {word}".strip()
        if font.getlength(test) <= width_px or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = word
    return lines + ([cur] if cur else [])


def _bubble(draw, text: str, sx: float, head_top: float, all_top: float | None = None) -> None:
    """Sprechblase oben im Bild, über ALLEN Köpfen (verdeckt kein Gesicht), Spitze zeigt auf den Sprecher."""
    limit = min(head_top, all_top if all_top is not None else head_top)
    room = limit - 22 - 14
    for fs in (22, 20, 18, 16, 14):
        font = _font(fs)
        lines = _wrap(text, font, (PANEL - 44) * S)
        lh = fs * 1.18
        h = len(lines) * lh + 22
        if h <= room:
            break
    w = min(PANEL - 20, max(110, max(font.getlength(t) for t in lines) / S + 32))
    x = min(max(sx - w / 2, 10), PANEL - 10 - w)
    y = max(14, limit - 30 - h)      # Blase knapp über dem höchsten Kopf
    bottom = y + h
    bx = min(max(sx, x + 26), x + w - 26)
    tip = (sx, head_top - 6)
    tail = [((bx - 9) * S, (bottom - 4) * S), ((bx + 9) * S, (bottom - 4) * S), (tip[0] * S, tip[1] * S)]
    draw.polygon(tail, fill="white", outline=LINE, width=int(3.5 * S))
    draw.rounded_rectangle((x * S, y * S, (x + w) * S, bottom * S), radius=14 * S, fill="white",
                           outline=LINE, width=int(3.5 * S))
    draw.rectangle(((bx - 6) * S, (bottom - 6) * S, (bx + 6) * S, (bottom + 2) * S), fill="white")
    for i, t in enumerate(lines):
        draw.text(((x + w / 2) * S, (y + 11 + i * lh) * S), t, font=font, fill=INK, anchor="mt")


def _cloud(draw, text: str, sx: float, head_top: float, all_top: float | None = None) -> None:
    """Gedankenblase: Wolke oben, kleine Kreise führen zum Kopf."""
    limit = min(head_top, all_top if all_top is not None else head_top)
    room = limit - 60
    for fs in (22, 20, 18, 16, 14):
        font = _font(fs)
        lines = _wrap(text, font, (PANEL - 76) * S)
        lh = fs * 1.18
        h = len(lines) * lh + 34
        if h <= room:
            break
    w = min(PANEL - 24, max(130, max(font.getlength(t) for t in lines) / S + 56))
    x = min(max(sx - w / 2, 12), PANEL - 12 - w)
    y = max(12, limit - 58 - h)
    lw = int(3.2 * S)
    # Wolke aus Kreisen am Rand + Fläche
    import math
    bumps = max(8, int((w + h) / 26))
    cx, cy, rx, ry = x + w / 2, y + h / 2, w / 2, h / 2
    pts = [(cx + rx * math.cos(2 * math.pi * i / bumps), cy + ry * math.sin(2 * math.pi * i / bumps)) for i in range(bumps)]
    r = max(16, min(rx, ry) * 0.42)
    for px, py in pts:
        draw.ellipse(((px - r) * S, (py - r) * S, (px + r) * S, (py + r) * S), fill="white", outline=LINE, width=lw)
    draw.ellipse(((cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S), fill="white")
    for px, py in pts:
        rr = r - 3.4
        draw.ellipse(((px - rr) * S, (py - rr) * S, (px + rr) * S, (py + rr) * S), fill="white")
    # kleine Kreise zum Kopf
    side = 1 if sx < PANEL - 70 else -1                  # Kreise schräg seitlich zum Kopf, nicht übereinander
    by = y + h + r * 0.55
    for k, rad in enumerate((10, 7, 4.5)):
        qx = sx + side * (34 - k * 12)
        qy = by + 6 + k * max(10, (head_top - 6 - by) / 3)
        draw.ellipse(((qx - rad) * S, (qy - rad) * S, (qx + rad) * S, (qy + rad) * S), fill="white", outline=LINE,
                     width=int(2.6 * S))
    for i, t in enumerate(lines):
        draw.text((cx * S, (cy - len(lines) * lh / 2 + i * lh) * S), t, font=font, fill=INK, anchor="mt")


# Körperhaltungen bleiben, auch wenn die Figur im nächsten Bild nichts sagt (Gesichter nicht)
KEEP = {"shtrire", "fle", "ecen", "topi", "mbeshtetur", "mbeshtetur-kenaqur", "kuti", "shpine"}


def _panel(p: dict, cast: list[str], meta: dict, last: dict | None = None, idx: int = 0) -> Image.Image:
    wall, shade, floor = PALETTES[idx % len(PALETTES)]
    im = Image.new("RGB", (PANEL * S, PANEL * S), wall)
    d = ImageDraw.Draw(im)
    # Schattenkeil an der Wand (Tiefe) und Boden
    d.polygon(((0, 250 * S), (PANEL * S, 205 * S), (PANEL * S, 318 * S), (0, 318 * S)), fill=shade)
    for yy in range(214, 318, 9):                        # feine Punkte wie Raster im Zeitungs-Comic
        for xx in range(4 + (yy // 9 % 2) * 4, PANEL, 9):
            if yy > 250 - xx * 45 / PANEL:
                d.ellipse(((xx - 1.1) * S, (yy - 1.1) * S, (xx + 1.1) * S, (yy + 1.1) * S), fill=floor)
    d.rectangle((0, 318 * S, PANEL * S, PANEL * S), fill=floor)
    place = dict(PLACE[len(cast)])
    if len(cast) == 2 and "zazu" not in cast:                 # Gianni und Sara: Sara rechts
        place["sara"] = (282, .85, 170)
    head_top = None
    tops: list[float] = []
    for who in cast:
        pose = p["pose"] if who == p["who"] else ((last or {}).get(who) if (last or {}).get(who) in KEEP else "normal")
        name = f"{who}-{pose}"
        cx, sc, max_w = place[who]
        m = meta[name]
        sp = Image.open(ASSETS / "sprites" / f"{name}.png")
        sc = min(sc, max_w * S / sp.width)               # breite Posen (liegend, laufend) kleiner
        w, h = round(sp.width * sc), round(sp.height * sc)
        sp = sp.resize((w, h), Image.LANCZOS)
        left = round(cx * S - w / 2)                     # Figur mittig auf ihrem Platz
        top = round(GROUND_Y * S - h)                    # unten auf der Bodenlinie
        im.paste(sp, (left, top), sp)
        ox, oy = (left + m["ox"] * sc) / S, (top + m["oy"] * sc) / S   # Kopfmitte
        tops.append(oy + m["top"] * sc)
        if who == p["who"]:
            head_top, sx = oy + m["top"] * sc, ox
    (_cloud if p.get("think") else _bubble)(d, p["text"], sx, head_top, min(tops))
    d.rectangle((0, 0, PANEL * S - 1, PANEL * S - 1), outline=INK, width=5 * S)
    return im


def render(panels: list[dict], out: Path, day: date | None = None) -> Path:
    meta = _sprites()
    cast = [w for w in ORDER if any(p["who"] == w for p in panels)]
    n = len(panels)
    width = 20 + n * (PANEL + GAP) - GAP
    im = Image.new("RGB", (width * S, 476 * S), "white")
    d = ImageDraw.Draw(im)
    d.text((10 * S, 40 * S), "ZaZu", font=_font(34), fill=LINE, anchor="ls")
    day = day or date.today()
    d.text((10 * S + _font(34).getlength("ZaZu") + 14 * S, 40 * S), f"nga UraPress · {day:%d.%m.%Y}",
           font=_font(20, bold=False), fill="#777777", anchor="ls")
    last: dict = {}
    for i, p in enumerate(panels):
        im.paste(_panel(p, cast, meta, last, i), ((10 + i * (PANEL + GAP)) * S, 60 * S))
        last[p["who"]] = p["pose"]
    d.text(((width - 10) * S, 468 * S), "© UraPress · ZaZu", font=_font(14, bold=False), fill="#999999", anchor="rs")
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, optimize=True)
    return out


def alt_text(panels: list[dict]) -> str:
    return " / ".join(f"{NAMES[p['who']]}: {p['text']}" for p in panels)
