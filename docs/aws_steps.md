# AWS Steps (EMR Serverless, version demo)

## 1) S3

- Bucket: `automation-risk-project` (region `eu-west-1`)
- Creer les dossiers : `raw/`, `jobs/`, `curated/`, `quarantine/`, `genai/`, `analytics/`
- Uploader le dataset brut dans `raw/`
- Uploader le script Spark:
  - `emr_jobs/automation_risk_transform_spark.py`
  - vers `s3://automation-risk-project/jobs/automation_risk_transform_spark.py`

## 2) IAM

- Role Lambda `automation-risk-transform`:
  - `emr-serverless:StartJobRun`
  - `iam:PassRole` (sur le role d'execution EMR)
  - S3 + CloudWatch logs
- Role d'execution EMR Serverless:
  - Trust policy `emr-serverless.amazonaws.com`
  - `AmazonS3FullAccess` (demo)
  - `CloudWatchLogsFullAccess` (demo)

## 3) EMR Serverless application

- Aller sur EMR Serverless et creer une application Spark
- Exemple nom: `automation-risk-emr-serverless`
- Recuperer `Application ID` (ex: `00g5...`)

## 4) Lambda Transform (orchestrateur)

- Fonction: `automation-risk-transform`
- Coller `lambda_transform/automation-risk-transform.py`
- Variables d'environnement:
  - `BUCKET_NAME=automation-risk-project`
  - `EMR_SERVERLESS_APP_ID=<application-id>`
  - `EMR_EXECUTION_ROLE_ARN=<execution-role-arn>`
- Lancer un test `{}`:
  - verifier un `jobRunId` en retour
  - verifier les outputs dans `curated/` et `quarantine/`

## 5) Lambda GenAI (mode simple sans Athena)

- Creer la fonction `automation-risk-genai`
- Coller `lambda_genai/automation-risk-genai.py`
- Variables d'environnement:
  - `BUCKET_NAME=automation-risk-project`
  - `INPUT_KEY=curated/automation_risk_enriched/`
  - `GENAI_OUTPUT_KEY=genai/recommendations.json`
  - `BEDROCK_MODEL_ID=<model-id ou inference-profile-id>`
- Lancer un test `{}` et verifier `genai/recommendations.json`

## 6) Streamlit local

- Telecharger depuis S3:
  - un fichier CSV sous `curated/automation_risk_enriched/`
  - `genai/recommendations.json`
- Mettre ces 2 fichiers dans `streamlit_app/`
- Lancer :

```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

## 7) Monitoring simple (low-cost)

- Logs CloudWatch pour Lambda et EMR Serverless
- Seuil qualite recommande:
  - warning si `quarantine ratio > 10%`
  - critique si `quarantine ratio > 20%`
- Le champ `ai_tool_availability` manquant est rempli avec `Unknown` (pas de rejet)

## 8) Athena (optionnel)

Athena est utile pour la partie SQL/analytics, mais pas obligatoire dans le flux GenAI.
Si besoin : utiliser `athena/create_table.sql` + `athena/queries.sql`.

## Points de blocage frequents

- **AccessDenied Athena** : role IAM Lambda incomplet.
- **AccessDenied EMR Serverless** : verifier `iam:PassRole` et role d'execution.
- **Model Bedrock invalide** : mauvais model ID, modele legacy, ou region incompatible.
- **Inference profile requis** : certains modeles n'acceptent pas on-demand direct.
- **CSV/Athena mismatch** : ordre des colonnes table != ordre des colonnes CSV.
- **Only one SQL statement is allowed** : executer une requete a la fois dans Athena.
- **Fichiers manquants en local** : Streamlit ne trouve pas `automation_risk_enriched.csv` ou `recommendations.json`.
