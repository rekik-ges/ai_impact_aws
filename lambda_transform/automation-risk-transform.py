import json
import boto3  # type: ignore[import-not-found]
import csv
import io
import os

s3 = boto3.client("s3")

def lambda_handler(event, context):
    
    try:
        # récupérer variables d’environnement 
        bucket = os.environ["BUCKET_NAME"]
        input_key = os.environ["INPUT_KEY"]
        output_key = os.environ["OUTPUT_KEY"]

        print(f"Lecture du fichier : s3://{bucket}/{input_key}")

        # lire le fichier depuis S3
        response = s3.get_object(Bucket=bucket, Key=input_key)
        content = response["Body"].read().decode("utf-8")

        reader = csv.DictReader(io.StringIO(content))

        output = io.StringIO()

        fieldnames = [
            "job_role",
            "industry",
            "automation_risk_pct",
            "risk_level",
            "automation_exposure_pct",
            "task_repetition_pct",
            "creativity_requirement_pct",
            "physical_labor_pct",
            "analytical_complexity_pct",
            "social_interaction_pct",
            "avg_salary_usd",
            "experience_required_years",
            "education_level",
            "job_demand_index",
            "job_growth_rate",
            "skill_complexity_score",
            "training_hours_needed",
            "ai_dependency_current",
            "ai_dependency_future",
            "ai_tool_availability"
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            try:
                # conversion en %
                automation_risk_pct = float(row["automation_risk_score"]) * 100
                task_rep = float(row["task_repetition_level"])

                creativity = float(row["creativity_requirement"]) * 100
                physical = float(row["physical_labor_level"]) * 100
                analytical = float(row["analytical_complexity"]) * 100
                social = float(row["social_interaction_level"]) * 100

                # risk level
                if automation_risk_pct <= 30:
                    risk_level = "Low"
                elif automation_risk_pct <= 70:
                    risk_level = "Medium"
                else:
                    risk_level = "High"

                # score exposition (aligné avec la documentation projet)
                exposure = ((task_rep * 100) + physical + analytical) / 3

                writer.writerow({
                    "job_role": row["job_role"],
                    "industry": row["industry"],
                    "automation_risk_pct": round(automation_risk_pct, 2),
                    "risk_level": risk_level,
                    "automation_exposure_pct": round(exposure, 2),
                    "task_repetition_pct": round(task_rep * 100, 2),
                    "creativity_requirement_pct": round(creativity, 2),
                    "physical_labor_pct": round(physical, 2),
                    "analytical_complexity_pct": round(analytical, 2),
                    "social_interaction_pct": round(social, 2),
                    "avg_salary_usd": int(float(row["avg_salary_usd"])),
                    "experience_required_years": int(float(row["experience_required_years"])),
                    "education_level": row["education_level"],
                    "job_demand_index": round(float(row["job_demand_index"]), 4),
                    "job_growth_rate": round(float(row["job_growth_rate"]), 4),
                    "skill_complexity_score": round(float(row["skill_complexity_score"]), 4),
                    "training_hours_needed": int(float(row["training_hours_needed"])),
                    "ai_dependency_current": round(float(row["ai_dependency_current"]), 4),
                    "ai_dependency_future": round(float(row["ai_dependency_future"]), 4),
                    "ai_tool_availability": row["ai_tool_availability"]
                })

            except Exception as e:
                print("Erreur sur une ligne :", e)
                continue

        print(f"Écriture du fichier : s3://{bucket}/{output_key}")

        # sauvegarde dans S3
        s3.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=output.getvalue()
        )

        return {
            "statusCode": 200,
            "message": "Transformation terminée"
        }

    except Exception as e:
        print("Erreur globale :", e)
        return {
            "statusCode": 500,
            "error": str(e)
        }