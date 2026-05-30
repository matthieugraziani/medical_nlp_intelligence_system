"""
src/core/settings.py — Configuration centralisée via dataclass
==============================================================
Charge toutes les variables d'environnement en un seul objet
typé. Les modules consomment Settings() au lieu d'appeler
os.getenv() directement.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    # ── Répertoires ──────────────────────────────────────────
    base_dir:    Path = field(default_factory=lambda: Path(__file__).resolve().parents[3])
    log_dir:     Path = field(default_factory=lambda: Path("logs"))
    data_dir:    Path = field(default_factory=lambda: Path("outputs/exports"))
    reports_dir: Path = field(default_factory=lambda: Path("outputs/reports"))

    # ── SMTP ─────────────────────────────────────────────────
    smtp_email:     str = field(default_factory=lambda: os.getenv("SMTP_EMAIL", ""))
    smtp_password:  str = field(default_factory=lambda: os.getenv("SMTP_PASSWORD", ""))
    smtp_server:    str = field(default_factory=lambda: os.getenv("SMTP_SERVER", "smtp.gmail.com"))
    smtp_port:      int = field(default_factory=lambda: int(os.getenv("SMTP_PORT", 587)))
    email_receiver: str = field(default_factory=lambda: os.getenv("EMAIL_RECEIVER", "destinataire@example.com"))

    # ── Slack ────────────────────────────────────────────────
    slack_token:   str = field(default_factory=lambda: os.getenv("SLACK_TOKEN", ""))
    slack_channel: str = field(default_factory=lambda: os.getenv("SLACK_CHANNEL", "#general"))

    # ── Scheduler ────────────────────────────────────────────
    schedule_day:  str = field(default_factory=lambda: os.getenv("SCHEDULE_DAY", "monday"))
    schedule_time: str = field(default_factory=lambda: os.getenv("SCHEDULE_TIME", "09:00"))

    # ── LLM local (optionnel) ────────────────────────────────
    gpt4all_model: str = field(default_factory=lambda: os.getenv("GPT4ALL_MODEL", ""))
    gpt4all_path:  str = field(default_factory=lambda: os.getenv("GPT4ALL_PATH", ""))

    def validate(self) -> None:
        """Émet des avertissements si des variables critiques sont absentes."""
        from src.core.logger import get_logger
        log = get_logger(__name__)
        missing = [v for v in ("SMTP_EMAIL", "SMTP_PASSWORD", "SMTP_SERVER") if not os.getenv(v)]
        if missing:
            log.warning("Variables SMTP manquantes : %s — emails desactives.", ", ".join(missing))
        if not self.slack_token:
            log.info("SLACK_TOKEN absent — alertes Slack desactivees.")

    def make_dirs(self) -> None:
        """Crée les répertoires de travail s'ils n'existent pas."""
        for d in (self.log_dir, self.data_dir, self.reports_dir):
            Path(d).mkdir(parents=True, exist_ok=True)


# Instance partagée (singleton léger)
settings = Settings()
