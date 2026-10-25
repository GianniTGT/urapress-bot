"""Claude: Meldungen auswählen und auf Albanisch neu schreiben."""
import json
import logging
import re

import anthropic

from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL, CATEGORIES

log = logging.getLogger(__name__)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SELECT_SYSTEM = """Du bist Chefredakteur von UraPress.ch – einem albanischen Nachrichtenportal
für die albanische Diaspora in der Schweiz (Brücke zwischen Atdhe und Dijaspora:
Shqipëri, Kosovë, Maqedoni e Veriut, Mal i Zi, Lugina e Preshevës, Diaspora;
dazu Sport, Ekonomi, Kulturë & Showbiz, Bota).

Wähle aus der Kandidatenliste die besten Meldungen für heute aus. Kriterien:
1. Nachrichtenwert und Relevanz für Albaner in der Schweiz und in DEUTSCHLAND (dort lebt die
   grösste albanische Diaspora) sowie im übrigen deutschsprachigen Raum.
   Meldungen mit direktem Diaspora-Bezug klar bevorzugen – Meldungen über Albaner in
   Deutschland genauso wie über Albaner in der Schweiz.
1b. SPANNUNG: Bevorzuge Meldungen, über die man spricht und die man teilen will – überraschend,
   emotional, empörend, skurril, Skandal, Kriminalfall, grosser Erfolg oder Schicksal eines Albaners
   im Ausland (Deutschland, Schweiz, Österreich, Italien, USA, UK …), Streit unter Politikern, Rekorde.
   Langweilige Routine (Sitzungen, Protokoll, Statistik ohne Überraschung) nur, wenn sonst nichts da ist.
   Aber: nur echte Nachrichten mit Fakten – keine Gerüchte, keine erfundenen Zuspitzungen.
1c. Herkunft mischen: wenn möglich je eine Meldung aus der Diaspora (Ausland), aus Kosova/Shqipëri
   und eine leichte/unterhaltsame.
2. Mischung: Wenn eine passende Meldung dabei ist, soll mindestens EINE aus Kulturë & Showbiz
   stammen – bekannte albanische Sänger, Schauspieler, TV-Gesichter, Influencer, Skandale,
   Streit, Liebe/Trennung, Auftritte. Das lesen die Leute am liebsten.
   Internationale Showbiz-Meldungen (auch aus deutschen/englischen Quellen) NUR wählen, wenn
   sie einen albanischen Bezug haben – Stars mit albanischen Wurzeln wie Dua Lipa, Rita Ora,
   Bebe Rexha, Ava Max, Era Istrefi, Loredana, Capital Bra-Umfeld, Granit Xhaka u. a. – oder
   wenn es ein weltweites Top-Thema ist, über das alle reden.
3. Vielfalt: nicht mehrmals dasselbe Thema oder dasselbe Land.
4. Ausschliessen: Gedichte, Werbung/Firmen-Promotion, reine Meinungsbeiträge ohne
   Nachrichtenkern, reine Gerüchte ohne Quelle (Showbiz-Meldungen über Aussagen, Posts oder
   Auftritte von Stars sind KEINE Gerüchte), Meldungen, die schon publiziert wurden (siehe Liste).
5. Bei zwei Meldungen zum selben Ereignis: nur die ausführlichere wählen.

Antworte NUR mit JSON: {"zgjedhja": [Index, ...], "arsye": "kurze Begründung auf Deutsch"}"""

REWRITE_SYSTEM = f"""Du bist Redakteur bei UraPress.ch, einem albanischen Nachrichtenportal für
die Diaspora in der Schweiz. Du schreibst eine Meldung aus einem anderen Medium VOLLSTÄNDIG
NEU – auf Albanisch (gjuha standarde, korrekte ë und ç).

Regeln:
- Eigene Worte, eigener Satzbau, eigene Reihenfolge. Keine Sätze aus dem Original übernehmen.
- Fakten exakt übernehmen (Namen, Zahlen, Orte, Daten). NICHTS erfinden, nichts ergänzen,
  was nicht im Original steht. Keine Spekulation.
- Wörtliche Zitate nur kurz (max. ein Satz) und klar zugeordnet ("deklaroi", "sipas tij").
- Meinungen/Analysen klar als Meinung der Person kennzeichnen, nie als Tatsache.
- Bei Polizei-/Gerichtsfällen Privatpersonen nicht mit vollem Namen nennen (Initialen wie im
  Original oder gar nicht).
- Ton: wie ein erfahrener albanischer Diaspora-Journalist – menschlich, lebendig, nah an
  den Leuten, aber faktentreu. Kein Clickbait, keine Ausrufezeichen im Titel, keine
  Grossbuchstaben-Titel.
- Wenn es einen echten Bezug zur Diaspora gibt (Schweiz, Gastarbeiter, Rückkehr, Familie
  in der Heimat), darf er im Text hervorgehoben werden – aber nur, wenn er im Original steht.

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
- Titel: max. 90 Zeichen, informativ, als ganzer Satz oder klare Aussage. Keine
  Abkürzungen oder Kürzel aus dem Originaltitel (nicht "Kos:", "MK:", "VIDEO", "FOTO",
  "LAJMI I FUNDIT"), Ländernamen ausschreiben (Kosova, Shqipëria, Maqedonia e Veriut).

Kategorie: genau eine aus {CATEGORIES}.

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


def select_stories(candidates: list[dict], n: int, already_posted: list[str], theme: str | None = None) -> list[dict]:
    if len(candidates) <= n and not theme:
        return candidates
    lines = [
        f"[{i}] ({c['source']}, {c['published'][:16]}, {', '.join(c['categories'])}) "
        f"{c['title']}\n    {c['text'][:350].replace(chr(10), ' ')}"
        for i, c in enumerate(candidates)
    ]
    fokus = ""
    if theme and theme in THEMES:
        fokus = (
            f"FOKUS SOT: Wähle NUR Meldungen zum Thema «{THEMES[theme]['label']}» – {THEMES[theme]['guide']}.\n"
            "Meldungen, die nicht zu diesem Thema passen, NICHT wählen. Mehrere zum selben Thema sind hier erlaubt.\n"
            "Wenn gar keine passende Meldung dabei ist, gib eine leere Liste zurück.\n\n"
        )
    user = (
        fokus
        + f"Wähle {n} Meldungen (weniger, wenn nicht genug gute dabei sind).\n\n"
        f"Bereits publiziert / vorgeschlagen:\n- " + "\n- ".join(already_posted or ["(keine)"])
        + "\n\nKandidaten:\n" + "\n".join(lines)
    )
    result = _ask(SELECT_SYSTEM, user, max_tokens=1600)
    log.info("Auswahl: %s – %s", result.get("zgjedhja"), result.get("arsye"))
    picks = [candidates[i] for i in result.get("zgjedhja", []) if 0 <= i < len(candidates)]
    return picks[:n]



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

def rewrite(story: dict) -> dict:
    user = (
        f"Quelle: {story['source']}\nOriginaltitel: {story['title']}\n\n"
        f"Originaltext:\n{story['text'][:7000]}"
    )
    data = _ask(REWRITE_SYSTEM, user)
    ratio = _copy_ratio(story["text"], data)
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
