"""
src/core/utils.py — Utilitaires texte et résumé
=================================================
Fonctions de nettoyage de texte et de résumé (extractif ou LLM).
"""

import re

from src.core.logger import get_logger
from src.core.settings import settings

log = get_logger(__name__)

_gpt_model = None


# ================================================================
#  ENCODAGE / NETTOYAGE
# ================================================================

def safe_latin1(text: str) -> str:
    """Encode en Latin-1 pour compatibilité FPDF (remplace les chars inconnus)."""
    return str(text).encode("latin-1", errors="replace").decode("latin-1")


def clean_html(text: str) -> str:
    """Supprime les balises HTML et normalise les espaces."""
    clean = re.sub(r"<[^>]+>", " ", str(text))
    return re.sub(r"\s+", " ", clean).strip()


# ================================================================
#  RÉSUMÉ
# ================================================================

def extractive_summary(text: str, n: int = 2) -> str:
    """Résumé par extraction des n premières phrases non vides."""
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if len(s.strip()) > 20]
    return ". ".join(sentences[:n]) + ("." if sentences else "")


def _load_llm():
    """Charge le modèle GPT4All si configuré, sinon retourne None."""
    global _gpt_model
    if _gpt_model is not None:
        return _gpt_model
    if not settings.gpt4all_model or not settings.gpt4all_path:
        return None
    try:
        from gpt4all import GPT4All
        _gpt_model = GPT4All(
            model_name=settings.gpt4all_model,
            model_path=settings.gpt4all_path,
        )
        log.info("LLM charge : %s", settings.gpt4all_model)
    except Exception as exc:
        log.error("Impossible de charger le LLM : %s", exc)
    return _gpt_model


def summarize(text: str, max_tokens: int = 150) -> str:
    """
    Résume un texte via LLM local (GPT4All) si disponible,
    sinon repli sur résumé extractif.
    """
    model = _load_llm()
    if model is None:
        return extractive_summary(text)
    try:
        prompt = (
            "Resume ce texte pour un medecin specialiste en 2-3 phrases "
            "claires et concises :\n" + text[:2000]
        )
        return model.generate(prompt, max_tokens=max_tokens)
    except Exception as exc:
        log.warning("Erreur LLM : %s", exc)
        return extractive_summary(text)
