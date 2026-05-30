"""
src/reporting/pdf_builder.py — Assemblage du rapport PDF
=========================================================
Génère le rapport PDF unifié (page de garde + 5 sections)
à partir des résultats des 4 agents.
"""

import datetime
import os

import pandas as pd
from fpdf import FPDF

from config.sources import TECH_SOURCE_COLORS, REG_SOURCE_COLORS
from src.core.logger import get_logger
from src.core.settings import settings
from src.core.utils import safe_latin1
from src.reporting.pdf_helpers import (
    DEFAULT_COLOR,
    set_fill,
    reset_colors,
    section_title,
    source_header,
    theme_sub,
    tech_block,
    reg_block,
)

log = get_logger(__name__)


# ================================================================
#  PAGE DE GARDE
# ================================================================

def _build_cover(
    pdf: FPDF,
    today: str,
    tech_total: int,
    reg_total: int,
    reg_critical: int,
    tech_results: dict[str, pd.DataFrame],
    reg_results: dict[str, pd.DataFrame],
) -> None:
    """Génère la page de garde avec statistiques, sommaire et légendes."""
    pdf.add_page()
    pdf.set_fill_color(30, 39, 46)
    pdf.rect(0, 0, 210, 60, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 22)
    pdf.ln(12)
    pdf.cell(0, 14, "Rapport de Veille IA Medicale", ln=True, align="C")
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 9, "Technologique · Concurrentielle · Reglementaire", ln=True, align="C")
    reset_colors(pdf)
    pdf.ln(10)

    # Statistiques
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, safe_latin1(f"Date : {today}"), ln=True, align="C")
    pdf.cell(0, 7, safe_latin1(f"Articles scientifiques analyses : {tech_total}"), ln=True, align="C")
    pdf.cell(0, 7, safe_latin1(f"Mises a jour reglementaires : {reg_total}"), ln=True, align="C")

    if reg_critical:
        pdf.ln(4)
        set_fill(pdf, 231, 76, 60)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(
            0, 10,
            safe_latin1(f"  ATTENTION : {reg_critical} alerte(s) reglementaire(s) CRITIQUE(S)"),
            ln=True, fill=True,
        )
        reset_colors(pdf)

    pdf.ln(8)

    # Sommaire
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Sommaire", ln=True)
    pdf.set_font("Arial", "", 10)
    sections = [
        ("1", "Alertes Reglementaires Critiques",    reg_critical > 0),
        ("2", "Veille Technologique & Scientifique", True),
        ("3", "Veille Concurrentielle",              True),
        ("4", "Veille Marches Publics",              True),
        ("5", "Veille Reglementaire Complete",       True),
    ]
    for num, title, active in sections:
        marker = ">>>" if active else "   "
        pdf.cell(0, 6, safe_latin1(f"  {marker}  Section {num}  —  {title}"), ln=True)
    pdf.ln(6)

    # Légende sources scientifiques
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "Sources scientifiques :", ln=True)
    pdf.set_font("Arial", "", 9)
    for src in tech_results:
        r, g, b = TECH_SOURCE_COLORS.get(src, DEFAULT_COLOR)
        set_fill(pdf, r, g, b)
        pdf.cell(50, 6, safe_latin1(f"  {src}"), fill=True)
        reset_colors(pdf)
        pdf.cell(3)
    pdf.ln(10)

    # Légende autorités réglementaires
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "Autorites reglementaires :", ln=True)
    for src in reg_results:
        r, g, b = REG_SOURCE_COLORS.get(src, DEFAULT_COLOR)
        set_fill(pdf, r, g, b)
        pdf.cell(35, 6, safe_latin1(f"  {src}"), fill=True)
        reset_colors(pdf)
        pdf.cell(3)
    pdf.ln(10)

    # Légende niveaux de criticité
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "Niveaux de priorite reglementaire :", ln=True)
    pdf.set_font("Arial", "", 9)
    for score, lbl, (r, g, b) in [
        (5, "CRITIQUE", (231, 76,  60)),
        (4, "HAUTE",    (230, 126, 34)),
        (3, "MOYENNE",  (52,  152, 219)),
        (2, "FAIBLE",   (189, 195, 199)),
        (1, "INFO",     (236, 240, 241)),
    ]:
        set_fill(pdf, r, g, b, text_white=(score >= 3))
        pdf.cell(55, 6, safe_latin1(f"  {'X'*score}{'.'*(5-score)}  {lbl}"), fill=True)
        reset_colors(pdf)
        pdf.cell(3)
    pdf.ln(10)


# ================================================================
#  SECTIONS DU RAPPORT
# ================================================================

def _section_critiques(pdf: FPDF, reg_results: dict[str, pd.DataFrame]) -> None:
    critical_rows = pd.concat(
        [df[df["priority"] == 5] for df in reg_results.values() if not df.empty],
        ignore_index=True,
    ) if reg_results else pd.DataFrame()

    if critical_rows.empty:
        return

    section_title(pdf, "1.", "ALERTES REGLEMENTAIRES CRITIQUES")
    set_fill(pdf, 231, 76, 60)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "  Action immediate requise", ln=True, fill=True)
    reset_colors(pdf)
    pdf.ln(3)
    for idx, (_, row) in enumerate(critical_rows.iterrows(), 1):
        reg_block(pdf, row, idx)


def _section_techno(pdf: FPDF, tech_results: dict[str, pd.DataFrame], tech_total: int) -> None:
    section_title(pdf, "2.", "Veille Technologique & Scientifique")
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, safe_latin1(
        f"Sources : PubMed · ArXiv · Google Scholar · ClinicalTrials.gov\n"
        f"Domaines : Radiologie · Oncologie · IA medicale · Neurologie\n"
        f"Total : {tech_total} articles analyses"
    ))
    pdf.ln(4)
    for src, df in tech_results.items():
        if df.empty:
            continue
        source_header(pdf, src, TECH_SOURCE_COLORS, len(df), "articles")
        for theme, group in df.groupby("theme"):
            theme_sub(pdf, str(theme))
            for idx, (_, row) in enumerate(group.head(8).iterrows(), 1):
                tech_block(pdf, row, idx)
        pdf.ln(4)


def _section_concurrence(pdf: FPDF, df_market: pd.DataFrame) -> None:
    section_title(pdf, "3.", "Veille Concurrentielle")
    if not df_market.empty:
        for _, row in df_market.iterrows():
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 6, safe_latin1(f"- {row['name']}"), ln=True)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 5, safe_latin1(
                f"  Statut : {row['status']}  |  Financement : {row['funding']}"
                f"  |  Regulation : {row['regulation']}  |  Priorite : {row['priority']}/3"
            ))
            pdf.ln(2)
    else:
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 6, "Aucune donnee concurrentielle disponible.", ln=True)


def _section_marches(pdf: FPDF, df_public: pd.DataFrame) -> None:
    section_title(pdf, "4.", "Veille Marches Publics")
    if not df_public.empty:
        for _, row in df_public.iterrows():
            pdf.set_font("Arial", "B", 10)
            pdf.multi_cell(0, 6, safe_latin1(f"- {row['title']}"))
            pdf.set_font("Arial", "", 9)
            pdf.multi_cell(0, 5, safe_latin1(f"  Date : {row['date']}  |  Priorite : {row['priority']}/3"))
            pdf.set_text_color(0, 0, 200)
            pdf.multi_cell(0, 5, safe_latin1(f"  {row['link']}"))
            reset_colors(pdf)
            pdf.ln(2)
    else:
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 6, "Aucun appel d'offres disponible.", ln=True)


def _section_reglementaire(
    pdf: FPDF,
    reg_results: dict[str, pd.DataFrame],
    reg_total: int,
    reg_critical: int,
) -> None:
    section_title(pdf, "5.", "Veille Reglementaire Complete")
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, safe_latin1(
        f"Autorites : FDA · CE/MDR · HAS · ANSM · IMDRF\n"
        f"Total : {reg_total} mises a jour  |  Critiques : {reg_critical}"
    ))
    pdf.ln(4)
    for src, df in reg_results.items():
        if df.empty:
            continue
        source_header(pdf, src, REG_SOURCE_COLORS, len(df), "mises a jour")
        for theme, group in df.groupby("theme"):
            theme_sub(pdf, str(theme))
            for idx, (_, row) in enumerate(group.head(10).iterrows(), 1):
                reg_block(pdf, row, idx)
        pdf.ln(5)


# ================================================================
#  POINT D'ENTRÉE PUBLIC
# ================================================================

def generate_unified_pdf(
    tech_results: dict[str, pd.DataFrame],
    df_market:    pd.DataFrame,
    df_public:    pd.DataFrame,
    reg_results:  dict[str, pd.DataFrame],
) -> str:
    """
    Génère le rapport PDF unifié complet (page de garde + 5 sections).

    Args:
        tech_results: Résultats de techwatch_agent().
        df_market:    Résultats de marketwatch_agent().
        df_public:    Résultats de publicwatch_agent().
        reg_results:  Résultats de regulatory_agent().

    Returns:
        Chemin absolu vers le fichier PDF généré.
    """
    today        = datetime.date.today().strftime("%d-%m-%Y")
    tech_total   = sum(len(df) for df in tech_results.values())
    reg_total    = sum(len(df) for df in reg_results.values())
    reg_critical = sum(
        len(df[df["priority"] == 5]) for df in reg_results.values() if not df.empty
    )

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    _build_cover(pdf, today, tech_total, reg_total, reg_critical, tech_results, reg_results)
    _section_critiques(pdf, reg_results)
    _section_techno(pdf, tech_results, tech_total)
    _section_concurrence(pdf, df_market)
    _section_marches(pdf, df_public)
    _section_reglementaire(pdf, reg_results, reg_total, reg_critical)

    pdf_path = os.path.join(settings.reports_dir, f"veille_complete_{today}.pdf")
    pdf.output(pdf_path)
    log.info("PDF unifie genere -> %s", pdf_path)
    return pdf_path
