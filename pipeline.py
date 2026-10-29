"""Ablauf: Quellen → Auswahl → Neu schreiben → Bild → Entwurf; und Veröffentlichung."""
import html
import logging
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import ai_writer
import db
import feeds
import images
from config import (AI_IMAGE_CAPTION, ARTICLES_PER_DAY, CH_FEEDS, CH_MAX_PER_FEED, FEEDS, MAX_AGE_HOURS,
                    MAX_GENERAL_PER_SCAN, OTHER_MAX_PER_FEED, POST_STATUS)
from wordpress import WordPress

log = logging.getLogger(__name__)


def _wp_or_none() -> WordPress | None:
    try:
        return WordPress()
    except Exception as exc:
        log.warning("WordPress nicht verfügbar: %s", exc)
        return None


def gather_candidates() -> list[dict]:
    """Schweizer Quellen zuerst (mehr Einträge), danach Balkan/Welt (weniger Einträge). Doppelte Links weg."""
    ch_set = set(CH_FEEDS)
    out = feeds.fetch_candidates(CH_FEEDS, MAX_AGE_HOURS, CH_MAX_PER_FEED, group="ch")
    out += feeds.fetch_candidates([f for f in FEEDS if f not in ch_set], MAX_AGE_HOURS, OTHER_MAX_PER_FEED,
                                  group="other")
    seen, unique = set(), []
    for c in out:
        if c["link"] not in seen:
            seen.add(c["link"])
            unique.append(c)
    return unique


def build_drafts(theme: str | None = None) -> tuple[list[int], list[str]]:
    """Gibt (Entwurfs-IDs, Fehlermeldungen) zurück. theme: optionales Thema für die Auswahl."""
    errors: list[str] = []
    candidates = gather_candidates()
    if not candidates:
        return [], errors

    picks = ai_writer.select_stories(candidates, ARTICLES_PER_DAY, db.recent_titles(), theme=theme,
                                     max_general=MAX_GENERAL_PER_SCAN)
    wp = _wp_or_none()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    ids: list[int] = []

    for i, story in enumerate(picks):
        db.mark_seen(story["link"], story["title"], story["source"])
        try:
            ids.append(_make_draft(story, wp, f"{stamp}-{i}", errors))
        except Exception as exc:
            log.exception("Fehler bei %s", story["link"])
            errors.append(f"«{story['title']}» konnte nicht verarbeitet werden: {exc}")
    return ids, errors


def _make_draft(story: dict, wp, stamp: str, errors: list[str]) -> int:
    """Eine Meldung: Volltext holen, neu schreiben, Foto suchen/erzeugen, als Entwurf speichern."""
    story = feeds.ensure_fulltext(story)
    art = ai_writer.rewrite(story)

    image_kind, image_ref, media_id = "none", None, None
    if art["persona"] and wp:
        media = images.find_person_photo(wp, art["persona"])
        if media:
            image_kind, image_ref, media_id = "wp", media["source_url"], media["id"]
    if image_kind == "none":
        try:
            path = images.generate_ai_image(art.get("prompt_imazhi") or art["titulli"], f"ai-{stamp}")
            if path:
                image_kind, image_ref = "ai", str(path)
        except Exception as exc:
            errors.append(f"KI-Bild für «{art['titulli']}» fehlgeschlagen: {exc}")

    return db.add_draft({
        "source_name": story["source"],
        "source_link": story["link"],
        "title": art["titulli"],
        "excerpt": art.get("permbledhja", ""),
        "paragraphs": art["paragrafet"],
        "category": art["kategoria"],
        "tags": art.get("etiketat", [])[:5],
        "person": art["persona"],
        "image_kind": image_kind,
        "image_ref": image_ref,
        "wp_media_id": media_id,
        "priority": story.get("prioriteti"),
        "reason": story.get("pse"),
        "kind": story.get("kind", "lajm"),
    })


def next_guide_key() -> str | None:
    """Nächster Udhëzues, der noch nie vorgeschlagen wurde (Reihenfolge wie in GUIDES)."""
    for key in ai_writer.GUIDES:
        if not db.guide_done(key):
            return key
    return None


def build_guide(key: str) -> tuple[int, list[str]]:
    """Praktischer Ratgeber aus offiziellen Seiten (SEM, Bund, Kanton). Gibt (Entwurfs-ID, Hinweise) zurück."""
    g = ai_writer.GUIDES[key]
    texts = []
    for u in g["urls"]:
        try:
            t = feeds.fetch_fulltext(u)
            if len(t) > 300:
                texts.append((u, t))
        except Exception as exc:
            log.warning("Offizielle Seite nicht lesbar: %s (%s)", u, exc)
    if not texts:
        raise ValueError("Faqet zyrtare nuk u lexuan dot – udhëzuesi nuk u shkrua.")
    art = ai_writer.write_guide(key, texts)
    errors: list[str] = []
    stamp = "guide-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    image_kind, image_ref = "none", None
    try:
        path = images.generate_ai_image(art.get("prompt_imazhi") or art["titulli"], f"ai-{stamp}")
        if path:
            image_kind, image_ref = "ai", str(path)
    except Exception as exc:
        errors.append(f"KI-Bild für «{art['titulli']}» fehlgeschlagen: {exc}")
    db.mark_seen(f"udhezues:{key}", art["titulli"], "udhezues")
    draft_id = db.add_draft({
        "source_name": urlparse(texts[0][0]).netloc.removeprefix("www."),
        "source_link": texts[0][0],
        "title": art["titulli"],
        "excerpt": art.get("permbledhja", ""),
        "paragraphs": art["paragrafet"],
        "category": "Zvicër",
        "tags": art.get("etiketat", [])[:5],
        "person": None,
        "image_kind": image_kind,
        "image_ref": image_ref,
        "wp_media_id": None,
        "priority": 1,
        "reason": "Udhëzues praktik (Google-Suche)",
        "kind": "udhezues",
    })
    return draft_id, errors


def build_from_link(url: str) -> tuple[int, list[str]]:
    """Eine Meldung aus einem Link (z. B. 20min.ch) neu schreiben. Gibt (Entwurfs-ID, Hinweise) zurück."""
    import requests
    from bs4 import BeautifulSoup

    link = feeds.normalize_link(url)
    resp = requests.get(link, headers=feeds.BROWSER_HEADERS, timeout=25)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    og = soup.find("meta", property="og:title")
    title = (og.get("content") if og else "") or (soup.title.get_text() if soup.title else "")
    text = feeds.fetch_fulltext(link)
    if len(text) < 200:
        raise ValueError("Nga kjo faqe nuk u lexua dot teksti i artikullit (ndoshta me pagesë ose i bllokuar).")
    story = {"title": title.strip(), "link": link, "source": feeds.source_name(link), "published": "",
             "categories": [], "text": text, "needs_fulltext": False}
    db.mark_seen(link, story["title"], story["source"])
    errors: list[str] = []
    draft_id = _make_draft(story, _wp_or_none(), "link-" + datetime.now().strftime("%Y%m%d-%H%M%S"), errors)
    return draft_id, errors


# Beiträge aus sozialen Netzen: Text schreibt die Redaktion, der Original-Beitrag wird eingebettet
SOCIAL = {"instagram.com": "Instagram", "x.com": "X", "twitter.com": "X", "tiktok.com": "TikTok"}


def social_platform(url: str) -> str | None:
    host = urlparse(url or "").netloc.lower().removeprefix("www.").removeprefix("m.").removeprefix("vm.")
    return SOCIAL.get(host)


def social_embed(url: str) -> str:
    """Offizieller Einbettungs-Code der Plattform: Bild/Video kommt live von dort, wird nicht kopiert."""
    u = html.escape(url)
    kind = social_platform(url)
    if kind == "Instagram":
        return (f'<blockquote class="instagram-media" data-instgrm-permalink="{u}" data-instgrm-version="14">'
                f'<a href="{u}">Shiko postimin në Instagram</a></blockquote>')
    if kind == "X":
        tw = html.escape(re.sub(r"//(www\.)?x\.com/", "//twitter.com/", url))
        return f'<blockquote class="twitter-tweet"><a href="{tw}">Shiko postimin në X</a></blockquote>'
    m = re.search(r"/video/(\d+)", url)
    vid = f' data-video-id="{m.group(1)}"' if m else ""
    return f'<blockquote class="tiktok-embed" cite="{u}"{vid}><a href="{u}">Shiko videon në TikTok</a></blockquote>'


def _social_caption(url: str) -> str:
    """Text des Beitrags, falls die Seite ihn ohne Anmeldung zeigt (oft nur bei Instagram). Sonst leer."""
    import requests
    from bs4 import BeautifulSoup
    try:
        resp = requests.get(url, headers=feeds.BROWSER_HEADERS, timeout=15)
        og = BeautifulSoup(resp.text, "html.parser").find("meta", property="og:description")
        return (og.get("content") or "").strip() if og else ""
    except Exception:
        return ""


def build_from_social(url: str, note: str) -> tuple[int, list[str]]:
    """Meldung zu einem Instagram/X/TikTok-Beitrag: die Notiz der Redaktion wird korrigiert und
    zu einer kurzen Meldung ausgebaut, der Original-Beitrag kommt eingebettet darunter."""
    platform = social_platform(url)
    caption = _social_caption(url) if platform == "Instagram" else ""
    text = f"Notiz der Redaktion:\n{note.strip()}"
    if caption:
        text += f"\n\nText des Beitrags:\n{caption}"
    story = {"title": "", "link": url, "source": platform, "published": "", "categories": [],
             "text": text, "needs_fulltext": False, "social": platform}
    db.mark_seen(url, note[:80], platform)
    errors: list[str] = []
    draft_id = _make_draft(story, _wp_or_none(), "social-" + datetime.now().strftime("%Y%m%d-%H%M%S"), errors)
    return draft_id, errors


def _para_html(p: str) -> str:
    """Absatz → HTML. "## Titel" = Zwischentitel, Zeilen mit "- " = Liste (für Udhëzues)."""
    e = lambda t: html.escape(t, quote=False)
    p = p.strip()
    if p.startswith("## "):
        return f"<h2>{e(p[3:].strip())}</h2>"
    lines = [ln.strip() for ln in p.splitlines() if ln.strip()]
    if lines and all(ln.startswith(("- ", "• ")) for ln in lines):
        return "<ul>" + "".join(f"<li>{e(ln[2:].strip())}</li>" for ln in lines) + "</ul>"
    return f"<p>{e(p)}</p>"


def related_block(related: list[dict]) -> str:
    """«Lexo edhe» mit 2–3 eigenen Artikeln – damit Leser von Facebook nicht nach einem Artikel gehen."""
    if not related:
        return ""
    items = "".join(f'<li><a href="{html.escape(r["link"])}">{html.escape(r["title"])}</a></li>' for r in related)
    return f'<div class="dj-lexo-edhe"><h3>Lexo edhe</h3><ul>{items}</ul></div>'


def build_content(d: dict, related: list[dict] | None = None) -> str:
    body = "\n".join(_para_html(p) for p in d["paragraphs"] if p.strip())
    if social_platform(d["source_link"]):
        body += "\n" + social_embed(d["source_link"])
    body += "\n" + related_block(related or [])
    source = ""
    if d.get("kind") == "udhezues" and d["source_link"]:  # offizielle Quelle: mit Link (Glaubwürdigkeit)
        source = (f'<p class="dj-burimi"><em>Burimi zyrtar: <a href="{html.escape(d["source_link"])}" '
                  f'target="_blank" rel="noopener">{html.escape(d["source_name"])}</a></em></p>')
    elif d["source_link"]:  # eigener Text der Redaktion: ohne Quelle
        # nur der Name der Quelle, ohne Link (keine Besucher zur Konkurrenz schicken)
        source = f'<p class="dj-burimi"><em>Burimi: {html.escape(d["source_name"])}</em></p>'
    if d["image_kind"] == "ai":
        source += f'\n<p class="dj-foto-ai"><em>{AI_IMAGE_CAPTION}</em></p>'
    return f"{body}\n{source}"


def publish_draft(draft_id: int) -> dict:
    d = db.get_draft(draft_id)
    wp = WordPress()

    media_id = d["wp_media_id"]
    if d["image_kind"] in ("ai", "manual") and not media_id:
        caption = AI_IMAGE_CAPTION if d["image_kind"] == "ai" else ""
        media = wp.upload_image(Path(d["image_ref"]), title=d["title"],
                                caption=caption, alt=d["title"])
        media_id = media["id"]
        db.update_draft(draft_id, wp_media_id=media_id)

    category = wp.term_id("categories", d["category"])
    tags = [wp.term_id("tags", t) for t in d["tags"]]
    try:
        related = wp.related_posts(category, tags, limit=3)
    except Exception as exc:  # «Lexo edhe» ist nett, darf das Publizieren aber nie stoppen
        log.warning("Lexo edhe nicht geladen: %s", exc)
        related = []
    post = wp.create_post(title=d["title"], content=build_content(d, related), excerpt=d["excerpt"],
                          categories=[category], tags=tags, featured_media=media_id,
                          status=POST_STATUS)
    db.update_draft(draft_id, status="posted", wp_post_id=post["id"], wp_post_url=post["link"],
                    error=None)
    return post


FB_SLOTS = {"mengjes": ((6, 30), (8, 0)), "mbremje": ((18, 30), (21, 0))}


def best_fb_time(preferred: str, now: datetime | None = None) -> str:
    """Nächstes passendes Zeitfenster (Morgen 06:30–08:00 oder Abend 18:30–21:00), Zürcher Zeit."""
    from datetime import timedelta
    from zoneinfo import ZoneInfo
    from config import TIMEZONE

    now = now or datetime.now(ZoneInfo(TIMEZONE))
    order = [preferred] + [k for k in FB_SLOTS if k != preferred]
    for day in range(0, 2):
        date = (now + timedelta(days=day)).date()
        for key in order:
            (h1, m1), (h2, m2) = FB_SLOTS[key]
            end = now.replace(year=date.year, month=date.month, day=date.day, hour=h2, minute=m2, second=0)
            if end > now:
                when = "sot" if day == 0 else "nesër"
                return f"{when} {h1:02d}:{m1:02d}–{h2:02d}:{m2:02d}"
    return "nesër 06:30–08:00"


def facebook_draft(draft_id: int) -> dict:
    """Facebook-Text für einen veröffentlichten Artikel erstellen (oder gespeicherten zurückgeben).
    Wird NICHT automatisch gepostet – die Redaktion kopiert ihn."""
    import json

    d = db.get_draft(draft_id)
    if d.get("fb_text"):
        return json.loads(d["fb_text"])
    fb = ai_writer.facebook_post(d["title"], d["excerpt"], d["paragraphs"], d["category"])
    fb["text"] = (f"{fb['hyrja'].strip()}\n\n{fb['permbledhja'].strip()}\n\n{fb['pyetja'].strip()}\n\n"
                  f"Lidhja në koment 👇\n\n{' '.join(fb['hashtags'])}")
    fb["koment"] = d["wp_post_url"] or ""
    fb["ora"] = best_fb_time(fb["koha"])
    db.update_draft(draft_id, fb_text=json.dumps(fb, ensure_ascii=False))
    return fb


def post_to_facebook(draft_id: int) -> str:
    """Postet einen bereits veröffentlichten Artikel auf die Facebook-Seite (mit Foto). Gibt die FB-URL zurück."""
    import facebook

    d = db.get_draft(draft_id)
    link = d["wp_post_url"]
    if not link:
        raise RuntimeError("Artikeli nuk është publikuar ende në WordPress")
    image_url = None
    if d["wp_media_id"]:
        try:
            image_url = WordPress().media_url(d["wp_media_id"]) or None
        except Exception as exc:
            log.warning("FB-Bild-URL nicht ermittelbar: %s", exc)
    fb = facebook_draft(draft_id)   # gleicher Text wie der Entwurf, Link im ersten Kommentar
    return facebook.post(fb["text"], link, image_url, first_comment=link)


def attach_photo(draft_id: int, path: Path) -> str:
    """Hängt ein Foto an einen bereits veröffentlichten Beitrag. Gibt den Beitrags-Link zurück."""
    d = db.get_draft(draft_id)
    wp = WordPress()
    media = wp.upload_image(path, title=d["title"], caption="", alt=d["title"])
    wp.set_featured_media(d["wp_post_id"], media["id"])
    db.update_draft(draft_id, image_kind="manual", image_ref=str(path), wp_media_id=media["id"])
    return d["wp_post_url"]



def publish_comic(path: Path, panels: list[dict], to_fb: bool) -> tuple[str, str | None]:
    """Stellt einen ZaZu-Comic in die Kategorie «ZaZu». Gibt (Link, Facebook-URL oder None) zurück."""
    import comic
    import facebook

    title = f"ZaZu – {datetime.now():%d.%m.%Y}"
    alt = comic.alt_text(panels)
    wp = WordPress()
    media = wp.upload_image(path, title=title, alt=alt)
    content = (f'<figure class="wp-block-image up-zazu-img"><img src="{html.escape(media["source_url"])}" '
               f'alt="{html.escape(alt)}" width="{media.get("media_details", {}).get("width", "")}" '
               f'height="{media.get("media_details", {}).get("height", "")}"/></figure>')
    post = wp.create_post(title=title, content=content, excerpt=panels[0]["text"],
                          categories=[wp.term_id("categories", "ZaZu")], tags=[],
                          featured_media=media["id"], status=POST_STATUS)
    fb_url = None
    if to_fb:
        fb_url = facebook.post(f"😺 {title}\n\n{post['link']}", post["link"], media["source_url"])
    return post["link"], fb_url
