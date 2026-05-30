"""
src/agents/regulatory.py — Agent RegulatoryWatch
=================================================
Collecte les flux RSS des autorités réglementaires
(FDA, CE/MDR, HAS, ANSM, IMDRF) et calcule un niveau de criticité.
"""

import os

import feedparser
import pandas as pd

from config.sources import REG_SOURCES
from src.core.logger import get_logger
from src.core.settings import settings
from src.core.utils import clean_html
from src.core.scoring import reg_priority

log = get_logger(__name__)

_MAX_ENTRIES  = 15
_EXCERPT_WORDS = 80


def _build_excerpt(raw: str) -> str:
    """Retourne les premiers mots d'un texte brut avec ellipse si tronqué."""
    words = raw.split()
    return " ".join(words[:_EXCERPT_WORDS]) + ("..." if len(words) > _EXCERPT_WORDS else "")


def regulatory_agent() -> dict[str, pd.DataFrame]:
    """
    Collecte les flux RSS réglementaires et exporte un CSV par autorité.

    Returns:
        Dictionnaire {nom_autorité: DataFrame} trié par priorité décroissante.
        Colonnes : source, theme, title, link, date, excerpt, priority, label.
    """
    log.info("--- RegulatoryWatch : collecte reglementaire ---")
    results: dict[str, pd.DataFrame] = {}
    global_seen: set[str] = set()

    for source, feeds in REG_SOURCES.items():
        items: list[dict] = []

        for feed_info in feeds:
            url = feed_info.get("url", "").strip()
            if not url:
                continue
            try:
                feed = feedparser.parse(url, request_headers={"User-Agent": "Mozilla/5.0"})
            except Exception as exc:
                log.error("[Regulatory/%s] Erreur %s : %s", source, url, exc)
                continue
            if feed.bozo and not feed.entries:
                log.warning("[Regulatory/%s] Flux indisponible : %s", source, url)
                continue

            for entry in feed.entries[:_MAX_ENTRIES]:
                link = getattr(entry, "link", "").strip()
                if not link or link in global_seen:
                    continue
                global_seen.add(link)
                title  = getattr(entry, "title", "Sans titre").strip()
                raw    = clean_html(getattr(entry, "summary", "") or title)
                score, label = reg_priority(title, raw, source)
                items.append({
                    "source":   source,
                    "theme":    feed_info["theme"],
                    "title":    title,
                    "link":     link,
                    "date":     getattr(entry, "published", getattr(entry, "updated", "N/A")),
                    "excerpt":  _build_excerpt(raw),
                    "priority": score,
                    "label":    label,
                })

        df = pd.DataFrame(items)
        if not df.empty:
            df = df.sort_values("priority", ascending=False).reset_index(drop=True)

        safe_name = source.replace("/", "-").replace(" ", "_")
        df.to_csv(
            os.path.join(settings.data_dir, f"reg_{safe_name}.csv"),
            index=False,
            encoding="utf-8-sig",
        )
        results[source] = df
        log.info("[Regulatory] %s : %d items", source, len(df))

    return results
