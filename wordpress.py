"""WordPress REST API: Medien suchen/hochladen, Kategorien/Tags, Beiträge erstellen."""
import html
import logging
import mimetypes
from pathlib import Path

import requests

from config import WP_APP_PASSWORD, WP_URL, WP_USER

log = logging.getLogger(__name__)


class WordPressError(RuntimeError):
    pass


class WordPress:
    def __init__(self, url: str = WP_URL, user: str = WP_USER, app_password: str = WP_APP_PASSWORD):
        if not (url and user and app_password):
            raise WordPressError("WP_URL / WP_USER / WP_APP_PASSWORD fehlen in .env")
        self.api = f"{url}/wp-json/wp/v2"
        self.s = requests.Session()
        self.s.auth = (user, app_password)
        self.s.headers["User-Agent"] = "urapress-bot/1.0"

    def _req(self, method: str, path: str, **kw) -> dict | list:
        r = self.s.request(method, f"{self.api}{path}", timeout=60, **kw)
        if r.status_code >= 400:
            raise WordPressError(f"{method} {path} → {r.status_code}: {r.text[:300]}")
        return r.json()

    # --- Test -----------------------------------------------------------------
    def whoami(self) -> dict:
        return self._req("GET", "/users/me", params={"context": "edit"})

    # --- Medien ---------------------------------------------------------------
    def search_media(self, term: str) -> list[dict]:
        return self._req("GET", "/media", params={"search": term, "per_page": 20, "media_type": "image"})

    def upload_image(self, path: Path, title: str, caption: str = "", alt: str = "") -> dict:
        mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
        media = self._req(
            "POST", "/media",
            data=path.read_bytes(),
            headers={"Content-Type": mime, "Content-Disposition": f'attachment; filename="{path.name}"'},
        )
        return self._req("POST", f"/media/{media['id']}",
                         json={"title": title, "caption": caption, "alt_text": alt or title})

    # --- Kategorien & Tags ----------------------------------------------------
    def term_id(self, taxonomy: str, name: str) -> int:
        """taxonomy = 'categories' oder 'tags'. Legt den Begriff an, falls er fehlt."""
        for t in self._req("GET", f"/{taxonomy}", params={"search": name, "per_page": 100}):
            if html.unescape(t["name"]).casefold() == name.casefold():
                return t["id"]
        r = self.s.post(f"{self.api}/{taxonomy}", json={"name": name}, timeout=60)
        if r.status_code == 400 and r.json().get("code") == "term_exists":
            # Gibt es schon (z. B. «Kulturë & Showbiz» – die Suche findet das «&» nicht)
            return int(r.json()["data"]["term_id"])
        if r.status_code >= 400:
            raise WordPressError(f"POST /{taxonomy} → {r.status_code}: {r.text[:300]}")
        return r.json()["id"]

    # --- Beitrag --------------------------------------------------------------
    def create_post(self, *, title: str, content: str, excerpt: str, categories: list[int],
                    tags: list[int], featured_media: int | None, status: str) -> dict:
        payload = {"title": title, "content": content, "excerpt": excerpt, "status": status,
                   "categories": categories, "tags": tags}
        if featured_media:
            payload["featured_media"] = featured_media
        return self._req("POST", "/posts", json=payload)

    def set_featured_media(self, post_id: int, media_id: int) -> dict:
        return self._req("POST", f"/posts/{post_id}", json={"featured_media": media_id})

    def media_url(self, media_id: int) -> str:
        return self._req("GET", f"/media/{media_id}").get("source_url", "")

    # --- Njoftime (Kleinanzeigen) --------------------------------------------
    def pending_njoftime(self) -> list[dict]:
        return self._req("GET", "/njoftime", params={"status": "pending", "context": "edit", "per_page": 20})

    def set_njoftim_status(self, nj_id: int, status: str) -> dict:
        return self._req("POST", f"/njoftime/{nj_id}", json={"status": status})

    def highlight_njoftim(self, nj_id: int, until: int) -> dict:
        """Veröffentlicht und hebt hervor bis zum Zeitpunkt until (Unix-Zeit)."""
        return self._req("POST", f"/njoftime/{nj_id}",
                         json={"status": "publish", "meta": {"_nj_theksuar": str(until)}})

    def trash_njoftim(self, nj_id: int) -> dict:
        return self._req("DELETE", f"/njoftime/{nj_id}")
