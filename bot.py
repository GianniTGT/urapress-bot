"""UraPress.ch News-Bot – Telegram-Freigabe mit Posto / Refuzo.

Start:  python bot.py
Befehle im Telegram-Chat:
  /start    zeigt deine Chat-ID (für .env)
  /skano    Scan sofort starten (optional: religjion | sport | politik | showbiz | gjermani)
  /shkruaj  eigenen Artikel schreiben (ohne Quelle)
  /zazu     ZaZu-Comic aus Text-Zeilen zeichnen
  /statusi  Statistik
"""
import asyncio
import html
import json
import logging
import re
import time
from datetime import time as dtime
from pathlib import Path
from zoneinfo import ZoneInfo

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, LinkPreviewOptions, Update
from telegram.constants import ParseMode
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler, ContextTypes,
                          MessageHandler, filters)

import ai_writer
import comic
import config
import db
import facebook
import pipeline

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("bot")

scan_lock = asyncio.Lock()
NO_PREVIEW = LinkPreviewOptions(is_disabled=True)


def is_admin(update: Update) -> bool:
    return update.effective_user and update.effective_user.id in config.TELEGRAM_ADMIN_IDS


BADGES = ["E FUNDIT", "TOP LAJM", "SKANDAL", "EKSKLUZIVE"]  # Reihenfolge beim Durchschalten


def current_badge(tags: list[str]) -> str | None:
    return next((t for t in tags if t in BADGES), None)


def keyboard(draft_id: int) -> InlineKeyboardMarkup:
    d = db.get_draft(draft_id)
    badge = current_badge(d["tags"]) if d else None
    rows = []
    if facebook.enabled():
        rows.append([InlineKeyboardButton("📘 Posto + Foto + FB", callback_data=f"pfb:{draft_id}")])
    rows.append([InlineKeyboardButton("✅ Posto + Foto", callback_data=f"posto:{draft_id}")])
    rows.append([InlineKeyboardButton(f"🏷 Shenjë mbi foto: {badge or 'asnjë'}", callback_data=f"shenje:{draft_id}")])
    rows.append([InlineKeyboardButton("✏️ Ndrysho tekstin", callback_data=f"ndrysho:{draft_id}"),
                 InlineKeyboardButton("❌ Mos posto", callback_data=f"refuzo:{draft_id}")])
    return InlineKeyboardMarkup(rows)


def has_photo(d: dict) -> bool:
    """Eigenes Foto (Reply) oder Personenfoto aus der eigenen WP-Mediathek."""
    return d["image_kind"] in ("manual", "wp")


def fb_keyboard(draft_id: int) -> InlineKeyboardMarkup | None:
    """Nur Facebook – für Artikel, die schon auf der Website sind (z. B. nach Foto-Reply)."""
    if not facebook.enabled():
        return None
    return InlineKeyboardMarkup([[InlineKeyboardButton("📘 Posto në FB", callback_data=f"fb:{draft_id}")]])


def preview_text(d: dict) -> str:
    e = html.escape
    photo = {
        "wp": f"🖼 Foto nga Mediateka: {e(d['person'] or '')}",
        "ai": f"🖼 {config.AI_IMAGE_CAPTION}",
        "manual": "🖼 Foto nga redaksia",
        "none": "🖼 Pa foto – shtyp një buton, pastaj dërgo foton",
    }[d["image_kind"]]
    body = "\n\n".join(d["paragraphs"])
    if len(body) > 2900:
        body = body[:2900].rsplit(" ", 1)[0] + " …"
    return (
        f"🆕 <b>#{d['id']} · {e(d['title'])}</b>\n<i>{e(d['excerpt'])}</i>\n\n{e(body)}\n\n"
        f"📂 {e(d['category'])} · 🏷 {e(', '.join(d['tags']))}\n"
        + (f"🔗 Burimi: <a href=\"{e(d['source_link'])}\">{e(d['source_name'])}</a>\n" if d["source_link"]
           else "✍️ Tekst i redaksisë – pa burim\n")
        + photo
    )


async def send_draft(bot, d: dict) -> None:
    chat = config.TELEGRAM_CHAT_ID
    try:
        if d["image_kind"] == "ai":
            with open(d["image_ref"], "rb") as f:
                await bot.send_photo(chat, photo=f, caption=f"#{d['id']} · {config.AI_IMAGE_CAPTION}")
        elif d["image_kind"] == "wp":
            await bot.send_photo(chat, photo=d["image_ref"], caption=f"#{d['id']} · {d['person']}")
    except Exception as exc:
        log.warning("Bild-Vorschau fehlgeschlagen: %s", exc)
    await bot.send_message(chat, preview_text(d), parse_mode=ParseMode.HTML,
                           reply_markup=keyboard(d["id"]), link_preview_options=NO_PREVIEW)


async def run_scan(bot, theme: str | None = None) -> None:
    if not config.TELEGRAM_CHAT_ID:
        log.warning("TELEGRAM_CHAT_ID fehlt – Scan übersprungen")
        return
    if scan_lock.locked():
        await bot.send_message(config.TELEGRAM_CHAT_ID, "⏳ Një skanim është duke u kryer.")
        return
    async with scan_lock:
        try:
            ids, errors = await asyncio.to_thread(pipeline.build_drafts, theme)
        except Exception as exc:
            log.exception("Scan fehlgeschlagen")
            await bot.send_message(config.TELEGRAM_CHAT_ID, f"⚠️ Skanimi dështoi: {exc}")
            return
        if not ids:
            if theme and theme in ai_writer.THEMES:
                await bot.send_message(config.TELEGRAM_CHAT_ID,
                                       f"ℹ️ Sot nuk ka lajme për temën «{ai_writer.THEMES[theme]['label']}».")
            else:
                await bot.send_message(config.TELEGRAM_CHAT_ID, "ℹ️ Sot nuk ka lajme të reja nga burimet.")
        for draft_id in ids:
            await send_draft(bot, db.get_draft(draft_id))
        for err in errors:
            await bot.send_message(config.TELEGRAM_CHAT_ID, f"⚠️ {err}")


# --- Eigener / korrigierter Text -------------------------------------------------
def parse_text(text: str) -> tuple[str, str, list[str]] | None:
    """Rreshti i parë = titulli, pastaj paragrafët (të ndarë me rresht bosh).
    Gibt (Titel, Kurztext, Absätze) zurück oder None, wenn kein Text da ist."""
    blocks, cur = [], []
    for line in text.strip().splitlines():
        line = line.strip()
        if line.startswith(("📂", "🔗", "🖼", "✍️")):
            continue
        if line:
            cur.append(line)
        elif cur:
            blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    if not blocks:
        return None
    from_preview = blocks[0][0].startswith("🆕")  # ganze Vorschau kopiert: 2. Zeile ist der alte Kurztext
    title = re.sub(r"^🆕\s*#\d+\s*·\s*", "", blocks[0][0]).strip()
    paras = []
    if len(blocks[0]) > 1 and not from_preview:  # Text direkt unter dem Titel ohne Leerzeile
        paras.append(" ".join(blocks[0][1:]))
    paras += [" ".join(b) for b in blocks[1:]]
    if not title or not paras:
        return None
    return title, make_excerpt(paras[0]), paras


def make_excerpt(first: str, limit: int = 240) -> str:
    """Kurztext: erster Satz (bei sehr kurzem Satz die ersten zwei)."""
    sentences = re.split(r"(?<=[.!?])\s+", first)
    out = sentences[0]
    if len(out) < 60 and len(sentences) > 1:
        out += " " + sentences[1]
    return out if len(out) <= limit else out[:limit].rsplit(" ", 1)[0] + " …"


def plain_text(d: dict) -> str:
    return d["title"] + "\n\n" + "\n\n".join(d["paragraphs"])


def category_keyboard(draft_id: int) -> InlineKeyboardMarkup:
    cats = config.CATEGORIES
    rows = [[InlineKeyboardButton(c, callback_data=f"kat:{draft_id}:{i}") for i, c in enumerate(cats)][j:j + 2]
            for j in range(0, len(cats), 2)]
    return InlineKeyboardMarkup(rows)


async def cmd_write(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update):
        return
    context.chat_data.pop("ndrysho", None)
    context.chat_data["shkruaj"] = True
    await update.message.reply_text(
        "✍️ Shkruaj lajmin dhe dërgoje këtu:\n\n"
        "• rreshti i parë = titulli\n"
        "• pastaj një rresht bosh\n"
        "• pastaj paragrafët (të ndarë me rresht bosh)\n\n"
        "Lajmi del pa burim. /anulo për ta ndërprerë.")


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update):
        return
    context.chat_data.pop("shkruaj", None)
    context.chat_data.pop("ndrysho", None)
    context.chat_data.pop("zazu", None)
    await update.message.reply_text("↩️ U anulua.")


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update):
        return
    msg = update.message
    if context.chat_data.get("zazu"):
        await make_comic(msg, context, msg.text or "")
        return
    # Ziel: Reply auf eine Nachricht mit #N, sonst der Entwurf, der gerade bearbeitet wird
    draft_id = None
    if msg.reply_to_message:
        m = re.search(r"#(\d+)", msg.reply_to_message.text or msg.reply_to_message.caption or "")
        draft_id = int(m.group(1)) if m else None
    draft_id = draft_id or context.chat_data.get("ndrysho")
    new_article = not draft_id and context.chat_data.get("shkruaj")
    if not draft_id and not new_article:
        await msg.reply_text("ℹ️ Për lajm të ri: /shkruaj. Për të ndryshuar një lajm: butoni ✏️ Ndrysho tekstin.")
        return
    parsed = parse_text(msg.text or "")
    if not parsed:
        await msg.reply_text("⚠️ Mungon titulli ose teksti. Rreshti i parë = titulli, pastaj paragrafët.")
        return
    title, excerpt, paras = parsed

    if new_article:
        context.chat_data.pop("shkruaj", None)
        new_id = db.add_draft({
            "source_name": "", "source_link": "", "title": title, "excerpt": excerpt,
            "paragraphs": paras, "category": config.CATEGORIES[0], "tags": [], "person": None,
            "image_kind": "none", "image_ref": None, "wp_media_id": None,
        })
        await msg.reply_text(f"📂 #{new_id} · Në cilën rubrikë?", reply_markup=category_keyboard(new_id))
        return

    d = db.get_draft(draft_id)
    if not d or d["status"] != "pending":
        context.chat_data.pop("ndrysho", None)
        await msg.reply_text(f"ℹ️ #{draft_id} nuk mund të ndryshohet më.")
        return
    db.update_draft(draft_id, title=title, excerpt=excerpt,
                    paragraphs=json.dumps(paras, ensure_ascii=False), source_name="", source_link="")
    context.chat_data.pop("ndrysho", None)
    await msg.reply_text(f"✏️ #{draft_id} u ndryshua (pa burim). Ja versioni i ri:")
    await send_draft(context.bot, db.get_draft(draft_id))


async def on_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if not is_admin(update):
        await q.answer("Nuk ke leje.", show_alert=True)
        return
    _, raw_id, raw_i = q.data.split(":")
    draft_id, i = int(raw_id), int(raw_i)
    if not 0 <= i < len(config.CATEGORIES):
        await q.answer()
        return
    db.update_draft(draft_id, category=config.CATEGORIES[i])
    await q.answer(config.CATEGORIES[i])
    await q.edit_message_text(f"📂 #{draft_id} · {config.CATEGORIES[i]}")
    await send_draft(context.bot, db.get_draft(draft_id))


# --- Handler ------------------------------------------------------------------
def _draft_id_from(msg) -> int | None:
    """Liest die Nummer #N aus dem Vorschau-Text (Antwort-Nachricht oder eigene Bildunterschrift)."""
    texts = []
    if msg.reply_to_message:
        texts.append(msg.reply_to_message.text or msg.reply_to_message.caption or "")
    texts.append(msg.caption or "")
    for text in texts:
        m = re.search(r"#(\d+)", text)
        if m:
            return int(m.group(1))
    return None


async def publish(message, draft_id: int, to_fb: bool) -> None:
    """Veröffentlicht auf der Website, bei to_fb zusätzlich auf Facebook. Antwortet auf message."""
    if not db.claim(draft_id, "publishing"):
        await message.reply_text(f"ℹ️ #{draft_id} është trajtuar tashmë.")
        return
    await message.reply_text(f"⏳ #{draft_id} duke u publikuar …")
    try:
        post = await asyncio.to_thread(pipeline.publish_draft, draft_id)
    except Exception as exc:
        log.exception("Publizieren fehlgeschlagen")
        db.update_draft(draft_id, status="pending", error=str(exc))
        await message.reply_text(f"⚠️ #{draft_id} nuk u publikua: {exc}", reply_markup=keyboard(draft_id))
        return
    msg = f"✅ #{draft_id} u publikua:\n{post['link']}"
    if to_fb:
        try:
            fb_url = await asyncio.to_thread(pipeline.post_to_facebook, draft_id)
            msg += f"\n📘 Facebook: {fb_url}"
        except Exception as exc:
            log.exception("Facebook fehlgeschlagen")
            msg += f"\n⚠️ Facebook dështoi: {exc}"
    await message.reply_text(msg)


async def _remove_buttons(msg) -> None:
    if msg:
        try:
            await msg.edit_reply_markup(reply_markup=None)
        except Exception:
            pass


async def on_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update):
        return
    pritje = context.chat_data.setdefault("pritje", {})  # draft_id -> to_fb
    # Reply auf eine Nachricht mit #N, sonst der Entwurf, für den zuletzt ein Foto verlangt wurde
    draft_id = _draft_id_from(update.message) or context.chat_data.get("e_fundit")
    if not draft_id:
        await update.message.reply_text("📷 Shtyp së pari një buton te lajmi (Posto + Foto …), pastaj dërgo foton.")
        return
    d = db.get_draft(draft_id)
    if not d or d["status"] not in ("pending", "posted"):
        await update.message.reply_text(f"ℹ️ #{draft_id} nuk mund të ndryshohet më.")
        return
    tg_file = await update.message.photo[-1].get_file()
    path = config.IMAGE_DIR / f"manual-{draft_id}.jpg"
    await tg_file.download_to_drive(path)

    # Schon online: Foto nachträglich einsetzen, dann FB anbieten
    if d["status"] == "posted" and d["wp_post_id"]:
        try:
            link = await asyncio.to_thread(pipeline.attach_photo, draft_id, path)
        except Exception as exc:
            log.exception("Foto anhängen fehlgeschlagen")
            await update.message.reply_text(f"⚠️ Foto nuk u vendos te #{draft_id}: {exc}")
            return
        await update.message.reply_text(f"📷 Foto u vendos te #{draft_id}:\n{link}",
                                        reply_markup=fb_keyboard(draft_id))
        return

    db.update_draft(draft_id, image_kind="manual", image_ref=str(path), wp_media_id=None)
    await _remove_buttons(update.message.reply_to_message)
    if draft_id in pritje:
        to_fb = pritje.pop(draft_id)
        if context.chat_data.get("e_fundit") == draft_id:
            context.chat_data.pop("e_fundit", None)
        await publish(update.message, draft_id, to_fb)
    else:
        # Foto zuerst geschickt: jetzt wählen, wohin
        await update.message.reply_text(f"📷 Foto u shtua te #{draft_id}. Ku ta postojmë?",
                                        reply_markup=keyboard(draft_id))


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"Përshëndetje! Bot-i i UraPress.ch\n\n"
        f"User-ID: {update.effective_user.id}\nChat-ID: {update.effective_chat.id}\n\n"
        f"Shkruaje Chat-ID te TELEGRAM_CHAT_ID në .env."
    )


async def cmd_scan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update):
        return
    theme = None
    if context.args:
        theme = ai_writer.resolve_theme(context.args[0])
        if not theme:
            await update.message.reply_text(
                "Temat: /skano religjion · /skano sport · /skano politik · /skano showbiz · /skano gjermani\n"
                "(ose thjesht /skano për të gjitha)")
            return
    label = ai_writer.THEMES[theme]["label"] if theme else None
    await update.message.reply_text(f"🔎 Duke skanuar burimet{f' · {label}' if label else ''} …")
    await run_scan(context.bot, theme)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update):
        return
    s = db.stats()
    await update.message.reply_text(
        f"📊 Linqe të para: {s.get('seen', 0)}\n"
        f"⏳ Në pritje: {s.get('pending', 0)}\n✅ Të publikuara: {s.get('posted', 0)}\n"
        f"❌ Të refuzuara: {s.get('rejected', 0)}\n\nSkanimi ditor: {config.SCAN_TIME}"
    )


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if not is_admin(update):
        await q.answer("Nuk ke leje.", show_alert=True)
        return
    action, raw_id = q.data.split(":")
    draft_id = int(raw_id)
    pritje = context.chat_data.setdefault("pritje", {})

    if action == "refuzo":
        if db.claim(draft_id, "rejected"):
            pritje.pop(draft_id, None)
            await q.answer("U refuzua")
            await q.edit_message_reply_markup(reply_markup=None)
            await q.message.reply_text(f"❌ #{draft_id} nuk u postua.")
        else:
            await q.answer("Ky lajm është trajtuar tashmë.", show_alert=True)
        return

    if action == "shenje":
        d = db.get_draft(draft_id)
        if not d or d["status"] != "pending":
            await q.answer("Ky lajm është trajtuar tashmë.", show_alert=True)
            return
        cur = current_badge(d["tags"])
        nxt = BADGES[BADGES.index(cur) + 1] if cur and cur != BADGES[-1] else (None if cur else BADGES[0])
        tags = [t for t in d["tags"] if t not in BADGES] + ([nxt] if nxt else [])
        db.update_draft(draft_id, tags=json.dumps(tags, ensure_ascii=False))
        await q.answer(nxt or "pa shenjë")
        await q.edit_message_reply_markup(reply_markup=keyboard(draft_id))
        return

    if action == "ndrysho":
        d = db.get_draft(draft_id)
        if not d or d["status"] != "pending":
            await q.answer("Ky lajm është trajtuar tashmë.", show_alert=True)
            return
        context.chat_data.pop("shkruaj", None)
        context.chat_data["ndrysho"] = draft_id
        await q.answer()
        await q.message.reply_text(
            f"✏️ #{draft_id}: kopjo tekstin më poshtë, ndryshoje dhe dërgoje këtu. "
            "Rreshti i parë = titulli. Burimi hiqet. /anulo për ta ndërprerë.")
        text = plain_text(d)
        for k in range(0, len(text), 4000):
            await q.message.reply_text(text[k:k + 4000])
        return

    if action == "anulo":
        pritje.pop(draft_id, None)
        if context.chat_data.get("e_fundit") == draft_id:
            context.chat_data.pop("e_fundit", None)
        await q.answer("U anulua")
        await q.edit_message_text(f"↩️ #{draft_id}: zgjidh përsëri.", reply_markup=keyboard(draft_id))
        return

    if action in ("posto", "pfb"):
        d = db.get_draft(draft_id)
        if not d or d["status"] != "pending":
            await q.answer("Ky lajm është trajtuar tashmë.", show_alert=True)
            return
        to_fb = action == "pfb"
        await q.answer()
        await q.edit_message_reply_markup(reply_markup=None)
        if has_photo(d):
            await publish(q.message, draft_id, to_fb)
            return
        # Erst Foto verlangen, dann veröffentlichen
        pritje[draft_id] = to_fb
        context.chat_data["e_fundit"] = draft_id
        ku = "uebfaqe + Facebook" if to_fb else "uebfaqe"
        await q.message.reply_text(
            f"📷 Dërgo foton për #{draft_id} ({ku}).",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✖ Anulo", callback_data=f"anulo:{draft_id}")]]))
        return

    if action == "fb":
        d = db.get_draft(draft_id)
        if not d or d["status"] != "posted":
            await q.answer("Artikulli nuk është ende në uebfaqe.", show_alert=True)
            return
        await q.answer("Duke postuar në Facebook …")
        try:
            fb_url = await asyncio.to_thread(pipeline.post_to_facebook, draft_id)
        except Exception as exc:
            log.exception("Facebook fehlgeschlagen")
            await q.message.reply_text(f"⚠️ Facebook dështoi: {exc}")
            return
        await q.edit_message_reply_markup(reply_markup=None)
        await q.message.reply_text(f"📘 #{draft_id} në Facebook:\n{fb_url}")


# --- ZaZu-Comic --------------------------------------------------------------------
ZAZU_HELP = (
    "😺 Shkruaj skicën – një rresht = një foto (1 deri 4):\n\n"
    "Sara: ZaZu, hajde të luajmë bowling!\n"
    "ZaZu (putra): Një… dy… tre… katër.\n"
    "ZaZu (mërzitur): S'ka shans. Gishta të vegjël.\n\n"
    "Gjendja në kllapa (pa kllapa = normal):\n"
    "ZaZu: gëzuar · mërzitur · habitur · putra\n"
    "Sara: mërzitur · habitur · topi\n\n"
    "/anulo për ta ndërprerë.")


def zazu_keyboard(key: int) -> InlineKeyboardMarkup:
    rows = []
    if facebook.enabled():
        rows.append([InlineKeyboardButton("📘 Posto + FB", callback_data=f"zz_pfb:{key}")])
    rows.append([InlineKeyboardButton("✅ Posto", callback_data=f"zz_ok:{key}"),
                 InlineKeyboardButton("❌ Mos posto", callback_data=f"zz_no:{key}")])
    return InlineKeyboardMarkup(rows)


async def make_comic(msg, context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    try:
        panels = comic.parse(text)
    except comic.ComicError as exc:
        await msg.reply_text(f"⚠️ {exc}")
        return
    context.chat_data.pop("zazu", None)
    key = context.chat_data.get("zazu_nr", 0) + 1
    context.chat_data["zazu_nr"] = key
    path = config.IMAGE_DIR / "zazu" / f"zazu-{msg.message_id}.png"
    await asyncio.to_thread(comic.render, panels, path)
    context.chat_data.setdefault("zazu_skica", {})[key] = {"panels": panels, "path": str(path)}
    with open(path, "rb") as fh:
        await msg.reply_photo(fh, caption=f"😺 ZaZu · skica {key}\nPër ta ndryshuar: /zazu dhe dërgo tekstin përsëri.",
                              reply_markup=zazu_keyboard(key))


async def cmd_zazu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update):
        return
    context.chat_data.pop("shkruaj", None)
    context.chat_data.pop("ndrysho", None)
    text = (update.message.text or "").split(None, 1)
    if len(text) > 1 and text[1].strip():
        await make_comic(update.message, context, text[1])
        return
    context.chat_data["zazu"] = True
    await update.message.reply_text(ZAZU_HELP)


async def on_zazu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if not is_admin(update):
        await q.answer("Nuk ke leje.", show_alert=True)
        return
    action, raw = q.data.split(":")
    sk = context.chat_data.get("zazu_skica", {}).pop(int(raw), None)
    if not sk:
        await q.answer("Kjo skicë është trajtuar tashmë.", show_alert=True)
        return
    await q.answer()
    await q.edit_message_reply_markup(reply_markup=None)
    if action == "zz_no":
        await q.message.reply_text("❌ ZaZu nuk u postua.")
        return
    await q.message.reply_text("⏳ ZaZu duke u publikuar …")
    try:
        link, fb_url = await asyncio.to_thread(
            pipeline.publish_comic, Path(sk["path"]), sk["panels"], action == "zz_pfb")
    except Exception as exc:
        log.exception("ZaZu fehlgeschlagen")
        context.chat_data.setdefault("zazu_skica", {})[int(raw)] = sk
        await q.message.reply_text(f"⚠️ ZaZu nuk u publikua: {exc}", reply_markup=zazu_keyboard(int(raw)))
        return
    await q.message.reply_text(f"✅ ZaZu u publikua:\n{link}" + (f"\n📘 Facebook: {fb_url}" if fb_url else ""))


# --- Njoftime (Kleinanzeigen von der Website) --------------------------------------
NJ_TYPES = {"kerkoj": "🔵 KËRKOJ", "ofroj": "🟢 OFROJ"}
NJ_CATS = {"pune": "Punë & zanate", "banese": "Banesë", "vetura": "Vetura", "sherbime": "Shërbime",
           "shitje": "Shitje & blerje", "tjera": "Të tjera"}


async def check_njoftime(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Jede Minute: neue Kleinanzeigen von der Website zur Freigabe schicken."""
    if not config.TELEGRAM_CHAT_ID:
        return
    try:
        items = await asyncio.to_thread(lambda: pipeline.WordPress().pending_njoftime())
    except Exception as exc:
        log.warning("Njoftime nicht abrufbar: %s", exc)
        return
    by_id = {it["id"]: it for it in items}
    for nj_id in db.nj_new_ids(list(by_id)):
        it = by_id[nj_id]
        m = it.get("meta") or {}
        e = html.escape
        title = it["title"].get("raw") or html.unescape(it["title"].get("rendered", ""))
        text = (f"📌 <b>Njoftim i ri #{nj_id}</b>\n"
                f"{NJ_TYPES.get(m.get('_nj_lloji'), '')} · {e(NJ_CATS.get(m.get('_nj_kategoria'), ''))}"
                f"{' · 📍 ' + e(m.get('_nj_vendi')) if m.get('_nj_vendi') else ''}\n\n"
                + (f"🚗 <b>{e(m.get('_nj_marka', ''))} {e(m.get('_nj_modeli', ''))}</b> · "
                   f"{int(m.get('_nj_cmimi') or 0):,} CHF\n".replace(",", "'") if m.get('_nj_marka') else "")
                + f"<b>{e(title)}</b>\n{e(it['content'].get('raw', ''))}\n\n"
                f"👤 {e(m.get('_nj_emri') or '–')} · 📞 {e(m.get('_nj_telefoni') or '–')}"
                + (f"\n📷 {len(it.get('nj_foto') or [])} foto" if it.get('nj_foto') else ""))
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Publiko", callback_data=f"nj_ok:{nj_id}"),
                                    InlineKeyboardButton("❌ Fshi", callback_data=f"nj_no:{nj_id}")],
                                   [InlineKeyboardButton("⭐ Publiko i theksuar (30 ditë)", callback_data=f"nj_star:{nj_id}")]])
        fotos = it.get("nj_foto") or []
        if fotos:
            try:
                if len(fotos) > 1:
                    await context.bot.send_media_group(config.TELEGRAM_CHAT_ID,
                                                       [InputMediaPhoto(u) for u in fotos[:3]])
                else:
                    await context.bot.send_photo(config.TELEGRAM_CHAT_ID, fotos[0])
            except Exception as exc:
                log.warning("Njoftim-Fotos nicht gesendet: %s", exc)
        await context.bot.send_message(config.TELEGRAM_CHAT_ID, text, parse_mode=ParseMode.HTML,
                                       reply_markup=kb, link_preview_options=NO_PREVIEW)


async def on_njoftim(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if not is_admin(update):
        await q.answer("Nuk ke leje.", show_alert=True)
        return
    action, raw_id = q.data.split(":")
    nj_id = int(raw_id)
    try:
        if action == "nj_ok":
            res = await asyncio.to_thread(lambda: pipeline.WordPress().set_njoftim_status(nj_id, "publish"))
            await q.answer("U publikua")
            await _remove_buttons(q.message)
            star = InlineKeyboardMarkup([[InlineKeyboardButton("⭐ Theksoje (30 ditë)", callback_data=f"nj_star:{nj_id}")]])
            await q.message.reply_text(f"✅ Njoftimi #{nj_id} është online:\n{res.get('link', '')}", reply_markup=star)
        elif action == "nj_star":
            until = int(time.time()) + 30 * 86400
            res = await asyncio.to_thread(lambda: pipeline.WordPress().highlight_njoftim(nj_id, until))
            await q.answer("⭐ I theksuar")
            await _remove_buttons(q.message)
            await q.message.reply_text(f"⭐ Njoftimi #{nj_id} është online dhe i theksuar në krye për 30 ditë:\n{res.get('link', '')}")
        else:
            await asyncio.to_thread(lambda: pipeline.WordPress().trash_njoftim(nj_id))
            await q.answer("U fshi")
            await _remove_buttons(q.message)
            await q.message.reply_text(f"❌ Njoftimi #{nj_id} u fshi.")
    except Exception as exc:
        log.exception("Njoftim-Aktion fehlgeschlagen")
        await q.answer("Gabim", show_alert=True)
        await q.message.reply_text(f"⚠️ Njoftimi #{nj_id}: {exc}")


async def scheduled_scan(context: ContextTypes.DEFAULT_TYPE) -> None:
    await run_scan(context.bot)


def main() -> None:
    db.init()
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("skano", cmd_scan))
    app.add_handler(CommandHandler("statusi", cmd_status))
    app.add_handler(CommandHandler("shkruaj", cmd_write))
    app.add_handler(CommandHandler("anulo", cmd_cancel))
    app.add_handler(CommandHandler("zazu", cmd_zazu))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, on_text))
    app.add_handler(CallbackQueryHandler(on_category, pattern=r"^kat:\d+:\d+$"))
    app.add_handler(CallbackQueryHandler(on_njoftim, pattern=r"^nj_(ok|no|star):\d+$"))
    app.add_handler(CallbackQueryHandler(on_zazu, pattern=r"^zz_(ok|pfb|no):\d+$"))
    app.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE, on_photo))
    app.add_handler(CallbackQueryHandler(on_button, pattern=r"^(posto|pfb|refuzo|anulo|fb|ndrysho|shenje):\d+$"))

    hour, minute = map(int, config.SCAN_TIME.split(":"))
    app.job_queue.run_daily(scheduled_scan, time=dtime(hour, minute, tzinfo=ZoneInfo(config.TIMEZONE)),
                            name="daily-scan")
    app.job_queue.run_repeating(check_njoftime, interval=60, first=15, name="njoftime")
    log.info("Bot läuft – täglicher Scan um %s (%s)", config.SCAN_TIME, config.TIMEZONE)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
