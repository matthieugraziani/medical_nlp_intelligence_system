"""
src/agents/techwatch.py — Agent TechWatch
==========================================
Collecte les flux RSS scientifiques (PubMed, ArXiv,
Google Scholar, ClinicalTrials.gov) et calcule un score
de priorité pour chaque article.
"""

import os

import feedparser
import pandas as pd

from config.sources import TECH_SOURCES
from src.core.logger import get_logger
from src.core.settings import settings
from src.core.utils import clean_html, summarize
from src.core.scoring import tech_priority

log = get_logger(__name__)


def techwatch_agent() -> dict[str, pd.DataFrame]:
    """
    Collecte les flux RSS scientifiques et exporte un CSV par source.

    Returns:
        Dictionnaire {nom_source: DataFrame} trié par priorité décroissante.
        Colonnes : source, theme, title, link, date, summary, priority.
    """
    log.info("--- TechWatch : collecte RSS scientifique ---")
    results: dict[str, pd.DataFrame] = {}
    global_seen: set[str] = set()

    for source, feeds in TECH_SOURCES.items():
        items: list[dict] = []

        for feed_info in feeds:
            url = feed_info.get("url", "").strip()
            if not url:
                continue
            try:
                feed = feedparser.parse(url)
            except Exception as exc:
                log.error("[TechWatch/%s] Erreur %s : %s", source, url, exc)
                continue
            if feed.bozo:
                log.warning("[TechWatch/%s] Flux bozo : %s", source, feed.bozo_exception)

            for entry in feed.entries[:20]:
                link = getattr(entry, "link", "").strip()
                if not link or link in global_seen:
                    continue
                global_seen.add(link)
                title   = getattr(entry, "title", "Sans titre").strip()
                raw     = clean_html(getattr(entry, "summary", "") or title)
                items.append({
                    "source":   source,
                    "theme":    feed_info["theme"],
                    "title":    title,
                    "link":     link,
                    "date":     getattr(entry, "published", "N/A"),
                    "summary":  summarize(raw),
                    "priority": tech_priority(title, raw),
                })

        df = pd.DataFrame(items)
        if not df.empty:
            df = df.sort_values("priority", ascending=False).reset_index(drop=True)

        safe_name = source.replace(" ", "_").replace("/", "-")
        df.to_csv(
            os.path.join(settings.data_dir, f"tech_{safe_name}.csv"),
            index=False,
            encoding="utf-8-sig",
        )
        results[source] = df
        log.info("[TechWatch] %s : %d articles", source, len(df))

    return results
