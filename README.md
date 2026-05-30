# Veille IA Médicale

Système de veille automatisé couvrant la littérature scientifique,
le marché concurrentiel, les marchés publics et la réglementation
dans le domaine de l'IA médicale.

---

## Arborescence

```
veille_ia_medicale/
│
├── main.py                         # Point d'entrée — orchestrateur + scheduler
├── requirements.txt
├── .env.example                    # Template de configuration
│
├── config/                         # Constantes & configuration des sources
│   ├── __init__.py
│   └── sources.py                  # URLs RSS, mots-clés, palettes couleurs
│
├── src/                            # Code source
│   ├── __init__.py
│   │
│   ├── core/                       # Socle technique partagé
│   │   ├── __init__.py
│   │   ├── settings.py             # Variables d'env (dataclass typée)
│   │   ├── logger.py               # Factory de logger centralisé
│   │   ├── utils.py                # Nettoyage texte + résumé LLM/extractif
│   │   └── scoring.py              # Calcul des scores de priorité
│   │
│   ├── agents/                     # Agents de collecte de données
│   │   ├── __init__.py
│   │   ├── techwatch.py            # PubMed · ArXiv · Scholar · ClinicalTrials
│   │   ├── marketwatch.py          # Veille concurrentielle
│   │   ├── publicwatch.py          # Marchés publics (BOAMP)
│   │   └── regulatory.py           # FDA · CE/MDR · HAS · ANSM · IMDRF
│   │
│   ├── reporting/                  # Génération du rapport PDF
│   │   ├── __init__.py
│   │   ├── pdf_helpers.py          # Primitives FPDF (blocs, couleurs, titres)
│   │   └── pdf_builder.py          # Assemblage du rapport complet (5 sections)
│   │
│   └── notifications/              # Envoi des rapports
│       ├── __init__.py
│       ├── email_sender.py         # Envoi SMTP avec PDF en pièce jointe
│       └── slack_sender.py         # Upload Slack
│
├── tests/                          # Tests unitaires
│   ├── __init__.py
│   └── test_scoring.py
│
├── data/          → outputs/exports/   # CSVs générés par les agents
├── logs/                               # Logs horodatés
└── outputs/
    ├── reports/                        # Rapports PDF générés
    └── exports/                        # Exports CSV par source
```

---

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# Éditer .env avec vos identifiants
```

## Usage

```bash
# Lancement immédiat
python main.py --now

# Mode scheduler (selon SCHEDULE_DAY / SCHEDULE_TIME dans .env)
python main.py

# Tests unitaires
pytest tests/ -v
```

---

## Variables d'environnement

| Variable        | Défaut              | Description                    |
|-----------------|---------------------|--------------------------------|
| SMTP_EMAIL      | —                   | Adresse expéditeur             |
| SMTP_PASSWORD   | —                   | Mot de passe SMTP              |
| SMTP_SERVER     | smtp.gmail.com      | Serveur SMTP                   |
| SMTP_PORT       | 587                 | Port SMTP                      |
| EMAIL_RECEIVER  | —                   | Destinataire du rapport        |
| SLACK_TOKEN     | —                   | Token bot Slack (optionnel)    |
| SLACK_CHANNEL   | #general            | Canal Slack cible              |
| SCHEDULE_DAY    | monday              | Jour de lancement automatique  |
| SCHEDULE_TIME   | 09:00               | Heure de lancement automatique |
| GPT4ALL_MODEL   | —                   | Modèle GPT4All (optionnel)     |
| GPT4ALL_PATH    | —                   | Chemin vers le modèle          |

---

## Dépendances entre modules

```
main.py
 ├── src/core/settings.py    ← singleton partagé par tous
 ├── src/core/logger.py      ← factory de logger
 ├── src/agents/             ← utilisent core/ + config/
 ├── src/reporting/          ← utilise core/ + config/
 └── src/notifications/      ← utilise core/settings uniquement
```
