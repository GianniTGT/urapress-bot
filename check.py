"""Verbindungstest – vor dem ersten Start ausführen:  python check.py"""
import requests

import config
import feeds


def ok(msg): print(f"  ✅ {msg}")
def fail(msg): print(f"  ❌ {msg}")


print("\n1) RSS-Quellen")
for url in config.FEEDS:
    try:
        entries = feeds.fetch_feed(url)
        ok(f"{url} – {len(entries)} Einträge")
    except Exception as exc:
        fail(f"{url} – {exc}")

print("\n2) Telegram")
r = requests.get(f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/getMe", timeout=15).json()
ok(f"Bot @{r['result']['username']}") if r.get("ok") else fail(r)
ok(f"Chat-ID {config.TELEGRAM_CHAT_ID}") if config.TELEGRAM_CHAT_ID else fail(
    "TELEGRAM_CHAT_ID fehlt – Bot starten, /start schicken, ID eintragen")

print("\n3) Claude")
try:
    import anthropic
    msg = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY).messages.create(
        model=config.ANTHROPIC_MODEL, max_tokens=20,
        messages=[{"role": "user", "content": "Thuaj vetëm: Gati"}])
    ok(f"{config.ANTHROPIC_MODEL}: {msg.content[0].text.strip()}")
except Exception as exc:
    fail(exc)

print("\n4) KI-Bilder")
ok(f"OpenAI-Key vorhanden ({config.OPENAI_IMAGE_MODEL})") if config.OPENAI_API_KEY else fail(
    "kein OPENAI_API_KEY – Beiträge ohne Personenfoto bleiben ohne Bild")

print("\n5) WordPress")
try:
    from wordpress import WordPress
    me = WordPress().whoami()
    roles = ", ".join(me.get("roles", []))
    ok(f"Angemeldet als {me['name']} ({roles})")
except Exception as exc:
    fail(exc)
print()
