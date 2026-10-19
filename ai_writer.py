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
1. Nachrichtenwert und Relevanz für Albaner in der Schweiz / im deutschsprachigen Raum.
   Meldungen mit direktem Diaspora-Bezug klar bevorzugen.
2. Vielfalt: nicht mehrmals dasselbe Thema oder dasselbe Land.
3. Ausschliessen: Gedichte, Werbung/Firmen-Promotion, reine Meinungsbeiträge ohne
   Nachrichtenkern, Gerüchte, Meldungen, die schon publiziert wurden (siehe Liste).
4. Bei zwei Meldungen zum selben Ereignis: nur die ausführlichere wählen.

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
- Klingt menschlich: kurze und mittlere Sätze gemischt, natürliche Übergänge. Vermeide
  KI-Floskeln wie "Në një kohë kur", "Është e rëndësishme të theksohet", "Si përfundim",
  "Në përfundim", "luan një rol kyç", "në një botë gjithnjë e më".
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


def _ask(system: str, user: str, max_tokens: int = 2500) -> dict:
    last_error = None
    for attempt in range(2):
        msg = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
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


def select_stories(candidates: list[dict], n: int, already_posted: list[str]) -> list[dict]:
    if len(candidates) <= n:
        return candidates
    lines = [
        f"[{i}] ({c['source']}, {c['published'][:16]}, {', '.join(c['categories'])}) "
        f"{c['title']}\n    {c['text'][:350].replace(chr(10), ' ')}"
        for i, c in enumerate(candidates)
    ]
    user = (
        f"Wähle {n} Meldungen (weniger, wenn nicht genug gute dabei sind).\n\n"
        f"Bereits publiziert / vorgeschlagen:\n- " + "\n- ".join(already_posted or ["(keine)"])
        + "\n\nKandidaten:\n" + "\n".join(lines)
    )
    result = _ask(SELECT_SYSTEM, user, max_tokens=800)
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
