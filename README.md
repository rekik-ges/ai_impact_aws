# AWS GenAI Automation Risk Project

## Projet 

Ce projet analyse l'impact de l'automatisation et de l'IA sur les metiers.
L'idee est de repondre a deux questions simples :

- Quels metiers et secteurs sont les plus exposes ?
- Quelles decisions prendre (reconversion, investissement, preservation) ?

## Dataset utilise

Fichier source : `https://www.kaggle.com/datasets/khushikyad001/ai-automation-risk-by-job-role`

Il contient notamment :

- metier, secteur
- risque d'automatisation
- facteurs metier (repetitivite, creativite, complexite, social, physique)
- colonnes enrichies (salaire, experience, niveau d'etude, demande marche, croissance, formation, dependance IA)

## Problematique

Dans beaucoup d'analyses, on a seulement un score de risque global.
Ici, on veut aller plus loin : expliquer le risque et aider a la decision.

## Valeur du projet (resume)

- vision macro : secteurs et metiers les plus touches
- vision metier : pourquoi ce metier est a risque
- vision decision : quels profils former, preserver ou transformer
- recommandations GenAI lisibles pour un dashboard

## Pipeline retenu (simple)

```text
CSV brut (Kaggle)
-> S3/raw
-> Lambda transform
-> S3/analytics (automation_risk_enriched.csv)
-> Lambda GenAI + Bedrock
-> S3/genai (recommendations.json)
-> Streamlit local
```

> Athena est present dans le repo pour analyse SQL, mais pas obligatoire dans le flux GenAI simple.

## Lancer Streamlit (local)

Depuis le dossier du projet :

```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

Pre-requis avant lancement :

- `streamlit_app/automation_risk_enriched.csv`
- `streamlit_app/recommendations.json`

## Structure rapide

```text
lambda_transform/automation-risk-transform.py
lambda_genai/automation-risk-genai.py
streamlit_app/app.py
sample_data/ai_automation_risk_dataset.csv
docs/aws_steps.md
```
