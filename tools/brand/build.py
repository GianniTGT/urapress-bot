"""UraPress Logo-Palette erzeugen (Variante 5 · Hängebrücke).

Schriftzug „urapress" = Fahrbahn, roter Bogen oben trägt ihn mit feinen Seilen.
Erzeugt SVG-Dateien. PNG/ICO/JPG macht render.py (Chromium).

    python3 tools/brand/build.py
"""
import math
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent / "theme" / "urapress" / "assets" / "brand"
OUT.mkdir(parents=True, exist_ok=True)

RED, INK = "#D7141A", "#16181D"
font = TTFont(HERE / "fonts" / "source-sans-3-latin-900-normal.woff")
gs, cmap = font.getGlyphSet(), font.getBestCmap()
UPM = font["head"].unitsPerEm
XH = font["OS/2"].sxHeight          # Höhe der Kleinbuchstaben
DESC = -font["hhea"].descent        # Unterlänge (p)
TRACK = -0.03 * UPM                 # wie auf der Website (letter-spacing -0.03em)


def word_paths(word: str, size: float, x0: float, base: float):
    """Gibt [(Buchstabe, SVG-Pfad, x, Breite)] und die Gesamtbreite zurück."""
    s = size / UPM
    out, x = [], x0
    for i, ch in enumerate(word):
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x, base)))
        adv = gs[g].width * s
        out.append((ch, pen.getCommands(), x, adv))
        x += adv + (TRACK * s if i < len(word) - 1 else 0)
    return out, x - x0


def bridge(size: float, pad: float, colors: dict, arch_h: float = 0.62):
    """Logo als SVG-Text. size = Schriftgrösse in px. colors: ura, press, arch, cable, dot."""
    s = size / UPM
    xh = XH * s
    top_gap = 0.20 * size           # Raum zwischen Seil-Ende und Buchstaben
    rise = arch_h * size            # Höhe des Bogens über der Fahrbahn
    deck = pad + rise + top_gap     # y der Seil-Enden (knapp über den Buchstaben)
    base = deck + 0.06 * size + xh  # Grundlinie
    glyphs, tw = word_paths("urapress", size, pad, base)
    x0, x1 = pad - 0.02 * size, pad + tw + 0.02 * size
    W = tw + 2 * pad
    H = base + DESC * s + pad * 0.6
    stroke = max(0.075 * size, 2.2)
    cable = max(0.026 * size, 1.1)
    r = max(0.085 * size, 2.4)

    def arch_y(x):
        t = (x - x0) / (x1 - x0)
        return deck - rise * math.sin(math.pi * t)

    pts = " ".join(f"{x0 + (x1 - x0) * i / 80:.2f},{arch_y(x0 + (x1 - x0) * i / 80):.2f}" for i in range(81))
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.1f} {H:.1f}" width="{W:.0f}" height="{H:.0f}" role="img" aria-label="UraPress">']
    # Seile zuerst (liegen hinter dem Bogen)
    for ch, d, x, adv in glyphs:
        cx = x + adv / 2
        parts.append(f'<line x1="{cx:.2f}" y1="{arch_y(cx):.2f}" x2="{cx:.2f}" y2="{deck:.2f}" stroke="{colors["cable"]}" stroke-width="{cable:.2f}" stroke-linecap="round"/>')
    parts.append(f'<polyline points="{pts}" fill="none" stroke="{colors["arch"]}" stroke-width="{stroke:.2f}" stroke-linecap="round" stroke-linejoin="round"/>')
    for x in (x0, x1):
        parts.append(f'<circle cx="{x:.2f}" cy="{deck:.2f}" r="{r:.2f}" fill="{colors["dot"]}"/>')
    for i, (ch, d, x, adv) in enumerate(glyphs):
        parts.append(f'<path d="{d}" fill="{colors["ura"] if i < 3 else colors["press"]}"/>')
    parts.append("</svg>")
    return "\n".join(parts), W, H


def icon(colors_bg=RED, fg="#FFFFFF", size=512, cables=5, rounded=True, bold=False):
    """Quadratisches Zeichen: flacher Brückenbogen mit Seilen über der Fahrbahn, auf rotem Grund.
    bold=True: dickere Linien, für 16/32 px."""
    S = size
    m = S * (0.15 if bold else 0.16)
    deck = S * (0.64 if bold else 0.62)
    x0, x1 = m, S - m
    rise = S * (0.30 if bold else 0.28)
    w_arch = S * (0.11 if bold else 0.07)
    w_cable = S * 0.032

    def ay(x):
        return deck - rise * math.sin(math.pi * (x - x0) / (x1 - x0))
    pts = " ".join(f"{x0 + (x1 - x0) * i / 60:.2f},{ay(x0 + (x1 - x0) * i / 60):.2f}" for i in range(61))
    cab = "".join(
        f'<line x1="{x:.2f}" y1="{ay(x):.2f}" x2="{x:.2f}" y2="{deck:.2f}" stroke="{fg}" stroke-width="{w_cable:.2f}" stroke-linecap="round"/>'
        for x in [x0 + (x1 - x0) * k / (cables + 1) for k in range(1, cables + 1)])
    rx = f"{S*0.22:.1f}" if rounded else "0"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}">'
            f'<rect width="{S}" height="{S}" rx="{rx}" fill="{colors_bg}"/>{cab}'
            f'<polyline points="{pts}" fill="none" stroke="{fg}" stroke-width="{w_arch:.2f}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<line x1="{x0:.2f}" y1="{deck:.2f}" x2="{x1:.2f}" y2="{deck:.2f}" stroke="{fg}" stroke-width="{w_arch:.2f}" stroke-linecap="round"/>'
            "</svg>")


VARIANTS = {
    "logo": dict(ura=RED, press=INK, arch=RED, cable=INK, dot=INK),
    "logo-white": dict(ura=RED, press="#FFFFFF", arch=RED, cable="#FFFFFF", dot="#FFFFFF"),
    "logo-mono": dict(ura=INK, press=INK, arch=INK, cable=INK, dot=INK),
    # für die Website: "press", Seile und Punkte folgen der Textfarbe (Kopf dunkel, Fuss weiss)
    "logo-inline": dict(ura=RED, press="currentColor", arch=RED, cable="currentColor", dot="currentColor"),
}

if __name__ == "__main__":
    for name, col in VARIANTS.items():
        svg, W, H = bridge(160, 18, col)
        (OUT / f"{name}.svg").write_text(svg)
        print(name, f"{W:.0f}x{H:.0f}")
    (OUT / "icon.svg").write_text(icon())
    (OUT / "icon-small.svg").write_text(icon(cables=0, bold=True))
    (OUT / "icon-maskable.svg").write_text(icon(rounded=False))
    print("icon.svg")
