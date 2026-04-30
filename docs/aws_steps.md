# AWS Steps (version etudiant, simple)

## 1) S3

- Creer un bucket (ex: `automation-risk-project`)
- Creer 4 dossiers : `raw/`, `analytics/`, `genai/`, `athena-results/`
- Uploader le dataset brut dans `raw/`

## 2) IAM (role Lambda)

- Creer un role pour Lambda
- Ajouter permissions de base :
  - S3 (lecture/ecriture bucket)
  - Bedrock (`InvokeModel`)
  - CloudWatch logs
- Si vous utilisez Athena en plus : ajouter permissions Athena/Glue

## 3) Lambda Transform

- Creer la fonction `automation-risk-transform`
- Coller `lambda_transform/automation-risk-transform.py`
- Variables d'environnement :
  - `BUCKET_NAME`
  - `INPUT_KEY=raw/ai_automation_risk_dataset.csv`
  - `OUTPUT_KEY=analytics/automation_risk_enriched.csv`
- Lancer un test `{}` et verifier le fichier dans `analytics/`

## 4) Lambda GenAI (mode simple sans Athena)

- Creer la fonction `automation-risk-genai`
- Coller `lambda_genai/automation-risk-genai.py`
- Variables d'environnement :
  - `BUCKET_NAME`
  - `INPUT_KEY=analytics/automation_risk_enriched.csv`
  - `GENAI_OUTPUT_KEY=genai/recommendations.json`
  - `BEDROCK_MODEL_ID=<model-id ou inference-profile-id>`
- Lancer un test `{}` et verifier `genai/recommendations.json`

## 5) Streamlit local

- Telecharger depuis S3 :
  - `analytics/automation_risk_enriched.csv`
  - `genai/recommendations.json`
- Mettre ces 2 fichiers dans `streamlit_app/`
- Lancer :

```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

## 6) Athena (optionnel)

Athena est utile pour la partie SQL/analytics, mais pas obligatoire dans le flux GenAI simple.
Si besoin : utiliser `athena/create_table.sql` + `athena/queries.sql`.

## Points de blocage frequents

- **AccessDenied Athena** : role IAM Lambda incomplet.
- **Model Bedrock invalide** : mauvais model ID, modele legacy, ou region incompatible.
- **Inference profile requis** : certains modeles n'acceptent pas on-demand direct.
- **CSV/Athena mismatch** : ordre des colonnes table != ordre des colonnes CSV.
- **Only one SQL statement is allowed** : executer une requete a la fois dans Athena.
- **Fichiers manquants en local** : Streamlit ne trouve pas `automation_risk_enriched.csv` ou `recommendations.json`.
