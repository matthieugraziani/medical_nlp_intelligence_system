"""
src/core/scoring.py — Calcul des scores de priorité
=====================================================
Fonctions de scoring indépendantes des sources RSS,
utilisées par les agents TechWatch et RegulatoryWatch.
"""

from config.sources import (
    TECH_KEYWORDS,
    REG_KEYWORDS_CRITICAL,
    REG_KEYWORDS_HIGH,
    REG_KEYWORDS_MEDIUM,
    CRITICAL_SOURCES,
    REG_PRIORITY_LABELS,
)


# ================================================================
#  SCORING TECHWATCH
# ================================================================

def tech_priority(title: str, summary: str) -> int:
    """
    Calcule un score de priorité (1–5) basé sur la présence
    de mots-clés dans le titre et le résumé.

    Returns:
        Entier entre 1 (faible) et 5 (critique).
    """
    text = (title + " " + summary).lower()
    return min(1 + sum(1 for kw in TECH_KEYWORDS if kw.lower() in text), 5)


def priority_stars(score: int) -> str:
    """
    Représentation visuelle du score : '***--' pour 3/5.

    Returns:
        Chaîne de 5 caractères (* et -).
    """
    return "*" * int(score) + "-" * (5 - int(score))


# ================================================================
#  SCORING REGULATORY WATCH
# ================================================================

def reg_priority(title: str, summary: str, source: str) -> tuple[int, str]:
    """
    Calcule un score de criticité réglementaire (1–5) et son libellé.
    Les sources listées dans CRITICAL_SOURCES sont automatiquement niveau 5.

    Returns:
        Tuple (score: int, label: str).
    """
    if source in CRITICAL_SOURCES:
        return 5, "CRITIQUE"

    text  = (title + " " + summary).lower()
    score = 1
    score += 3 * sum(1 for kw in REG_KEYWORDS_CRITICAL if kw.lower() in text)
    score += 2 * sum(1 for kw in REG_KEYWORDS_HIGH     if kw.lower() in text)
    score += 1 * sum(1 for kw in REG_KEYWORDS_MEDIUM   if kw.lower() in text)
    score  = min(score, 5)
    return score, REG_PRIORITY_LABELS.get(score, "INFO")
