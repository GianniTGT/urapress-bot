"""SQLite: bereits gesehene Links + Entwürfe mit Freigabe-Status."""
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS seen (
    link     TEXT PRIMARY KEY,
    title    TEXT,
    source   TEXT,
    seen_at  TEXT
);
CREATE TABLE IF NOT EXISTS drafts (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name   TEXT,
    source_link   TEXT,
    title         TEXT,
    excerpt       TEXT,
    paragraphs    TEXT,      -- JSON-Liste
    category      TEXT,
    tags          TEXT,      -- JSON-Liste
    person        TEXT,
    image_kind    TEXT,      -- wp | ai | none
    image_ref     TEXT,      -- WP: source_url, AI: lokaler Pfad
    wp_media_id   INTEGER,
    status        TEXT DEFAULT 'pending',  -- pending|publishing|posted|rejected|error
    wp_post_id    INTEGER,
    wp_post_url   TEXT,
    error         TEXT,
    created_at    TEXT
);
"""


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init() -> None:
    with closing(_conn()) as c, c:
        c.executescript(SCHEMA)


def is_seen(link: str) -> bool:
    with closing(_conn()) as c:
        return c.execute("SELECT 1 FROM seen WHERE link=?", (link,)).fetchone() is not None


def mark_seen(link: str, title: str, source: str) -> None:
    with closing(_conn()) as c, c:
        c.execute(
            "INSERT OR IGNORE INTO seen(link,title,source,seen_at) VALUES (?,?,?,?)",
            (link, title, source, _now()),
        )


def recent_titles(limit: int = 30) -> list[str]:
    with closing(_conn()) as c:
        rows = c.execute(
            "SELECT title FROM drafts WHERE status IN ('posted','pending') "
            "ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [r["title"] for r in rows]


def add_draft(d: dict) -> int:
    with closing(_conn()) as c, c:
        cur = c.execute(
            """INSERT INTO drafts(source_name,source_link,title,excerpt,paragraphs,category,
               tags,person,image_kind,image_ref,wp_media_id,created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                d["source_name"], d["source_link"], d["title"], d["excerpt"],
                json.dumps(d["paragraphs"], ensure_ascii=False), d["category"],
                json.dumps(d["tags"], ensure_ascii=False), d.get("person"),
                d["image_kind"], d.get("image_ref"), d.get("wp_media_id"), _now(),
            ),
        )
        return cur.lastrowid


def get_draft(draft_id: int) -> dict | None:
    with closing(_conn()) as c:
        row = c.execute("SELECT * FROM drafts WHERE id=?", (draft_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["paragraphs"] = json.loads(d["paragraphs"] or "[]")
    d["tags"] = json.loads(d["tags"] or "[]")
    return d


def update_draft(draft_id: int, **fields) -> None:
    keys = ", ".join(f"{k}=?" for k in fields)
    with closing(_conn()) as c, c:
        c.execute(f"UPDATE drafts SET {keys} WHERE id=?", (*fields.values(), draft_id))


def claim(draft_id: int, new_status: str) -> bool:
    """Setzt Status nur, wenn der Entwurf noch 'pending' ist (Schutz vor Doppelklick)."""
    with closing(_conn()) as c, c:
        cur = c.execute(
            "UPDATE drafts SET status=? WHERE id=? AND status='pending'", (new_status, draft_id)
        )
        return cur.rowcount == 1


def stats() -> dict:
    with closing(_conn()) as c:
        rows = c.execute("SELECT status, COUNT(*) n FROM drafts GROUP BY status").fetchall()
        seen = c.execute("SELECT COUNT(*) FROM seen").fetchone()[0]
    return {"seen": seen, **{r["status"]: r["n"] for r in rows}}
