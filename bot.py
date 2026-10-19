"""UraPress.ch News-Bot – Telegram-Freigabe mit Posto / Refuzo.

Start:  python bot.py
Befehle im Telegram-Chat:
  /start    zeigt deine Chat-ID (für .env)
  /skano    Scan sofort starten
  /statusi  Statistik
"""
import asyncio
import html
import logging
import re
from datetime import time as dtime
from zoneinfo import ZoneInfo

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions, Update
from telegram.constants import ParseMode
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler, ContextTypes,
                          MessageHandler, filters)

import config
import db
import pipeline

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("bot")

scan_lock = asyncio.Lock()
NO_PREVIEW = LinkPreviewOptions(is_disabled=True)


def is_admin(update: Update) -> bool:
    return update.effective_user and update.effective_user.id in config.TELEGRAM_ADMIN_IDS


def keyboard(draft_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Posto", callback_data=f"posto:{draft_id}"),
        InlineKeyboardButton("❌ Refuzo", callback_data=f"refuzo:{draft_id}"),
    ]])


def preview_text(d: dict) -> str:
    e = html.escape
    photo = {
        "wp": f"🖼 Foto nga Mediateka: {e(d['person'] or '')}",
        "ai": f"🖼 {config.AI_IMAGE_CAPTION}",
        "manual": "🖼 Foto nga redaksia",
        "none": "🖼 Pa foto – dërgo një foto si përgjigje (Reply) këtij mesazhi",
    }[d["image_kind"]]
    body = "\n\n".join(d["paragraphs"])
    if len(body) > 2900:
        body = body[:2900].rsplit(" ", 1)[0] + " …"
    return (
        f"🆕 <b>#{d['id']} · {e(d['title'])}</b>\n<i>{e(d['excerpt'])}</i>\n\n{e(body)}\n\n"
        f"📂 {e(d['category'])} · 🏷 {e(', '.join(d['tags']))}\n"
        f"🔗 Burimi: <a href=\"{e(d['source_link'])}\">{e(d['source_name'])}</a>\n{photo}"
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


async def run_scan(bot) -> None:
    if not config.TELEGRAM_CHAT_ID:
        log.warning("TELEGRAM_CHAT_ID fehlt – Scan übersprungen")
        return
    if scan_lock.locked():
        await bot.send_message(config.TELEGRAM_CHAT_ID, "⏳ Një skanim është duke u kryer.")
        return
    async with scan_lock:
        try:
            ids, errors = await asyncio.to_thread(pipeline.build_drafts)
        except Exception as exc:
            log.exception("Scan fehlgeschlagen")
            await bot.send_message(config.TELEGRAM_CHAT_ID, f"⚠️ Skanimi dështoi: {exc}")
            return
        if not ids:
            await bot.send_message(config.TELEGRAM_CHAT_ID, "ℹ️ Sot nuk ka lajme të reja nga burimet.")
        for draft_id in ids:
            await send_draft(bot, db.get_draft(draft_id))
        for err in errors:
            await bot.send_message(config.TELEGRAM_CHAT_ID, f"⚠️ {err}")


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


async def on_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update):
        return
    draft_id = _draft_id_from(update.message)
    if not draft_id:
        await update.message.reply_text("📷 Dërgoje foton si përgjigje (Reply) te mesazhi i lajmit.")
        return
    d = db.get_draft(draft_id)
    if not d or d["status"] != "pending":
        await update.message.reply_text(f"ℹ️ #{draft_id} nuk është më në pritje.")
        return
    tg_file = await update.message.photo[-1].get_file()
    path = config.IMAGE_DIR / f"manual-{draft_id}.jpg"
    await tg_file.download_to_drive(path)
    db.update_draft(draft_id, image_kind="manual", image_ref=str(path), wp_media_id=None)
    await update.message.reply_text(f"📷 Foto u shtua te #{draft_id}. Shtyp ✅ Posto.",
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
    await update.message.reply_text("🔎 Duke skanuar burimet …")
    await run_scan(context.bot)


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

    if action == "refuzo":
        if db.claim(draft_id, "rejected"):
            await q.answer("U refuzua")
            await q.edit_message_reply_markup(reply_markup=None)
            await q.message.reply_text(f"❌ #{draft_id} u refuzua.")
        else:
            await q.answer("Ky lajm është trajtuar tashmë.", show_alert=True)
        return

    if action == "posto":
        if not db.claim(draft_id, "publishing"):
            await q.answer("Ky lajm është trajtuar tashmë.", show_alert=True)
            return
        await q.answer("Duke publikuar …")
        try:
            post = await asyncio.to_thread(pipeline.publish_draft, draft_id)
        except Exception as exc:
            log.exception("Publizieren fehlgeschlagen")
            db.update_draft(draft_id, status="pending", error=str(exc))
            await q.message.reply_text(f"⚠️ #{draft_id} nuk u publikua: {exc}\nProvo përsëri me ✅ Posto.")
            return
        await q.edit_message_reply_markup(reply_markup=None)
        await q.message.reply_text(f"✅ #{draft_id} u publikua:\n{post['link']}")


async def scheduled_scan(context: ContextTypes.DEFAULT_TYPE) -> None:
    await run_scan(context.bot)


def main() -> None:
    db.init()
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("skano", cmd_scan))
    app.add_handler(CommandHandler("statusi", cmd_status))
    app.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE, on_photo))
    app.add_handler(CallbackQueryHandler(on_button, pattern=r"^(posto|refuzo):\d+$"))

    hour, minute = map(int, config.SCAN_TIME.split(":"))
    app.job_queue.run_daily(scheduled_scan, time=dtime(hour, minute, tzinfo=ZoneInfo(config.TIMEZONE)),
                            name="daily-scan")
    log.info("Bot läuft – täglicher Scan um %s (%s)", config.SCAN_TIME, config.TIMEZONE)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
