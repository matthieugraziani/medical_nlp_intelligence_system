"""
src/notifications/email_sender.py — Envoi du rapport par email
===============================================================
"""

import datetime
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.core.logger import get_logger
from src.core.settings import settings

log = get_logger(__name__)


def send_email(
    pdf_path: str,
    tech_total: int,
    reg_total: int,
    reg_critical: int,
) -> None:
    """
    Envoie le rapport PDF par email via SMTP.

    Args:
        pdf_path:     Chemin vers le PDF à joindre.
        tech_total:   Nombre d'articles scientifiques collectés.
        reg_total:    Nombre de mises à jour réglementaires.
        reg_critical: Nombre d'alertes critiques.
    """
    cfg = settings
    if not all([cfg.smtp_email, cfg.smtp_password, cfg.smtp_server, cfg.email_receiver]):
        log.error("Config SMTP incomplete — email non envoye.")
        return

    today   = datetime.date.today().strftime("%d/%m/%Y")
    subject = f"[Veille IA Medicale] Rapport complet — {today}"
    if reg_critical:
        subject = f"[CRITIQUE] {subject}  ({reg_critical} alerte(s))"

    body = (
        f"Bonjour,\n\n"
        f"Veuillez trouver en piece jointe le rapport unifie de veille IA medicale du {today}.\n\n"
        f"RESUME :\n"
        f"  - Articles scientifiques analyses : {tech_total}\n"
        f"  - Mises a jour reglementaires    : {reg_total}\n"
        f"  - Alertes critiques              : {reg_critical}\n\n"
        f"MODULES COUVERTS :\n"
        f"  1. Veille Technologique  (PubMed, ArXiv, Scholar, ClinicalTrials)\n"
        f"  2. Veille Concurrentielle\n"
        f"  3. Marches Publics (BOAMP)\n"
        f"  4. Veille Reglementaire  (FDA, CE/MDR, HAS, ANSM, IMDRF)\n\n"
        f"Cordialement."
    )

    msg            = MIMEMultipart()
    msg["From"]    = cfg.smtp_email
    msg["To"]      = cfg.email_receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with open(pdf_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(pdf_path)}")
        msg.attach(part)
    except OSError as exc:
        log.error("Impossible de lire le PDF : %s", exc)
        return

    try:
        with smtplib.SMTP(cfg.smtp_server, cfg.smtp_port) as server:
            server.starttls()
            server.login(cfg.smtp_email, cfg.smtp_password)
            server.sendmail(cfg.smtp_email, cfg.email_receiver, msg.as_string())
        log.info("Email envoye a %s", cfg.email_receiver)
    except smtplib.SMTPException as exc:
        log.error("Erreur SMTP : %s", exc)
