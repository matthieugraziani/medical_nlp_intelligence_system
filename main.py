"""
main.py — Point d'entrée du système de veille IA médicale
==========================================================
Orchestre les 4 agents, génère le rapport PDF et envoie les notifications.

Usage :
    python main.py           # mode scheduler (défaut : lundi 09:00)
    python main.py --now     # lancement immédiat
"""

import argparse
import datetime
import sys
import time

import schedule

from src.core.settings import settings
from src.core.logger import get_logger
from src.agents import techwatch_agent, marketwatch_agent, publicwatch_agent, regulatory_agent
from src.reporting import generate_unified_pdf
from src.notifications import send_email, send_slack

log = get_logger(__name__)

_DAY_MAP = {
    "monday":    schedule.every().monday,
    "tuesday":   schedule.every().tuesday,
    "wednesday": schedule.every().wednesday,
    "thursday":  schedule.every().thursday,
    "friday":    schedule.every().friday,
    "saturday":  schedule.every().saturday,
    "sunday":    schedule.every().sunday,
}


# ================================================================
#  ORCHESTRATEUR
# ================================================================

def run_full_watch() -> None:
    """
    Pipeline complet de veille :
      [1/4] Techno · [2/4] Marché/Publics · [3/4] Réglementaire · [4/4] Rapport + Notifs
    """
    start = datetime.datetime.now()
    log.info("=" * 65)
    log.info("  VEILLE IA MEDICALE COMPLETE — %s", start.strftime("%d/%m/%Y %H:%M"))
    log.info("=" * 65)

    log.info("[1/4] Veille Technologique & Scientifique...")
    tech_results = techwatch_agent()
    tech_total   = sum(len(df) for df in tech_results.values())

    log.info("[2/4] Veille Concurrentielle & Marches Publics...")
    df_market = marketwatch_agent()
    df_public = publicwatch_agent()

    log.info("[3/4] Veille Reglementaire...")
    reg_results  = regulatory_agent()
    reg_total    = sum(len(df) for df in reg_results.values())
    reg_critical = sum(
        len(df[df["priority"] == 5]) for df in reg_results.values() if not df.empty
    )
    if reg_critical:
        log.warning("!!! %d ALERTE(S) REGLEMENTAIRE(S) CRITIQUE(S) !!!", reg_critical)

    log.info("[4/4] Generation du rapport PDF unifie...")
    pdf_path = generate_unified_pdf(tech_results, df_market, df_public, reg_results)

    send_email(pdf_path, tech_total, reg_total, reg_critical)
    send_slack(pdf_path, reg_critical)

    elapsed = (datetime.datetime.now() - start).seconds
    log.info("Pipeline termine en %ds. Rapport : %s", elapsed, pdf_path)
    log.info("=" * 65)


# ================================================================
#  SCHEDULER
# ================================================================

def start_scheduler() -> None:
    """Lance le scheduler selon SCHEDULE_DAY / SCHEDULE_TIME."""
    scheduler = _DAY_MAP.get(settings.schedule_day.lower(), schedule.every().monday)
    scheduler.at(settings.schedule_time).do(run_full_watch)
    log.info(
        "Scheduler actif — prochain lancement : %s a %s",
        settings.schedule_day, settings.schedule_time,
    )
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        log.info("Arret demande (CTRL+C).")


# ================================================================
#  POINT D'ENTRÉE
# ================================================================

if __name__ == "__main__":
    settings.validate()
    settings.make_dirs()

    parser = argparse.ArgumentParser(description="Veille IA Medicale Unifiee")
    parser.add_argument("--now", action="store_true", help="Lance la veille immediatement")
    args = parser.parse_args()

    if args.now:
        run_full_watch()
        sys.exit(0)

    start_scheduler()
