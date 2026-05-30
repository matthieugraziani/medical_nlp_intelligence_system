"""
tests/test_scoring.py — Tests unitaires du module de scoring
=============================================================
Lance avec : pytest tests/
"""

import pytest
from src.core.scoring import tech_priority, priority_stars, reg_priority


class TestTechPriority:
    def test_min_score_no_keywords(self):
        assert tech_priority("titre quelconque", "résumé sans mots-clés") == 1

    def test_score_increases_with_keywords(self):
        score = tech_priority("AI deep learning transformer", "neural network benchmark")
        assert score > 1

    def test_max_score_capped_at_5(self):
        text = " ".join(["AI", "deep learning", "neural network", "transformer",
                         "segmentation", "detection", "FDA", "CE mark", "randomized"])
        assert tech_priority(text, text) == 5


class TestPriorityStars:
    def test_format_length(self):
        for score in range(1, 6):
            assert len(priority_stars(score)) == 5

    def test_stars_content(self):
        assert priority_stars(3) == "***--"
        assert priority_stars(5) == "*****"
        assert priority_stars(1) == "*----"


class TestRegPriority:
    def test_critical_source_always_5(self):
        score, label = reg_priority("titre", "résumé", "ANSM")
        assert score == 5
        assert label == "CRITIQUE"

    def test_critical_keyword_raises_score(self):
        score, label = reg_priority("urgent recall", "safety alert grave", "FDA")
        assert score >= 4

    def test_info_score_for_generic_text(self):
        score, label = reg_priority("generic update", "no keywords here", "FDA")
        assert score == 1
        assert label == "INFO"

    def test_score_capped_at_5(self):
        keywords = "recall rappel urgent safety alert suspension retrait incident grave"
        score, _ = reg_priority(keywords, keywords, "FDA")
        assert score == 5
