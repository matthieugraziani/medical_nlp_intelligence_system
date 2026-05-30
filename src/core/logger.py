"""
src/core/logger.py — Logging centralisé
========================================
Fournit un logger unique avec handlers fichier + console.
Tous les modules appellent get_logger(__name__).
"""

import datetime
import logging
import os
from pathlib import Path


def _setup_root_logger(log_dir: str = "logs") -> None:
    """Configure le logger racine une seule fois."""
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_file = os.path.join(log_dir, f"veille_{datetime.date.today():%Y-%m-%d}.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  [%(name)s]  %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


_initialized = False


def get_logger(name: str) -> logging.Logger:
    """
    Retourne un logger nommé, en initialisant le root logger si nécessaire.

    Args:
        name: Identifiant du logger (typiquement __name__).

    Returns:
        Instance logging.Logger configurée.
    """
    global _initialized
    if not _initialized:
        _setup_root_logger()
        _initialized = True
    return logging.getLogger(name)
