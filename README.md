# UraPress.ch – News-Bot

Täglicher Ablauf (Standard 07:30, Europe/Zurich):

1. RSS-Quellen lesen (shtegu.com, lajmpress.org …) – nur Meldungen der letzten 48 h, die noch nie gesehen wurden
2. Claude wählt 2–3 Meldungen (Diaspora-Bezug bevorzugt, keine Gedichte/Werbung/Duplikate)
3. Claude schreibt jede Meldung **neu auf Albanisch** (eigene Worte, Fakten 1:1)
4. Bild: Personenfoto aus der WP-Mediathek (Titel = Name) → sonst KI-Symbolbild „Foto ilustruese (AI)"
5. Vorschau im Telegram mit **✅ Posto / ❌ Refuzo**
6. Bei *Posto*: Upload Bild + Beitrag über WordPress REST API, Quelle + Link unten im Artikel

Telegram-Befehle: `/start` (zeigt Chat-ID) · `/skano` (Scan sofort) · `/statusi` (Statistik)

---

## 1. Vorbereitung (einmalig)

### Telegram-Bot
1. In Telegram **@BotFather** → `/newbot` → Name z. B. *UraPress Redaksia* → Token kopieren.

### API-Keys
- **Claude**: console.anthropic.com → API Keys
- **KI-Bilder** (optional): platform.openai.com → API Keys. Ohne Key: Beiträge ohne Personenfoto bleiben ohne Bild.

### WordPress (sobald UraPress.ch läuft)
1. Neuen Benutzer anlegen: `redaksia-bot`, Rolle **Redakteur** (Editor).
2. Als dieser Benutzer: *Benutzer → Profil → Anwendungspasswörter* → Name „News-Bot" → Passwort kopieren.
   (Funktioniert nur mit **HTTPS** – Let's Encrypt im Hosttech-Panel aktivieren.)
3. **Hosttech/Apache-Falle:** Wenn `check.py` bei WordPress „401" meldet, wird der Authorization-Header nicht durchgereicht. Ganz oben in die `.htaccess` von WordPress:
   ```
   SetEnvIf Authorization "(.*)" HTTP_AUTHORIZATION=$1
   ```
4. Security-Plugins (Wordfence, iThemes …): REST API und Anwendungspasswörter **nicht** sperren.
5. **Personenfotos:** in die Mediathek hochladen, Titel = exakter Name, z. B. `Albin Kurti`, `Granit Xhaka`.
   Gross/Klein und ë/ç werden ignoriert. Nur Fotos mit Nutzungsrecht (eigene, Pressebilder mit Freigabe, Wikimedia mit Lizenzangabe).

---

## 2. Installation auf dem vServer (Ubuntu 24)

```bash
# als root
apt update && apt install -y python3-venv python3-pip unzip
adduser --system --group --home /opt/urapress-bot urapress

# Projekt hochladen (z. B. per scp/WinSCP) und entpacken
unzip urapress-bot.zip -d /opt/
cd /opt/urapress-bot
python3 -m venv venv
venv/bin/pip install -r requirements.txt

cp .env.example .env
nano .env                         # Token, Keys, WP-Daten eintragen
chown -R urapress:urapress /opt/urapress-bot
chmod 600 .env
```

### Chat-ID herausfinden
```bash
sudo -u urapress venv/bin/python bot.py
```
Im Telegram dem Bot `/start` schicken → Chat-ID wird angezeigt → in `.env` bei `TELEGRAM_CHAT_ID` eintragen → Bot mit `Ctrl+C` stoppen.

### Verbindungstest
```bash
sudo -u urapress venv/bin/python check.py
```
Alle 5 Punkte sollten ✅ sein (WordPress erst, wenn die Seite steht).

### Als Dienst starten (läuft dauerhaft, startet nach Reboot neu)
```bash
cp deploy/urapress-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now urapress-bot
journalctl -u urapress-bot -f    # Log live ansehen
```

Nach Änderungen an `.env` oder am Code: `systemctl restart urapress-bot`

---

## 3. Testbetrieb

- In `.env` zuerst `POST_STATUS=draft` → Beiträge landen als **Entwurf** in WP. Wenn Texte und Bilder passen: auf `publish` umstellen.
- Im Telegram `/skano` → Vorschläge kommen sofort, ohne auf 07:30 zu warten.

## 4. Neue Quelle hinzufügen
In `.env` bei `FEEDS` mit Komma anhängen, z. B.:
```
FEEDS=https://shtegu.com/feed/,https://lajmpress.org/feed/,https://beispiel.com/feed/
```
WordPress-Seiten haben fast immer `/feed/`. Neustart nicht vergessen.

Liefert ein Feed nur einen Anriss (z. B. Alsat, PortaliX), lädt der Bot den Artikel
für die ausgewählten Meldungen automatisch von der Webseite (trafilatura).

| Quelle | Feed | Volltext |
|---|---|---|
| shtegu.com | `https://shtegu.com/feed/` | im Feed |
| lajmpress.org | `https://lajmpress.org/feed/` | im Feed |
| alsat.mk | `https://alsat.mk/feed/` | von der Webseite |
| portalix.mk | `https://portalix.mk/api/rss.xml` | von der Webseite |

## 5. Dateien

| Datei | Aufgabe |
|---|---|
| `bot.py` | Telegram-Bot, täglicher Zeitplan, Buttons |
| `pipeline.py` | Ablauf Scan → Entwurf, und Veröffentlichen |
| `feeds.py` | RSS lesen, Text säubern, Duplikate filtern |
| `ai_writer.py` | Claude: Auswahl + Neuschreiben (Prompts hier anpassen) |
| `images.py` | Mediathek-Suche + KI-Bild |
| `wordpress.py` | WP REST API |
| `db.py` | SQLite (`data/urapress.db`): gesehene Links, Entwürfe |
| `check.py` | Verbindungstest |

**Hinweis Urheberrecht:** Der Bot übernimmt nur Fakten, schreibt komplett neu, nennt Quelle + Link und verwendet **nie** Bilder der Quellseiten.
