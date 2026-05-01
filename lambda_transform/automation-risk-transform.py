import os

import boto3  # type: ignore[import-not-found]

emr_serverless = boto3.client("emr-serverless", region_name="eu-west-1")

def lambda_handler(event, context):
    try:
        # Variables d'environnement
        bucket = os.environ["BUCKET_NAME"]
        app_id = os.environ["EMR_SERVERLESS_APP_ID"]
        execution_role_arn = os.environ["EMR_EXECUTION_ROLE_ARN"]

        input_path = f"s3://{bucket}/raw/ai_automation_risk_dataset.csv"
        curated_prefix = f"s3://{bucket}/curated/automation_risk_enriched/"
        quarantine_prefix = f"s3://{bucket}/quarantine/automation_risk_rejected/"
        entrypoint = f"s3://{bucket}/jobs/automation_risk_transform_spark.py"

        response = emr_serverless.start_job_run(
            applicationId=app_id,
            executionRoleArn=execution_role_arn,
            jobDriver={
                "sparkSubmit": {
                    "entryPoint": entrypoint,
                    "entryPointArguments": [
                        input_path,
                        curated_prefix,
                        quarantine_prefix
                    ],
                    "sparkSubmitParameters": "--conf spark.executor.memory=2g --conf spark.driver.memory=2g"
                }
            },
            configurationOverrides={
                "monitoringConfiguration": {
                    "cloudWatchLoggingConfiguration": {
                        "enabled": True,
                        "logGroupName": "/emr-serverless/automation-risk",
                        "logStreamNamePrefix": "spark-job"
                    }
                }
            }
        )

        return {
            "statusCode": 200,
            "message": "EMR Serverless job submitted",
            "applicationId": app_id,
            "jobRunId": response["jobRunId"]
        }

    except Exception as e:
        print("Erreur globale :", e)
        return {
            "statusCode": 500,
            "error": str(e)
        }