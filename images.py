"""Bildlogik: zuerst Personenfoto aus der WP-Mediathek, sonst KI-Symbolbild."""
import base64
import io
import logging
import unicodedata
from pathlib import Path

from PIL import Image

from config import IMAGE_DIR, OPENAI_API_KEY, OPENAI_IMAGE_MODEL
from wordpress import WordPress

log = logging.getLogger(__name__)

STYLE = ("Realistic editorial news photograph, natural light, documentary style, 3:2. "
         "No text, no letters, no logos, no watermarks, no recognizable real people. Scene: ")


def _norm(s: str) -> str:
    """'Albin Kurti' == 'albin kurti' == 'Albin  Kurtí' – Akzente/ë/ç ignorieren."""
    s = unicodedata.normalize("NFKD", s or "")
    return " ".join("".join(c for c in s if not unicodedata.combining(c)).casefold().split())


def find_person_photo(wp: WordPress, person: str) -> dict | None:
    """Sucht ein Bild, dessen Titel exakt dem Namen der Person entspricht."""
    try:
        results = wp.search_media(person)
    except Exception as exc:
        log.warning("Mediathek-Suche fehlgeschlagen: %s", exc)
        return None
    target = _norm(person)
    for m in results:
        if _norm(m.get("title", {}).get("rendered", "")) == target:
            return m
    return None


def generate_ai_image(prompt: str, name: str) -> Path | None:
    if not OPENAI_API_KEY:
        log.info("Kein OPENAI_API_KEY – kein KI-Bild")
        return None
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    res = client.images.generate(model=OPENAI_IMAGE_MODEL, prompt=STYLE + prompt,
                                 size="1536x1024", n=1)
    raw = base64.b64decode(res.data[0].b64_json)
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    path = IMAGE_DIR / f"{name}.jpg"
    img.save(path, "JPEG", quality=85, optimize=True)
    return path
