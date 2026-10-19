"""Facebook-Seite: einen Beitrag posten (mit Foto, sonst als Link)."""
import logging

import requests

import config

log = logging.getLogger(__name__)
GRAPH = "https://graph.facebook.com/v21.0"


def enabled() -> bool:
    return bool(config.FB_PAGE_ID and config.FB_PAGE_TOKEN)


def post(message: str, link: str, image_url: str | None = None) -> str:
    """Postet auf die Seite. Mit image_url → Foto-Beitrag (Bild gross), sonst Link-Beitrag.
    Gibt die URL des Beitrags zurück."""
    if not enabled():
        raise RuntimeError("Facebook nuk është konfiguruar (FB_PAGE_ID / FB_PAGE_TOKEN në .env)")
    if image_url:
        endpoint = f"{GRAPH}/{config.FB_PAGE_ID}/photos"
        data = {"url": image_url, "caption": message, "access_token": config.FB_PAGE_TOKEN}
    else:
        endpoint = f"{GRAPH}/{config.FB_PAGE_ID}/feed"
        data = {"message": message, "link": link, "access_token": config.FB_PAGE_TOKEN}
    r = requests.post(endpoint, data=data, timeout=30)
    try:
        j = r.json()
    except ValueError:
        j = {}
    if r.status_code >= 400 or "error" in j:
        msg = (j.get("error", {}) or {}).get("message", r.text)
        raise RuntimeError(str(msg)[:300])
    pid = j.get("post_id") or j.get("id") or ""
    return f"https://www.facebook.com/{pid}" if pid else "OK"
