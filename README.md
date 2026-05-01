# AI Job Impact Explorer (AWS + GenAI)

## Contexte

Dans ce projet, on analyse l'impact de l'automatisation et de l'IA sur les metiers pour repondre a deux questions:

- Quels metiers sont les plus exposes ?
- Quelles decisions prendre (reconversion, investissement, preservation) ?


## Besoin

On part d'un dataset Kaggle avec un score de risque, mais on veut aller plus loin:

- nettoyer la donnee,
- expliquer les facteurs de risque,
- produire des recommandations lisibles pour un dashboard.

## Solution retenue

On a choisi une architecture simple, Big Data et peu couteuse:

```text
S3/raw (CSV brut)
-> Lambda orchestrateur (automation-risk-transform)
-> EMR Serverless Spark (clean + transform)
-> S3/curated + S3/quarantine
-> Lambda GenAI + Bedrock
-> S3/genai/recommendations.json
-> Streamlit local
```

## Pourquoi ces composants

- `S3` : stockage brut/clean/rejets/recommandations.
- `Lambda` : orchestration event-driven (leger, simple a exploiter).
- `EMR Serverless Spark` : traitement distribue pour batchs plus volumineux.
- `Bedrock` : generation de recommandations metier.
- `CloudWatch` : logs + alarmes d'erreur.
- `Streamlit` : restitution rapide orientee demo.

## Transformations appliquees (Spark)

- normalisation texte (`job_role`, `industry`, `education_level`),
- imputation `ai_tool_availability` vide -> `Unknown`,
- cast des colonnes numeriques,
- regles de validite:
  - scores entre `0` et `1`,
  - `avg_salary_usd` entre `30000` et `180000`,
  - `experience_required_years` entre `0` et `14`,
- calculs metier:
  - `automation_risk_pct`,
  - `risk_level` (Low / Medium / High),
  - `automation_exposure_pct` et autres pourcentages,
- ajout de `domain` (regroupement par metier),
- sortie des lignes invalides dans `quarantine`.

## Resultat attendu

- `curated` contient les lignes propres prêtes pour analyse.
- `quarantine` contient les lignes invalides pour audit.
- `genai/recommendations.json` contient les recommandations Bedrock.
- Streamlit affiche les visualisations (axe principal: `domain`).

## Comment lancer (resume)

1. lancer `automation-risk-transform` (Lambda orchestrateur),
2. attendre la fin du job EMR Serverless,
3. lancer `automation-risk-genai`,
4. recuperer le CSV `curated` + `recommendations.json` dans `streamlit_app/`,
5. executer:

```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

