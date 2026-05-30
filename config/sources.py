"""
config/sources.py — Configuration des sources RSS et des règles de scoring
===========================================================================
Centralise les URLs, mots-clés et palettes couleurs PDF.
Aucune logique métier : uniquement des constantes.
"""

# ================================================================
#  MODULE 1 — SOURCES TECHWATCH
# ================================================================
TECH_SOURCES: dict[str, list[dict]] = {
    "PubMed": [
        {
            "theme": "Radiologie / Imagerie medicale",
            "url": "https://pubmed.ncbi.nlm.nih.gov/rss/search/?term=radiology+medical+imaging+AI&limit=20&sort=date",
        },
        {
            "theme": "Oncologie",
            "url": "https://pubmed.ncbi.nlm.nih.gov/rss/search/?term=oncology+deep+learning+diagnosis&limit=20&sort=date",
        },
        {
            "theme": "IA medicale generale",
            "url": "https://pubmed.ncbi.nlm.nih.gov/rss/search/?term=artificial+intelligence+clinical+medicine&limit=20&sort=date",
        },
        {
            "theme": "Neurologie",
            "url": "https://pubmed.ncbi.nlm.nih.gov/rss/search/?term=neurology+neuroimaging+machine+learning&limit=20&sort=date",
        },
        {
            "theme": "Tumeurs cerebrales & IRM",
            "url": "https://pubmed.ncbi.nlm.nih.gov/rss/search/1P5xyB4cY7nR?term=brain+tumor+MRI&limit=20&sort=date",
        },
    ],
    "ArXiv": [
        {"theme": "Traitement image medicale (eess.IV)", "url": "https://arxiv.org/rss/eess.IV"},
        {"theme": "Machine Learning medical (cs.LG)",    "url": "https://arxiv.org/rss/cs.LG"},
        {"theme": "Computer Vision medical (cs.CV)",     "url": "https://arxiv.org/rss/cs.CV"},
    ],
    "Google Scholar": [
        {"theme": "Radiologie IA - Scholar",  "url": ""},  # TODO : URL alerte RSS Scholar
        {"theme": "Oncologie IA - Scholar",   "url": ""},  # TODO : URL alerte RSS Scholar
    ],
    "ClinicalTrials": [
        {
            "theme": "Essais IA & Radiologie",
            "url": (
                "https://clinicaltrials.gov/api/v2/studies"
                "?format=rss&query.term=artificial+intelligence+radiology"
                "&filter.overallStatus=RECRUITING&pageSize=20"
            ),
        },
        {
            "theme": "Essais IA & Oncologie",
            "url": (
                "https://clinicaltrials.gov/api/v2/studies"
                "?format=rss&query.term=deep+learning+oncology"
                "&filter.overallStatus=RECRUITING&pageSize=20"
            ),
        },
        {
            "theme": "Essais IA & Neurologie",
            "url": (
                "https://clinicaltrials.gov/api/v2/studies"
                "?format=rss&query.term=AI+neurology+brain"
                "&filter.overallStatus=RECRUITING&pageSize=20"
            ),
        },
    ],
}

TECH_KEYWORDS: list[str] = [
    "AI", "deep learning", "neural network", "transformer",
    "segmentation", "detection", "glioblastoma", "FDA", "CE mark",
    "randomized", "multicenter", "prospective", "benchmark",
]

TECH_SOURCE_COLORS: dict[str, tuple[int, int, int]] = {
    "PubMed":         (41,  128, 185),
    "ArXiv":          (192,  57,  43),
    "Google Scholar": (39,  174,  96),
    "ClinicalTrials": (142,  68, 173),
}


# ================================================================
#  MODULE 2 — SOURCES REGULATORY WATCH
# ================================================================
REG_SOURCES: dict[str, list[dict]] = {
    "FDA": [
        {
            "theme": "News & Devices IA",
            "url": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/medical-devices/rss.xml",
        },
        {
            "theme": "Safety Communications",
            "url": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/medwatch-safety-alerts/rss.xml",
        },
        {
            "theme": "Digital Health & IA Policy",
            "url": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/fda-news-releases/rss.xml",
        },
    ],
    "CE/MDR": [
        {
            "theme": "Reglements DM & IVDR",
            "url": "https://eur-lex.europa.eu/tools/rss.do?other=&type=qry&query=MDR+dispositifs+medicaux+intelligence+artificielle&lg=fr&collection=eu-law",
        },
        {
            "theme": "AI Act - Secteur medical",
            "url": "https://eur-lex.europa.eu/tools/rss.do?other=&type=qry&query=AI+Act+dispositifs+medicaux&lg=fr&collection=eu-law",
        },
    ],
    "HAS": [
        {
            "theme": "Recommandations & Referentiels",
            "url": "https://www.has-sante.fr/jcms/fc_1210288/fr/flux-rss?portletId=fc_1210288&cid=c_1210288",
        },
        {
            "theme": "Avis Dispositifs medicaux",
            "url": "https://www.has-sante.fr/jcms/fc_1248478/fr/flux-rss?portletId=fc_1248478&cid=c_1248478",
        },
    ],
    "ANSM": [
        {
            "theme": "Decisions & Alertes",
            "url": "https://ansm.sante.fr/rss/actualites",
        },
        {
            "theme": "Rappels de produits",
            "url": "https://ansm.sante.fr/rss/rappels-de-produits",
        },
    ],
    "IMDRF": [
        {
            "theme": "Guidelines internationaux DM",
            "url": "https://www.imdrf.org/rss.xml",
        },
    ],
}

REG_KEYWORDS_CRITICAL: list[str] = [
    "recall", "rappel", "urgent", "safety alert", "alerte securite",
    "suspension", "retrait du marche", "market withdrawal", "incident grave",
]
REG_KEYWORDS_HIGH: list[str] = [
    "510(k)", "PMA", "De Novo", "clearance", "approval", "approbation",
    "MDR", "IVDR", "CE marking", "marquage CE", "AI Act", "certification",
]
REG_KEYWORDS_MEDIUM: list[str] = [
    "artificial intelligence", "intelligence artificielle",
    "deep learning", "machine learning", "algorithm", "radiology",
    "radiologie", "oncologie", "neurologie", "medical device",
    "dispositif medical", "SaMD", "guidance", "guideline", "referentiel",
]

CRITICAL_SOURCES: set[str] = {"ANSM"}

REG_SOURCE_COLORS: dict[str, tuple[int, int, int]] = {
    "FDA":    (41,  128, 185),
    "CE/MDR": (39,  174,  96),
    "HAS":    (231,  76,  60),
    "ANSM":   (230, 126,  34),
    "IMDRF":  (142,  68, 173),
}

REG_PRIORITY_LABELS: dict[int, str] = {
    5: "CRITIQUE",
    4: "HAUTE",
    3: "MOYENNE",
    2: "FAIBLE",
    1: "INFO",
}
