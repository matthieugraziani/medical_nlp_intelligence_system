"""
src/reporting/pdf_helpers.py — Primitives de rendu PDF
=======================================================
Fonctions bas niveau pour la mise en forme FPDF :
couleurs, bandeaux, titres de section, blocs articles.
"""

import pandas as pd
from fpdf import FPDF

from src.core.utils import safe_latin1
from src.core.scoring import priority_stars

DEFAULT_COLOR: tuple[int, int, int] = (52, 73, 94)


# ================================================================
#  COULEURS & RESET
# ================================================================

def set_fill(pdf: FPDF, r: int, g: int, b: int, text_white: bool = True) -> None:
    """Applique couleur de fond et couleur de texte (blanc ou noir)."""
    pdf.set_fill_color(r, g, b)
    if text_white:
        pdf.set_text_color(255, 255, 255)
    else:
        pdf.set_text_color(0, 0, 0)


def reset_colors(pdf: FPDF) -> None:
    """Remet texte noir et fond blanc."""
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)


# ================================================================
#  TITRES & EN-TÊTES
# ================================================================

def section_title(pdf: FPDF, num: str, title: str) -> None:
    """Titre de section principal sur nouvelle page (fond sombre)."""
    pdf.add_page()
    pdf.set_fill_color(30, 39, 46)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 13, safe_latin1(f"  {num}  {title}"), ln=True, fill=True)
    reset_colors(pdf)
    pdf.ln(3)


def source_header(
    pdf: FPDF,
    source: str,
    colors: dict[str, tuple[int, int, int]],
    count: int,
    label: str = "articles",
) -> None:
    """Bandeau coloré identifiant une source avec compteur."""
    r, g, b = colors.get(source, DEFAULT_COLOR)
    set_fill(pdf, r, g, b)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, safe_latin1(f"  {source}  ({count} {label})"), ln=True, fill=True)
    reset_colors(pdf)
    pdf.ln(2)


def theme_sub(pdf: FPDF, theme: str) -> None:
    """Sous-titre de thème sur fond gris clair."""
    pdf.set_fill_color(240, 240, 240)
    pdf.set_text_color(30, 39, 46)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, safe_latin1(f"   > {theme}"), ln=True, fill=True)
    reset_colors(pdf)
    pdf.set_font("Arial", "", 10)
    pdf.ln(1)


# ================================================================
#  BLOCS D'ARTICLE
# ================================================================

def tech_block(pdf: FPDF, row: pd.Series, idx: int) -> None:
    """Bloc article scientifique avec titre, date, résumé et lien."""
    stars = priority_stars(row["priority"])
    pdf.set_font("Arial", "B", 10)
    pdf.multi_cell(0, 5, safe_latin1(f"{idx}. {row['title']}"))
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 4, safe_latin1(f"   Date : {row.get('date','N/A')}   Priorite : {stars}"))
    pdf.multi_cell(0, 4, safe_latin1(f"   Resume : {row.get('summary','')}"))
    pdf.set_text_color(0, 0, 200)
    pdf.multi_cell(0, 4, safe_latin1(f"   {row['link']}"))
    reset_colors(pdf)
    pdf.ln(3)


def reg_block(pdf: FPDF, row: pd.Series, idx: int) -> None:
    """Bloc réglementaire avec bandeau couleur selon criticité."""
    score = int(row["priority"])
    label = row.get("label", "INFO")

    # Bandeau couleur selon niveau de criticité
    if score == 5:
        set_fill(pdf, 231, 76, 60)
    elif score == 4:
        set_fill(pdf, 230, 126, 34)
    elif score == 3:
        set_fill(pdf, 52, 152, 219)
    else:
        pdf.set_fill_color(236, 240, 241)
        pdf.set_text_color(0, 0, 0)

    pdf.set_font("Arial", "B", 8)
    bar = "[" + "X" * score + "." * (5 - score) + f"]  {label}"
    pdf.cell(0, 5, safe_latin1(f"  {bar}"), ln=True, fill=True)
    reset_colors(pdf)

    pdf.set_font("Arial", "B", 10)
    pdf.multi_cell(0, 5, safe_latin1(f"{idx}. {row['title']}"))
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 4, safe_latin1(f"   Date : {row.get('date','N/A')}"))
    if row.get("excerpt"):
        pdf.multi_cell(0, 4, safe_latin1(f"   {row['excerpt']}"))
    pdf.set_text_color(0, 0, 200)
    pdf.multi_cell(0, 4, safe_latin1(f"   {row['link']}"))
    reset_colors(pdf)
    pdf.ln(4)
