"""
src/notifications/slack_sender.py — Envoi du rapport sur Slack
===============================================================
"""

import datetime

from src.core.logger import get_logger
from src.core.settings import settings

log = get_logger(__name__)


def send_slack(pdf_path: str, reg_critical: int = 0) -> None:
    """
    Envoie un message et le rapport PDF sur Slack.

    Args:
        pdf_path:     Chemin vers le PDF à uploader.
        reg_critical: Nombre d'alertes critiques (préfixe d'urgence si > 0).
    """
    if not settings.slack_token:
        log.info("SLACK_TOKEN absent — envoi Slack ignore.")
        return
    try:
        from slack_sdk import WebClient
        client = WebClient(token=settings.slack_token)
        today  = datetime.date.today().strftime("%d/%m/%Y")
        prefix = f":rotating_light: *{reg_critical} alerte(s) CRITIQUE(S)*\n" if reg_critical else ""
        client.chat_postMessage(
            channel=settings.slack_channel,
            text=(
                f"{prefix}:stethoscope: *Rapport Veille IA Medicale* — {today}\n"
                f"Modules : Techno · Concurrence · Marches Publics · Reglementaire\n"
                f"Rapport PDF joint."
            ),
        )
        client.files_upload(
            channels=settings.slack_channel,
            file=pdf_path,
            title=f"Veille Complete {datetime.date.today():%d-%m-%Y}",
        )
        log.info("Rapport envoye sur Slack (%s)", settings.slack_channel)
    except Exception as exc:
        log.error("Erreur Slack : %s", exc)
