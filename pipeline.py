"""Ablauf: Quellen → Auswahl → Neu schreiben → Bild → Entwurf; und Veröffentlichung."""
import html
import logging
from datetime import datetime
from pathlib import Path

import ai_writer
import db
import feeds
import images
from config import AI_IMAGE_CAPTION, ARTICLES_PER_DAY, FEEDS, MAX_AGE_HOURS, POST_STATUS
from wordpress import WordPress

log = logging.getLogger(__name__)


def _wp_or_none() -> WordPress | None:
    try:
        return WordPress()
    except Exception as exc:
        log.warning("WordPress nicht verfügbar: %s", exc)
        return None


def build_drafts() -> tuple[list[int], list[str]]:
    """Gibt (Entwurfs-IDs, Fehlermeldungen) zurück."""
    errors: list[str] = []
    candidates = feeds.fetch_candidates(FEEDS, MAX_AGE_HOURS)
    if not candidates:
        return [], errors

    picks = ai_writer.select_stories(candidates, ARTICLES_PER_DAY, db.recent_titles())
    wp = _wp_or_none()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    ids: list[int] = []

    for i, story in enumerate(picks):
        db.mark_seen(story["link"], story["title"], story["source"])
        try:
            story = feeds.ensure_fulltext(story)
            art = ai_writer.rewrite(story)

            image_kind, image_ref, media_id = "none", None, None
            if art["persona"] and wp:
                media = images.find_person_photo(wp, art["persona"])
                if media:
                    image_kind, image_ref, media_id = "wp", media["source_url"], media["id"]
            if image_kind == "none":
                try:
                    path = images.generate_ai_image(art.get("prompt_imazhi") or art["titulli"],
                                                    f"ai-{stamp}-{i}")
                    if path:
                        image_kind, image_ref = "ai", str(path)
                except Exception as exc:
                    errors.append(f"KI-Bild für «{art['titulli']}» fehlgeschlagen: {exc}")

            ids.append(db.add_draft({
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
            }))
        except Exception as exc:
            log.exception("Fehler bei %s", story["link"])
            errors.append(f"«{story['title']}» konnte nicht verarbeitet werden: {exc}")
    return ids, errors


def build_content(d: dict) -> str:
    body = "\n".join(f"<p>{html.escape(p, quote=False)}</p>" for p in d["paragraphs"])
    source = (f'<p class="dj-burimi"><em>Burimi: <a href="{html.escape(d["source_link"])}" '
              f'target="_blank" rel="noopener nofollow">{html.escape(d["source_name"])}</a></em></p>')
    if d["image_kind"] == "ai":
        source += f'\n<p class="dj-foto-ai"><em>{AI_IMAGE_CAPTION}</em></p>'
    return f"{body}\n{source}"


def publish_draft(draft_id: int) -> dict:
    d = db.get_draft(draft_id)
    wp = WordPress()

    media_id = d["wp_media_id"]
    if d["image_kind"] == "ai" and not media_id:
        media = wp.upload_image(Path(d["image_ref"]), title=d["title"],
                                caption=AI_IMAGE_CAPTION, alt=d["title"])
        media_id = media["id"]
        db.update_draft(draft_id, wp_media_id=media_id)

    category = wp.term_id("categories", d["category"])
    tags = [wp.term_id("tags", t) for t in d["tags"]]
    post = wp.create_post(title=d["title"], content=build_content(d), excerpt=d["excerpt"],
                          categories=[category], tags=tags, featured_media=media_id,
                          status=POST_STATUS)
    db.update_draft(draft_id, status="posted", wp_post_id=post["id"], wp_post_url=post["link"],
                    error=None)
    return post
