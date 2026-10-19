"""Zentrale Konfiguration – alle Werte kommen aus der Datei .env"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _get(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(f"Wert fehlt in .env: {name}")
    return value or ""


# --- Telegram ---------------------------------------------------------------
TELEGRAM_BOT_TOKEN = _get("TELEGRAM_BOT_TOKEN", required=True)
# Chat, in den die Vorschläge geschickt werden (deine User-ID oder eine Gruppe)
TELEGRAM_CHAT_ID = int(_get("TELEGRAM_CHAT_ID", "0") or 0)
# Wer darf Posto/Refuzo drücken? Standard: nur TELEGRAM_CHAT_ID
TELEGRAM_ADMIN_IDS = {
    int(x) for x in _get("TELEGRAM_ADMIN_IDS", "").replace(" ", "").split(",") if x
} or ({TELEGRAM_CHAT_ID} if TELEGRAM_CHAT_ID else set())

# --- KI Text (Claude) -------------------------------------------------------
ANTHROPIC_API_KEY = _get("ANTHROPIC_API_KEY", required=True)
ANTHROPIC_MODEL = _get("ANTHROPIC_MODEL", "claude-sonnet-5-5")

# --- KI Bild (optional) -----------------------------------------------------
OPENAI_API_KEY = _get("OPENAI_API_KEY", "")
OPENAI_IMAGE_MODEL = _get("OPENAI_IMAGE_MODEL", "gpt-image-1")
AI_IMAGE_CAPTION = "Foto ilustruese (AI)"

# --- WordPress --------------------------------------------------------------
WP_URL = _get("WP_URL", "").rstrip("/")
WP_USER = _get("WP_USER", "")
WP_APP_PASSWORD = _get("WP_APP_PASSWORD", "")
POST_STATUS = _get("POST_STATUS", "publish")  # publish | draft

# --- Quellen & Ablauf -------------------------------------------------------
FEEDS = [f.strip() for f in _get(
    "FEEDS",
    "https://shtegu.com/feed/,https://lajmpress.org/feed/,https://alsat.mk/feed/,https://portalix.mk/api/rss.xml",

).split(",") if f.strip()]
SCAN_TIME = _get("SCAN_TIME", "07:30")          # HH:MM
TIMEZONE = _get("TIMEZONE", "Europe/Zurich")
ARTICLES_PER_DAY = int(_get("ARTICLES_PER_DAY", "3"))
MAX_AGE_HOURS = int(_get("MAX_AGE_HOURS", "48"))
CATEGORIES = [c.strip() for c in _get(
    "CATEGORIES",
    "Zvicër,Diaspora,Kosovë,Shqipëri,Maqedoni e Veriut,Mal i Zi,Lugina e Preshevës,Bota,Ekonomi,Sport,Kulturë & Showbiz",
).split(",") if c.strip()]

# --- Speicher ---------------------------------------------------------------
DATA_DIR = Path(_get("DATA_DIR", str(BASE_DIR / "data")))
IMAGE_DIR = DATA_DIR / "images"
DB_PATH = DATA_DIR / "urapress.db"
DATA_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_DIR.mkdir(parents=True, exist_ok=True)
