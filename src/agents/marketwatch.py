"""
src/agents/marketwatch.py — Agent MarketWatch
=============================================
Collecte les données concurrentielles.
À connecter à une source live (API, scraping) selon les besoins.
"""

import os

import pandas as pd

from src.core.logger import get_logger
from src.core.settings import settings

log = get_logger(__name__)


def marketwatch_agent() -> pd.DataFrame:
    """
    Retourne le paysage concurrentiel trié par priorité.
    Exporte market.csv dans le répertoire d'exports.

    Returns:
        DataFrame avec colonnes : name, status, funding, regulation, priority.
    """
    log.info("--- MarketWatch : concurrence ---")

    # TODO : remplacer par une source live (API interne, scraping, flux RSS)
    competitors = [
        {"name": "BrainScanAI",  "status": "market",  "funding": "5M EUR", "regulation": "FDA approved", "priority": 3},
        {"name": "NeuroVision",  "status": "preprod", "funding": "2M EUR", "regulation": "CE",           "priority": 2},
        {"name": "NeuroScanPro", "status": "R&D",     "funding": "1M EUR", "regulation": "pending",      "priority": 1},
    ]

    df = pd.DataFrame(competitors).sort_values("priority", ascending=False)
    df.to_csv(os.path.join(settings.data_dir, "market.csv"), index=False, encoding="utf-8-sig")
    log.info("[MarketWatch] %d concurrents", len(df))
    return df
