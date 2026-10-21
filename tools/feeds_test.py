"""Prüft alle Quellen: wie viele Meldungen jede liefert (oder Fehler).

    cd /opt/urapress-bot && sudo -u urapress venv/bin/python tools/feeds_test.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
import feeds  # noqa: E402

for url in config.FEEDS:
    try:
        n = len(feeds.fetch_feed(url))
        print(f"{'✅' if n else '⚠️ '} {n:3d}  {url}")
    except Exception as exc:
        print(f"❌   –  {url}  ({str(exc)[:80]})")
