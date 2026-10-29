"""RSS-Quellen einlesen und Kandidaten liefern."""
import logging
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import feedparser
import requests
from bs4 import BeautifulSoup

import db

log = logging.getLogger(__name__)
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; urapress-bot/1.0; +https://urapress.ch)"}
BROWSER_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                 "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
MIN_TEXT_LENGTH = 300   # darunter gilt der Feed-Text als Anriss → Volltext von der Webseite
MAX_PER_FEED = 12       # nur die neuesten Einträge pro Quelle (viele Quellen → Auswahl bleibt überschaubar)


def normalize_link(link: str) -> str:
    """Entfernt utm_*-Parameter, damit derselbe Artikel nicht doppelt erkannt wird.
    Bing-News-Links (…/apiclick.aspx?url=…) werden auf die echte Artikel-Adresse aufgelöst."""
    p = urlparse(link)
    if p.netloc.endswith("bing.com") and "url=" in p.query:
        real = dict(parse_qsl(p.query)).get("url")
        if real:
            p = urlparse(real)
    query = [(k, v) for k, v in parse_qsl(p.query) if not k.lower().startswith("utm_")]
    return urlunparse(p._replace(query=urlencode(query), fragment=""))


def source_name(link: str) -> str:
    return urlparse(link).netloc.removeprefix("www.")


def clean_html(raw: str) -> str:
    soup = BeautifulSoup(raw or "", "html.parser")
    for tag in soup(["script", "style", "figure", "img", "aside", "header", "iframe"]):
        tag.decompose()
    blocks = [el.get_text(" ", strip=True) for el in soup.find_all(["p", "h2", "h3", "li"])]
    text = "\n\n".join(b for b in blocks if b) or soup.get_text("\n", strip=True)
    # WordPress-Fusszeile "The post ... appeared first on ..." entfernen
    text = re.sub(r"\n*The post .*? appeared first on .*?$", "", text, flags=re.S | re.M)
    return re.sub(r"[ \u00a0]+", " ", text).strip()


def _entry_date(entry) -> datetime | None:
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    return datetime(*t[:6], tzinfo=timezone.utc) if t else None


def fetch_feed(url: str) -> list:
    resp = requests.get(url, headers=HEADERS, timeout=25)
    if resp.status_code == 403:  # manche Seiten (Top Channel, Panorama …) blocken Bot-Namen
        resp = requests.get(url, headers=BROWSER_HEADERS, timeout=25)
    resp.raise_for_status()
    return feedparser.parse(resp.content).entries


def fetch_candidates(feeds: list[str], max_age_hours: int, max_per_feed: int = MAX_PER_FEED,
                     group: str = "") -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    candidates: list[dict] = []
    for url in feeds:
        try:
            entries = fetch_feed(url)
        except Exception as exc:  # eine kaputte Quelle soll den Rest nicht stoppen
            log.warning("Feed nicht lesbar: %s (%s)", url, exc)
            continue
        for e in entries[:max_per_feed]:
            link = normalize_link(e.get("link", ""))
            if not link or db.is_seen(link):
                continue
            published = _entry_date(e)
            if published and published < cutoff:
                continue
            raw = (e.get("content") or [{}])[0].get("value") or e.get("summary", "")
            text = clean_html(raw)
            if not e.get("title"):
                continue
            candidates.append({
                "title": BeautifulSoup(e.get("title", ""), "html.parser").get_text().strip(),
                "link": link,
                "source": source_name(link),
                "published": published.isoformat() if published else "",
                "categories": [t.get("term", "") for t in e.get("tags", [])],
                "text": text,
                "needs_fulltext": len(text) < MIN_TEXT_LENGTH,
                "group": group,
            })
        log.info("%s: %d Einträge gelesen", url, len(entries))
    log.info("Kandidaten gesamt: %d", len(candidates))
    return candidates


def fetch_fulltext(url: str) -> str:
    """Lädt die Artikelseite und extrahiert nur den Artikeltext (ohne Menü, Werbung, Kommentare)."""
    import trafilatura

    resp = requests.get(url, headers=HEADERS, timeout=25)
    if resp.status_code == 403:  # manche Seiten blocken Bot-Namen, Browser-Kennung wird akzeptiert
        resp = requests.get(url, headers=BROWSER_HEADERS, timeout=25)
    resp.raise_for_status()
    text = trafilatura.extract(resp.text, include_comments=False, include_tables=False,
                               favor_precision=True) or ""
    return text.strip()


def ensure_fulltext(story: dict) -> dict:
    """Ergänzt den Volltext, falls der Feed nur einen Anriss liefert. Wirft Fehler, wenn zu kurz."""
    if story.get("needs_fulltext"):
        try:
            full = fetch_fulltext(story["link"])
            if len(full) > len(story["text"]):
                story["text"] = full
        except Exception as exc:  # Volltext nicht ladbar → Feed-Text verwenden, falls lang genug
            log.warning("Volltext nicht ladbar, nutze Feed-Text: %s (%s)", story["link"], exc)
        story["needs_fulltext"] = False
    if len(story["text"]) < MIN_TEXT_LENGTH:
        raise ValueError("Artikeltext zu kurz (nur Anriss verfügbar)")
    return story
