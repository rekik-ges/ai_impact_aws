import json
import os
import csv
import io
from typing import Any

import boto3  # type: ignore[import-not-found]

s3 = boto3.client("s3")
bedrock = boto3.client("bedrock-runtime")


def build_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = []
    for row in rows:
        lines.append(" ; ".join(f"{col}: {row.get(col, '')}" for col in columns))
    return "\n".join(lines)


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    bucket = os.environ["BUCKET_NAME"]
    input_key = os.environ["INPUT_KEY"]
    output_key = os.environ["GENAI_OUTPUT_KEY"]
    model_id = os.environ["BEDROCK_MODEL_ID"]

    response = s3.get_object(Bucket=bucket, Key=input_key)
    content = response["Body"].read().decode("utf-8")

    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)

    numeric_cols = [
        "automation_risk_pct",
        "automation_exposure_pct",
        "task_repetition_pct",
        "creativity_requirement_pct",
        "physical_labor_pct",
        "analytical_complexity_pct",
        "social_interaction_pct"
    ]

    for row in rows:
        for col in numeric_cols:
            row[col] = float(row[col])

    top_risk_jobs = sorted(
        rows,
        key=lambda x: x["automation_risk_pct"],
        reverse=True
    )[:6]

    low_risk_jobs = sorted(
        rows,
        key=lambda x: x["automation_risk_pct"]
    )[:6]

    prompt = f"""
Tu es un Data Analyst senior.

Ta réponse doit être adaptée à un dashboard Streamlit.
Elle doit être courte, lisible et directement exploitable.

FORMAT OBLIGATOIRE :
1. Personnes exposées
- Métier : raison du risque + reconversion conseillée.

2. Entreprises
- Métier : tâche à automatiser + raison + rôle humain à conserver.

3. Postes à préserver
- Métier : raison de préservation + usage de l’IA en support.

RÈGLES STRICTES :
- Une seule ligne par métier.
- Un seul métier par ligne.
- Ne jamais regrouper plusieurs métiers.
- Ne jamais écrire de paragraphe.
- Ne jamais écrire de phrase d’introduction.
- Ne jamais écrire de synthèse globale.
- Ne jamais mentionner le secteur.
- Maximum 5 lignes par section.
- Chaque ligne doit faire maximum 25 mots.
- Pas de tableau.
- Pas de markdown complexe.
- Pas de caractères #, **, | ou ---.
- N’invente aucun métier.
- Utilise uniquement les métiers fournis.

Données métiers à risque :
{build_table(top_risk_jobs, ["job_role", "automation_risk_pct", "task_repetition_pct", "creativity_requirement_pct"])}

Données métiers peu exposés :
{build_table(low_risk_jobs, ["job_role", "automation_risk_pct", "creativity_requirement_pct", "analytical_complexity_pct", "social_interaction_pct"])}
"""

    bedrock_response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 900,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
    )

    result = json.loads(bedrock_response["body"].read())
    generated_text = result["content"][0]["text"]

    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=json.dumps(
            {"recommendations": generated_text},
            ensure_ascii=False,
            indent=2
        ),
        ContentType="application/json"
    )

    return {
        "statusCode": 200,
        "message": "Recommandations GenAI générées",
        "output": f"s3://{bucket}/{output_key}"
    }