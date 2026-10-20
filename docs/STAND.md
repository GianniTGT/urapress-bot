# UraPress – Stand 19.10.2026 (Abend)

## Fertig und live

**Website (Theme, live auf urapress.ch)**
- Leuchtendes TiffCore-Logo als Animation in den TiffCore- und Tiff-Anzeigen (`assets/ads/glow.js`)
- Logo blitzt einmal pro Besuch gross in der Mitte auf (`assets/ads/tiff-flash.js`, 15–45 s nach Seitenaufruf)
- Feste TiffCore-Anzeige als Kachel im Raster „Më shumë lajme" (nach der 4. Karte)
- Oberste Leiste (Datum + Slogan) entfernt
- Aufmacher mischt Rubriken (`urapress_diverse_ids`), damit oben verschiedene Themen stehen
- Kommentar-Zahl klein unten rechts auf dem Foto (nur wenn Kommentare da sind)
- TiffCar-Anzeige: „Për auto-sallone dhe servise veturash" (auch in WordPress-Anzeige ID 9024 geändert)
- Theme-Version 1.6.0

Theme-Dateien werden live so ausgespielt: Datei vom GitHub-Commit laden und ins Theme schreiben
(`/var/www/vhosts/urapress.ch/httpdocs/wp-content/themes/urapress/`). Repo und Server sind gleich.

**Bot (Code im Repo, auf dem vServer `/opt/urapress-bot`)**
- `temperature`-Fallback für die alte `anthropic`-Version auf dem Server (läuft, siehe Log „ohne Temperatur erneut")
- Mit Foto auf einen Vorschlag antworten: Er wird **sofort** veröffentlicht, ohne nochmal „Posto"
- `/skano religjion` · `/skano sport` · `/skano politik` (ohne Thema: alles gemischt)
- Schreibstil menschlicher (Satzrhythmus, Einstieg variieren, mehr Floskeln gesperrt)
- Facebook-Knopf „📘 Posto + FB" (siehe unten). Er erscheint erst, wenn der FB-Token in der `.env` steht.

Update auf dem Server:
```
ssh ktifeki@185.178.195.35
cd /opt/urapress-bot && sudo git pull && sudo systemctl restart urapress-bot
```

## Offen für morgen

### 1. Bot: „scannt und scannt"
Letzter sauberer Scan im Log: 22:21–22:22 (3 Sport-Vorschläge, keine Fehler).
Ein normaler Scan dauert 1–2 Minuten. Zum Prüfen:
```
journalctl -u urapress-bot -f
```
Dann in Telegram `/skano` schicken, 2 Minuten warten und nachsehen, wo es hängt.
Unklar ist noch, ob der neueste Stand (`e09fdc7`, mit Facebook) schon gezogen und neu gestartet wurde.

### 2. Facebook einrichten

> **Vollständige Anleitung mit Bildern: [FACEBOOK-EINRICHTEN.md](FACEBOOK-EINRICHTEN.md)**
> Stand 20.10.: App-Rechte freigeschaltet, Seiten-ID `1390417390820237`, Token in der `.env` eingetragen.

**Stand:**
- FB-Seite **Urapress.ch** (Nachrichten- und Medienseite) existiert
- Meta-App **urapress** erstellt, Anwendungsfall „Alles auf deiner Seite verwalten" (Pages API),
  Business-Portfolio „Qani Tufekcis Unternehmen" (nicht verifiziert, reicht für die eigene Seite)
- Problem: Beim Token kam „Invalid Scopes: pages_read_engagement, pages_read_user_content".
  `pages_read_engagement` ist in der App noch nicht hinzugefügt. `pages_read_user_content` kam
  nur von `pages_manage_engagement` und das wird nicht gebraucht.

**Nächste Schritte:**
1. developers.facebook.com → Meine Apps → **urapress** → Anwendungsfälle →
   „Alles auf deiner Seite verwalten" → **Anpassen** → bei `pages_read_engagement` **Hinzufügen**
   (`pages_manage_posts` und `pages_show_list` müssen auch drin sein)
2. Graph API Explorer: App **urapress**, `pages_manage_engagement` entfernen.
   Genau diese drei auswählen: `pages_show_list`, `pages_manage_posts`, `pages_read_engagement`
3. **Generate Access Token** → Urapress.ch anhaken → erlauben (das ist der kurze **Nutzer**-Token)
4. Token dauerhaft machen. App-ID und App-Geheimcode stehen unter urapress → Einstellungen → Allgemeines:
   ```
   https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=KURZER_NUTZERTOKEN
   ```
5. Mit dem langen Nutzer-Token im Explorer abfragen:
   ```
   me/accounts?fields=name,id,access_token
   ```
   Bei Urapress.ch stehen dort `id` (= `FB_PAGE_ID`) und `access_token` (= `FB_PAGE_TOKEN`, läuft nicht ab)
6. In die `.env` auf dem Server eintragen (nicht in Chat oder Repo):
   ```
   FB_PAGE_ID=...
   FB_PAGE_TOKEN=...
   ```
   Danach `git pull` + Neustart. Der Knopf 📘 Posto + FB erscheint dann in Telegram.

**So funktioniert der FB-Teil im Code:**
- `facebook.py` postet über die Graph API v21.0. Mit Bild: `/{page}/photos` (Foto gross, Text mit Link).
  Ohne Bild: `/{page}/feed` mit Link.
- `pipeline.post_to_facebook(draft_id)` nimmt Titel + Kurztext + Link. Das Bild ist das Beitragsbild aus WordPress.
- „📘 Posto + FB" veröffentlicht zuerst in WordPress und dann auf Facebook. Wenn FB fehlschlägt,
  bleibt der Artikel trotzdem auf der Website und Telegram zeigt den Fehler.
- „✅ Posto" bleibt nur WordPress. Der Foto-Reply veröffentlicht auch nur in WordPress
  (noch offen: soll er auch auf FB?).

### 3. Kleinkram
- Platzhalter `[ ]` in Impressum, Datenschutz, Kontakt ausfüllen, danach Suchmaschinen-Indexierung einschalten
- hosts-Zeile auf dem Server prüfen: `grep urapress /etc/hosts`
- Kein `OPENAI_API_KEY` → keine KI-Bilder (optional)
- Ungenutzte CSS-Regel `.up-topbar` in `style.css` (stört nicht)
- Die Sidebar auf Artikelseiten zeigt Standard-WP-Widgets (Recent Posts, Archives …), weil
  `sidebar-1` belegt ist. Wenn die Widgets dort entfernt werden, erscheint die Theme-Sidebar.
