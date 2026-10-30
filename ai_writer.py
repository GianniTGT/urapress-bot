"""Claude: Meldungen auswählen und auf Albanisch neu schreiben."""
import json
import logging
import re

import anthropic

from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL, CATEGORIES

log = logging.getLogger(__name__)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SELECT_SYSTEM = """Du bist Chefredakteur von UraPress.ch – einem albanischen Nachrichtenportal
für die albanische Diaspora, vor allem in der Schweiz.

WAS DIE LESER WIRKLICH LESEN (Daten 24.–30.10.2026):
- Top: Schweiz-Themen mit Geld/Familie («Vajza mbush 18 vjeç … 5'600 franga», 5:50 min),
  Albaner in der Schweiz (Shasime Osmani, 29 min), Diaspora-Anlässe (Shqip Up Comedy).
- ABER AUCH stark: albanischer Stolz/Identität und Gesprächsstoff aus der Heimat:
  «Adeyemi kommt mit Kosovo-Kennzeichen (Ferizaj) ins Camp Nou» (5:27 min),
  «Vučić akzeptiert Niederlage, Albaner kommen ins serbische Parlament» (4:53),
  grosse Kriminalfälle in Kosova (Vitomiricë, 4:34), bekannte Politiker (Veliaj), Albaner in Italien/Deutschland.
- Schwach (0–1 Leser, 0 Sekunden): trockene Schweizer Statistiken ohne Gefühl (Lehrstellen-Barometer, Ebola,
  Verwaltungsmeldungen), Weltnachrichten ohne albanischen Bezug, Routine-Tagespolitik.

PRIORITÄTEN (p = 1 bis 5):
1 = SCHWEIZ, die Albaner direkt betrifft: Geld, Papiere, Familie, Kinder, Wohnen, Arbeit
    (Bewilligung B/C, Einbürgerung, Familiennachzug, Krankenkasse, AHV, Steuern, Löhne, Mieten, Verkehr).
    Nur mit konkreter Wirkung auf den Alltag – keine trockenen Berichte/Statistiken.
2 = ALBANER IM AUSLAND: Schweiz zuerst, aber auch Deutschland, Österreich, Italien, USA, UK –
    Erfolg, Schicksal, Skandal, Gerichtsfall, Politiker, Künstler, Diaspora-Anlässe.
3 = SPORT MIT ALBANERN: Super League und Nati (Xhaka …), Kombëtarja e Kosovës / Shqipërisë,
    albanische Spieler in grossen Ligen, Stars mit albanischen Wurzeln (auch Gesten wie Kosovo-Kennzeichen).
4 = GROSSE GESCHICHTE AUS DER HEIMAT, über die alle reden: nationale Fragen und Stolz (Serbien–Kosova,
    Rechte der Albaner in Serbien/MK/MZ, Preševo), schwere Kriminalfälle, Skandale bekannter Politiker
    (Kurti, Rama, Veliaj …), emotionale Menschengeschichten, alles zu Reisen/Zoll/Pässen/Diaspora-Stimme.
5 = alles andere: Routine-Tagespolitik, kleine Unfälle, Welt ohne albanischen Bezug, trockene Statistik.

MISCHUNG pro Auswahl (z. B. 4 Meldungen):
- etwa die Hälfte aus p = 1–2 (Schweiz/Diaspora), der Rest aus p = 3–4 (Sport, grosse Heimat-Geschichte).
- höchstens EINE mit p = 5, und nur wenn sie wirklich aussergewöhnlich ist.
- nicht zweimal dasselbe Thema; nicht nur Schweiz, nicht nur Balkan.

AUSWAHL-REGEL: Würde ein Albaner in der Schweiz das auf Facebook teilen oder kommentieren?
Gefühl, Stolz, Empörung, Geld, Familie, Überraschung → ja. Trocken, amtlich, weit weg → nein.
Nur echte Fakten, keine Gerüchte. Ausschliessen: Werbung, reine Meinung, schon publizierte Themen (Liste).
Bei zwei Meldungen zum selben Ereignis: die ausführlichere wählen.

Antworte NUR mit JSON:
{"zgjedhja": [{"i": Index, "p": 1-5, "pse": "1 Satz auf Deutsch: warum Albaner in der Schweiz das lesen/teilen"}],
 "arsye": "kurze Gesamtbegründung auf Deutsch"}"""

REWRITE_SYSTEM = f"""Du bist Redakteur bei UraPress.ch, einem albanischen Nachrichtenportal für
die Diaspora in der Schweiz. Du schreibst eine Meldung aus einem anderen Medium VOLLSTÄNDIG
NEU – auf Albanisch (gjuha standarde, korrekte ë und ç).

Regeln:
- Eigene Worte, eigener Satzbau, eigene Reihenfolge. Keine Sätze aus dem Original übernehmen.
- Fakten exakt übernehmen (Namen, Zahlen, Orte, Daten). NICHTS erfinden, nichts ergänzen,
  was nicht im Original steht. Keine Spekulation.
- Wörtliche Zitate nur kurz (max. ein Satz) und klar zugeordnet ("deklaroi", "sipas tij").
- Meinungen/Analysen klar als Meinung der Person kennzeichnen, nie als Tatsache.
- Namen bei Polizei-/Gerichtsfällen so übernehmen, wie sie im Original stehen (voller Name, wenn
  das Original ihn schreibt – Entscheid der Redaktion). Verdächtige immer als "i dyshuari" bezeichnen,
  nie als Täter, solange es kein Urteil gibt. Ausnahme: Kinder und Jugendliche unter 18 nie mit
  vollem Namen.
- Ton: wie ein erfahrener albanischer Diaspora-Journalist – menschlich, lebendig, nah an
  den Leuten, aber faktentreu. Kein Clickbait, keine Ausrufezeichen im Titel, keine
  Grossbuchstaben-Titel.
- NICHT EINFACH ÜBERSETZEN: Erkläre, was die Meldung FÜR ALBANER IN DER SCHWEIZ bedeutet.
  Bei Schweizer Themen (Bewilligung B/C, Einbürgerung, Familiennachzug, Krankenkasse, AHV, Steuern,
  Löhne, Mieten, Lehre, Verkehr): ein eigener Absatz «Çfarë do të thotë kjo për ju» – wer ist betroffen
  (z. B. Leute mit Ausweis B, Familien mit Kindern, Grenzgänger), ab wann, was man jetzt tun kann.
  Nur mit Fakten aus dem Original oder allgemein bekannten, sicheren Grundregeln (z. B. «Kündigungsfrist
  Grundversicherung 30. November»). KEINE neuen Zahlen, Fristen oder Behauptungen erfinden. Wenn das
  Original dafür nichts hergibt, den Absatz weglassen.
- Bei Albanern in der Schweiz und Schweizer Sport mit albanischen Spielern: die albanische Seite der
  Geschichte nach vorne (Name, Herkunft, Kanton/Klub), soweit sie im Original steht.
- Zahlen, die in verschiedene Richtungen gehen (Schweiz-Durchschnitt steigt, eine Region sinkt), ausdrücklich
  erklären («Kjo është mesatarja – nuk rritet kudo njësoj»), damit es nicht wie ein Widerspruch klingt.
- Zweideutige Wörter vermeiden: «banesa të lira» heisst auch «billige Wohnungen» – für freie/angebotene
  Wohnungen «banesat që ofrohen në treg» schreiben. Angebotsmieten = Mieten neu ausgeschriebener Wohnungen,
  nicht die Miete, die man heute schon zahlt – das so sagen.
- Schweizer Begriffe einmal auf Deutsch in Klammern nennen, damit Leser sie bei Behörden wiedererkennen
  (z. B. «leja C (Niederlassungsbewilligung)», «sigurimi bazë (Grundversicherung)»).

SO VERMEIDEST DU DEN "KI-KLANG" (sehr wichtig – perfekte, gleichförmige Texte wirken maschinell):
- SATZRHYTHMUS MISCHEN. Nicht jeder Satz gleich lang. Setze bewusst auch mal einen sehr
  kurzen Satz (3–5 Wörter) nach einem längeren. Dieser Wechsel ist das Wichtigste.
- NICHT JEDER ARTIKEL GLEICH ANFANGEN. Variiere den Einstieg: mal mit dem Ort, mal mit der
  handelnden Person, mal mit der Zahl/dem Kernfakt, mal mit dem Zeitpunkt. Niemals ein
  Schema-F-Muster über alle Artikel.
- Ein echtes, kurzes Zitat aus dem Original (ein Satz, korrekt zugeordnet mit "deklaroi",
  "tha", "sipas tij/saj") macht den Text lebendig – nutze es, wenn das Original eines hergibt,
  statt alles glattzubügeln.
- Natürliche Übergänge statt Aufzählungs-Takt. Ein Absatz darf an den vorherigen anknüpfen
  ("Por", "Ndërkohë", "Vendimi vjen pasi …") – nicht jeder Absatz als isolierter Block.
- Konkret statt allgemein: Namen, Orte und Zahlen gehören in den Fliesstext, nicht hinter
  Floskeln versteckt.
- VERBOTENE KI-FLOSKELN (nie verwenden): "Në një kohë kur", "Është e rëndësishme të theksohet",
  "Vlen të theksohet se", "Si përfundim", "Në përfundim", "luan një rol kyç", "në një botë
  gjithnjë e më", "Në një zhvillim të rëndësishëm", "Duhet theksuar se", "Në fund të fundit",
  "hap një kapitull të ri", "dërgon një mesazh të qartë".
- Lieber ein schlichter, klarer Satz als ein aufgeblähter. Schreib, wie ein Mensch einem
  anderen die Neuigkeit erzählt – nicht wie ein Pressetext-Generator.
- Die Quelle (z. B. alsat.mk) höchstens EINMAL im Text nennen, am besten gar nicht –
  sie steht automatisch in der Quellen-Box unter dem Artikel. Ausnahme: ein eigenes
  Interview oder eine eigene Recherche des Mediums ("sipas një hulumtimi të …").
- Erster Absatz beantwortet: wer, was, wo, wann.
- Länge: 3–6 Absätze, insgesamt ca. 180–350 Wörter.
- Titel: max. 90 Zeichen, informativ, als ganzer Satz oder klare Aussage. Mit den Wörtern, die Leute
  bei Google auf Albanisch suchen: «Zvicër», Kanton/Stadt (Bernë, Cyrih, St. Gallen …), «leje», «franga»,
  «Krankenkasse», «naturalizim», Klub- und Spielernamen. Keine
  Abkürzungen oder Kürzel aus dem Originaltitel (nicht "Kos:", "MK:", "VIDEO", "FOTO",
  "LAJMI I FUNDIT"), Ländernamen ausschreiben (Kosova, Shqipëria, Maqedonia e Veriut).

Kategorie: genau eine aus {CATEGORIES}.
Schweizer Themen → «Zvicër»; Albaner in der Schweiz → «Diaspora»; Schweizer Sport → «Sport».
Schlagwörter (etiketat): immer den Kanton/Ort und das Hauptthema; bei Schweizer Fussball/Sport
zusätzlich «Sport CH»; bei Bewilligungen «Leje qëndrimi»; bei Einbürgerung «Naturalizim»;
bei Krankenkasse «Krankenkasse».

Antworte NUR mit JSON in diesem Format:
{{
  "titulli": "...",
  "permbledhja": "1–2 Sätze für den Auszug",
  "paragrafet": ["Absatz 1", "Absatz 2", "..."],
  "kategoria": "...",
  "etiketat": ["3 bis 5 Schlagwörter"],
  "persona": "Vollständiger Name der Hauptperson (Politiker, Sportler, Künstler) oder null",
  "prompt_imazhi": "English prompt for a symbolic, realistic editorial photo of the topic.
                    No real or recognizable people, no text, no logos, no flags with wrong details."
}}"""


def _extract_json(text: str) -> dict:
    """Findet das erste vollständige JSON-Objekt im Text (auch in ```json-Blöcken)."""
    text = re.sub(r"```(?:json)?", "", text)
    decoder = json.JSONDecoder()
    pos = text.find("{")
    while pos != -1:
        try:
            obj, _ = decoder.raw_decode(text, pos)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
        pos = text.find("{", pos + 1)
    raise ValueError(f"Keine JSON-Antwort von Claude: {text[:300]}")


def _create(max_tokens: int, system: str, user: str):
    """messages.create mit temperature, fällt bei älterer SDK ohne temperature zurück."""
    kwargs = dict(
        model=ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        temperature=0.9,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    try:
        return client.messages.create(**kwargs)
    except TypeError as exc:
        if "temperature" not in str(exc):
            raise
        log.warning("anthropic-SDK ohne 'temperature' – ohne Temperatur erneut")
        kwargs.pop("temperature", None)
        return client.messages.create(**kwargs)


def _ask(system: str, user: str, max_tokens: int = 2500) -> dict:
    last_error = None
    for attempt in range(2):
        msg = _create(max_tokens, system, user)
        text = "".join(getattr(b, "text", "") for b in msg.content if getattr(b, "type", "") == "text")
        if msg.stop_reason == "max_tokens":
            log.warning("Antwort abgeschnitten (max_tokens) – Versuch %d", attempt + 1)
            max_tokens = int(max_tokens * 1.8)
        try:
            return _extract_json(text)
        except ValueError as exc:
            last_error = exc
            log.warning("JSON nicht lesbar (Versuch %d): %s", attempt + 1, str(exc)[:200])
    raise last_error


# Themen für /skano <thema> – gezielt statt zufällig auswählen.
THEMES = {
    "religjion": {
        "label": "Fe & Religjion",
        "aliases": ["religion", "religjion", "religjioni", "fe", "feja", "fetare", "fetë", "besim", "besimi", "islam", "islami"],
        "guide": "lajme fetare: Islami dhe bashkësia islame, jeta fetare e shqiptarëve, xhamia dhe kisha, "
                 "hoxhë/imamë dhe klerikë, festat dhe kremtimet fetare, por edhe besimet e tjera të shqiptarëve",
    },
    "sport": {
        "label": "Sport",
        "aliases": ["sport", "sporti", "sports"],
        "guide": "lajme sportive: futboll dhe basketboll, kombëtaret e Kosovës dhe Shqipërisë, sportistë shqiptarë "
                 "brenda dhe jashtë vendit, ndeshje, transferime, rezultate dhe arritje",
    },
    "showbiz": {
        "label": "Showbiz & Skandale",
        "aliases": ["showbiz", "show", "skandal", "skandale", "vip", "kulture", "kulturë", "muzike", "muzikë"],
        "guide": "showbiz shqiptar: këngëtarë, aktorë, prezantues, influencerë, Big Brother VIP, skandale, "
                 "grindje, dashuri e ndarje, dasma, koncerte dhe paraqitje publike të të famshmëve",
    },
    "gjermani": {
        "label": "Gjermani",
        "aliases": ["gjermani", "gjermania", "germany", "deutschland", "de"],
        "guide": "shqiptarët në Gjermani dhe lajme nga Gjermania që prekin diasporën: punë, leje qëndrimi, "
                 "shtetësi, politikë gjermane, histori të shqiptarëve në qytete gjermane, sport dhe biznes",
    },
    "politik": {
        "label": "Politikë",
        "aliases": ["politik", "politike", "politikë", "politika", "politics", "politik"],
        "guide": "lajme politike: qeveria, parlamenti, zgjedhjet dhe partitë, BE-ja dhe marrëdhëniet ndërkombëtare, "
                 "deklarata të politikanëve të Kosovës, Shqipërisë dhe Maqedonisë së Veriut",
    },
}


def resolve_theme(word: str | None) -> str | None:
    w = (word or "").strip().lower()
    if not w:
        return None
    for key, t in THEMES.items():
        if w == key or w in t["aliases"]:
            return key
    return None


def select_stories(candidates: list[dict], n: int, already_posted: list[str], theme: str | None = None,
                   max_general: int = 1) -> list[dict]:
    """Wählt Meldungen nach Priorität 1–5. Jede gewählte Meldung bekommt story['prioriteti'] und ['pse']."""
    if not candidates:
        return []
    lines = [
        f"[{i}] ({'CH' if c.get('group') == 'ch' else 'Balkan/Welt'} · {c['source']}, {c['published'][:16]}"
        f"{', ' + ', '.join(c['categories'][:3]) if c['categories'] else ''}) "
        f"{c['title']}\n    {c['text'][:300].replace(chr(10), ' ')}"
        for i, c in enumerate(candidates)
    ]
    fokus = ""
    if theme and theme in THEMES:
        fokus = (
            f"FOKUS SOT: Wähle NUR Meldungen zum Thema «{THEMES[theme]['label']}» – {THEMES[theme]['guide']}.\n"
            "Meldungen, die nicht zu diesem Thema passen, NICHT wählen. Mehrere zum selben Thema sind hier erlaubt.\n"
            "Die Quote für p = 4–5 gilt bei einem Fokus-Thema nicht.\n"
            "Wenn gar keine passende Meldung dabei ist, gib eine leere Liste zurück.\n\n"
        )
    user = (
        fokus
        + f"Wähle höchstens {n} Meldungen (weniger, wenn nicht genug gute dabei sind).\n\n"
        f"Bereits publiziert / vorgeschlagen:\n- " + "\n- ".join(already_posted or ["(keine)"])
        + "\n\nKandidaten:\n" + "\n".join(lines)
    )
    result = _ask(SELECT_SYSTEM, user, max_tokens=2000)
    log.info("Auswahl: %s – %s", result.get("zgjedhja"), result.get("arsye"))
    picks, general = [], 0
    for item in result.get("zgjedhja", []):
        if isinstance(item, int):  # Rückfall auf altes Format
            item = {"i": item, "p": 5, "pse": ""}
        i = item.get("i")
        if not isinstance(i, int) or not 0 <= i < len(candidates):
            continue
        try:
            prio = int(item.get("p", 5))
        except (TypeError, ValueError):
            prio = 5
        if prio >= 5 and not theme:
            if general >= max_general:
                log.info("Übersprungen (Quote p5): %s", candidates[i]["title"])
                continue
            general += 1
        story = dict(candidates[i], prioriteti=prio, pse=item.get("pse", ""))
        picks.append(story)
    picks.sort(key=lambda c: c["prioriteti"])
    return picks[:n]


# --- Udhëzues (praktische Ratgeber, 1–2 pro Woche) ------------------------------------------
# Quellen: offizielle Seiten (am 29.10.2026 geprüft, liefern Inhalt). Weitere Themen hier ergänzen.
GUIDES = {
    "leja-c": {
        "titull": "Si merret leja C në Zvicër – kushtet dhe afatet",
        "fokus": "Niederlassungsbewilligung C: nach wie vielen Jahren (Regel und vorzeitige Erteilung), "
                 "Integrationskriterien, Sprachkenntnisse, was zum Verlust führen kann, wo man sie beantragt",
        "urls": ["https://www.sem.admin.ch/sem/de/home/themen/aufenthalt/faq.html"],
    },
    "bashkim-familjar": {
        "titull": "Bashkimi familjar në Zvicër – çfarë duhet të dini",
        "fokus": "Familiennachzug: wer nachziehen darf (Ehepartner, Kinder bis welches Alter), Fristen, "
                 "Wohnung, finanzielle Mittel, Sprache, Unterschied Ausweis B / C / Schweizer Bürger",
        "urls": ["https://www.sem.admin.ch/sem/de/home/themen/aufenthalt/faq.html"],
    },
    "naturalizim": {
        "titull": "Naturalizimi në Zvicër hap pas hapi",
        "fokus": "ordentliche Einbürgerung: Ausweis C, Aufenthaltsjahre, Doppelzählung 8.–18. Altersjahr, "
                 "Integration, Sprache, Ablauf Bund–Kanton–Gemeinde, Kosten, Doppelbürgerschaft",
        "urls": ["https://www.sem.admin.ch/sem/de/home/integration-einbuergerung/schweizer-werden/ordentlich.html",
                 "https://www.sem.admin.ch/sem/de/home/integration-einbuergerung/schweizer-werden/faq.html"],
    },
    "krankenkasse": {
        "titull": "Krankenkasse 2027: si ta zgjidhni më të lirën",
        "fokus": "Grundversicherung wechseln: Prämienrechner priminfo, Kündigungsfrist, Franchise, "
                 "Modelle (Hausarzt, Telmed, HMO), Prämienverbilligung, worauf Familien achten müssen",
        "urls": ["https://www.priminfo.admin.ch/de/praemien"],
    },
    "leja-biometrike": {
        "titull": "Leja biometrike e të huajve në Zvicër – çfarë ndryshon dhe si merret",
        "fokus": "biometrischer Ausländerausweis: wer ihn braucht, Termin, Kosten, Gültigkeit, Reisen",
        "urls": ["https://www.sem.admin.ch/sem/de/home/themen/aufenthalt/biometr_auslaenderausweis.html"],
    },
}

GUIDE_SYSTEM = f"""Du bist Redakteur bei UraPress.ch und schreibst einen PRAKTISCHEN RATGEBER (udhëzues) auf
Albanisch (gjuha standarde, korrekte ë und ç) für Albaner, die in der Schweiz leben. Leute finden ihn über
Google, wenn sie eine konkrete Frage haben.

Grundlage ist NUR der offizielle Text (SEM, Bund, Kanton), den du bekommst. Regeln:
- Alles muss stimmen. Nur Fakten aus dem offiziellen Text. Nichts erfinden, keine Zahlen, Fristen oder
  Kosten, die dort nicht stehen. Wo der Kanton entscheidet, das so sagen («varet nga kantoni»).
- Eigene Worte, einfach und klar, wie man es einem Nachbarn erklärt. Kurze Sätze.
- Schweizer Begriffe einmal auf Deutsch in Klammern (z. B. «leja C (Niederlassungsbewilligung)»).
- Aufbau: kurzer Einstieg (für wen ist das), dann Zwischentitel als eigene Absätze, die mit "## " beginnen
  (z. B. "## Kush ka të drejtë", "## Hapat", "## Afatet", "## Kujdes"), Listen als Absätze mit Zeilen,
  die mit "- " beginnen. Am Ende ein Absatz "## Ku informoheni" mit der zuständigen Stelle.
- Am Schluss der Satz: «Ky udhëzues bazohet në informacionet zyrtare të [Stelle] në datën e publikimit.
  Rregullat mund të ndryshojnë – për rastin tuaj pyesni zyrën e migracionit të kantonit.»
- Länge: 500–900 Wörter.
- Titel: max. 90 Zeichen, mit Suchwörtern (Zvicër, leje, franga …).

Kategorie: «Zvicër». Antworte NUR mit JSON:
{{
  "titulli": "...",
  "permbledhja": "1–2 Sätze",
  "paragrafet": ["...", "## Zwischentitel", "- Punkt 1\n- Punkt 2", "..."],
  "kategoria": "Zvicër",
  "etiketat": ["Udhëzues", "3 bis 4 weitere Schlagwörter"],
  "persona": null,
  "prompt_imazhi": "English prompt for a symbolic, realistic editorial photo of the topic. No people's faces, no text."
}}"""


def write_guide(key: str, official_texts: list[tuple[str, str]]) -> dict:
    g = GUIDES[key]
    src = "\n\n".join(f"=== Quelle: {u} ===\n{t[:9000]}" for u, t in official_texts)
    user = (f"Thema: {g['titull']}\nWas der Ratgeber beantworten soll: {g['fokus']}\n\n"
            f"Offizieller Text:\n{src}")
    data = _ask(GUIDE_SYSTEM, user, max_tokens=5000)
    data["kategoria"] = "Zvicër"
    data["persona"] = None
    tags = [t for t in (data.get("etiketat") or []) if t]
    if "Udhëzues" not in tags:
        tags.insert(0, "Udhëzues")
    data["etiketat"] = tags[:5]
    return data


FB_SYSTEM = """Du schreibst für die Facebook-Seite von UraPress.ch einen Post auf Albanisch (gjuha standarde,
korrekte ë und ç) zu einem Artikel. Leser: Albaner in der Schweiz, viele lesen am Handy auf dem Arbeitsweg.

Regeln:
1. "hyrja" (erste Zeile): macht neugierig, aber ehrlich – kein falsches Clickbait, keine Grossbuchstaben,
   höchstens ein Ausrufe- oder Fragezeichen. Gut: «Nga 1 janari ndryshon Krankenkasse – kush paguan më
   shumë në kantonin e Bernës?» Schlecht: «NUK DO TA BESONI çfarë ndodhi në Zvicër!!!»
2. "permbledhja": 2–3 Sätze: was passiert ist und warum es Albaner in der Schweiz betrifft.
   Nur Fakten aus dem Artikel, nichts dazuerfinden.
3. "pyetja": eine Frage für die Kommentare, die Leute wirklich beantworten wollen
   (z. B. «Si e keni ju këtë në kantonin tuaj?»). Bei Unglücken/Verbrechen/Todesfällen KEINE
   Frage nach Meinungen über Personen – dann eine respektvolle, sachliche Frage oder ein Wunsch.
4. KEIN Link im Text. Der Link kommt in den ersten Kommentar.
5. "hashtags": 2 bis 3, z. B. #Zvicër #Diaspora #Shqiptarët – passend zum Thema (#Bernë, #SportCH …).
6. "koha": "mengjes" (06:30–08:00, Arbeitsweg) oder "mbremje" (18:30–21:00) – was für dieses Thema besser
   passt (Praktisches/Nachrichten eher Morgen, Geschichten/Sport/Unterhaltung eher Abend).

Antworte NUR mit JSON:
{"hyrja": "...", "permbledhja": "...", "pyetja": "...", "hashtags": ["#Zvicër", "#Diaspora"], "koha": "mengjes"}"""


def facebook_post(title: str, excerpt: str, paragraphs: list[str], category: str) -> dict:
    body = "\n\n".join(p for p in paragraphs if not p.startswith("## "))[:5000]
    data = _ask(FB_SYSTEM, f"Kategorie: {category}\nTitel: {title}\nAuszug: {excerpt}\n\nArtikel:\n{body}",
                max_tokens=900)
    tags = []
    for t in data.get("hashtags") or []:
        t = "#" + str(t).lstrip("#").replace(" ", "")
        if len(t) > 1 and t not in tags:
            tags.append(t)
    data["hashtags"] = (tags or ["#Zvicër", "#Diaspora"])[:3]
    data["koha"] = "mbremje" if str(data.get("koha", "")).startswith("mbr") else "mengjes"
    return data


COPY_LIMIT = 0.12  # Anteil 6-Wort-Folgen aus dem Original, ab dem der Text als Kopie gilt


def _ngrams(text: str, n: int = 6) -> set:
    words = re.findall(r"\w+", text.lower())
    return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}


def _copy_ratio(source: str, data: dict) -> float:
    out = " ".join([data.get("titulli", "")] + list(data.get("paragrafet") or []))
    out_grams = _ngrams(out)
    if not out_grams:
        return 0.0
    return len(out_grams & _ngrams(source)) / len(out_grams)

SOCIAL_NOTE = """

SONDERFALL – Beitrag aus {platform}: Die "Notiz der Redaktion" hat der Redakteur selbst geschrieben
(evtl. mit Tipp- oder Grammatikfehlern, evtl. auf Deutsch). Mach daraus eine kurze, saubere Meldung
auf Albanisch: Sprache korrigieren, Inhalt und Aussage des Redakteurs beibehalten, NICHTS dazuerfinden.
Länge: 1–3 Absätze, ca. 50–150 Wörter. Der Original-Beitrag wird automatisch unter dem Text
eingebettet – darauf darfst du verweisen ("siç shihet në postimin më poshtë"), {platform} einmal nennen."""


def rewrite(story: dict) -> dict:
    user = (
        f"Quelle: {story['source']}\nOriginaltitel: {story['title']}\n\n"
        f"Originaltext:\n{story['text'][:7000]}"
    )
    if story.get("social"):  # eigener Text der Redaktion: korrigieren statt Kopie-Prüfung
        data = _ask(REWRITE_SYSTEM + SOCIAL_NOTE.format(platform=story["social"]), user)
    else:
        data = _ask(REWRITE_SYSTEM, user)
    ratio = 0.0 if story.get("social") else _copy_ratio(story["text"], data)
    if ratio > COPY_LIMIT:
        log.warning("Entwurf zu nah am Original (%.0f%%), zweiter Versuch", ratio * 100)
        strict = user + ("\n\nWICHTIG: Der letzte Entwurf war zu nah am Original. Schreibe alles "
                         "komplett neu mit eigenen Sätzen. Übernimm keine Wortgruppen aus dem "
                         "Original, nur die Fakten.")
        data = _ask(REWRITE_SYSTEM, strict)
        ratio = _copy_ratio(story["text"], data)
        if ratio > COPY_LIMIT:
            raise ValueError(f"Text zu nah am Original ({ratio:.0%}), übersprungen")
    if data.get("kategoria") not in CATEGORIES:
        data["kategoria"] = CATEGORIES[0]
    persona = data.get("persona")
    data["persona"] = persona.strip() if isinstance(persona, str) and persona.strip().lower() != "null" else None
    return data
