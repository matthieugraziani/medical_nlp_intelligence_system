"""
src/agents/publicwatch.py — Agent PublicWatch
=============================================
Collecte les appels d'offres publics via le flux RSS BOAMP.
"""

import os

import feedparser
import pandas as pd

from src.core.logger import get_logger
from src.core.settings import settings

log = get_logger(__name__)

_BOAMP_RSS_URL    = "https://www.boamp.fr/rss"
_IA_KEYWORDS      = ["IA", "imagerie", "intelligence artificielle"]
_MAX_ENTRIES      = 10
_PRIORITY_HIGH    = 3
_PRIORITY_DEFAULT = 1


def _is_ia_related(title: str) -> bool:
    return any(kw.lower() in title.lower() for kw in _IA_KEYWORDS)


def publicwatch_agent() -> pd.DataFrame:
    """
    Collecte les appels d'offres BOAMP et exporte public.csv.

    Returns:
        DataFrame avec colonnes : title, link, date, priority.
    """
    log.info("--- PublicWatch : marches publics ---")
    ao_list: list[dict] = []

    try:
        feed = feedparser.parse(_BOAMP_RSS_URL)
        for entry in feed.entries[:_MAX_ENTRIES]:
            title = getattr(entry, "title", "Sans titre")
            ao_list.append({
                "title":    title,
                "link":     getattr(entry, "link", ""),
                "date":     getattr(entry, "published", "N/A"),
                "priority": _PRIORITY_HIGH if _is_ia_related(title) else _PRIORITY_DEFAULT,
            })
    except Exception as exc:
        log.error("[PublicWatch] Flux BOAMP : %s", exc)

    df = pd.DataFrame(ao_list)
    if not df.empty:
        df = df.sort_values("priority", ascending=False).reset_index(drop=True)

    df.to_csv(os.path.join(settings.data_dir, "public.csv"), index=False, encoding="utf-8-sig")
    log.info("[PublicWatch] %d appels d'offres", len(df))
    return df
