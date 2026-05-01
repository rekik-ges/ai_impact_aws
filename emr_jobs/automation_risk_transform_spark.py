import sys

from pyspark.sql import SparkSession  # type: ignore[import-not-found]
from pyspark.sql.functions import (  # type: ignore[import-not-found]
    col,
    lower,
    lit,
    round as sround,
    trim,
    when,
)

if len(sys.argv) != 4:
    raise ValueError("Usage: script.py <input_path> <curated_prefix> <quarantine_prefix>")

input_path = sys.argv[1]
curated_prefix = sys.argv[2]
quarantine_prefix = sys.argv[3]

spark = SparkSession.builder.appName("automation-risk-transform").getOrCreate()

df = spark.read.option("header", True).csv(input_path)

# Normalisation texte + imputation simple
df = (
    df.withColumn("job_role", trim(col("job_role")))
    .withColumn("industry", trim(col("industry")))
    .withColumn("education_level", trim(col("education_level")))
    .withColumn(
        "ai_tool_availability",
        when(
            col("ai_tool_availability").isNull()
            | (trim(col("ai_tool_availability")) == ""),
            lit("Unknown"),
        ).otherwise(trim(col("ai_tool_availability"))),
    )
)

# Mapping domain depuis job_role (industry reste conserve)
df = df.withColumn(
    "domain",
    when(
        lower(col("job_role")).isin(
            "accountant", "business analyst", "consultant", "product manager"
        ),
        lit("Finance & Business"),
    )
    .when(
        lower(col("job_role")).isin("data analyst", "software engineer", "ux designer"),
        lit("Data & Tech"),
    )
    .when(lower(col("job_role")).isin("doctor", "nurse"), lit("Healthcare"))
    .when(
        lower(col("job_role")).isin(
            "civil engineer", "electrician", "mechanic", "plumber"
        ),
        lit("Engineering & Maintenance"),
    )
    .when(lower(col("job_role")).isin("lawyer"), lit("Legal & Compliance"))
    .when(
        lower(col("job_role")).isin("marketing specialist", "graphic designer"),
        lit("Marketing & Creative"),
    )
    .when(
        lower(col("job_role")).isin("hr specialist", "customer support"),
        lit("HR & Support"),
    )
    .when(lower(col("job_role")).isin("teacher"), lit("Education"))
    .when(lower(col("job_role")).isin("sales manager"), lit("Sales"))
    .otherwise(lit("Other")),
)

typed = (
    df.withColumn("automation_risk_score", col("automation_risk_score").cast("double"))
    .withColumn("task_repetition_level", col("task_repetition_level").cast("double"))
    .withColumn("creativity_requirement", col("creativity_requirement").cast("double"))
    .withColumn("physical_labor_level", col("physical_labor_level").cast("double"))
    .withColumn("analytical_complexity", col("analytical_complexity").cast("double"))
    .withColumn("social_interaction_level", col("social_interaction_level").cast("double"))
    .withColumn("avg_salary_usd", col("avg_salary_usd").cast("double"))
    .withColumn("experience_required_years", col("experience_required_years").cast("double"))
    .withColumn("job_demand_index", col("job_demand_index").cast("double"))
    .withColumn("job_growth_rate", col("job_growth_rate").cast("double"))
    .withColumn("skill_complexity_score", col("skill_complexity_score").cast("double"))
    .withColumn("training_hours_needed", col("training_hours_needed").cast("double"))
    .withColumn("ai_dependency_current", col("ai_dependency_current").cast("double"))
    .withColumn("ai_dependency_future", col("ai_dependency_future").cast("double"))
)

# Regles de qualite simples et adaptees au dataset actuel
is_valid = (
    col("job_role").isNotNull()
    & (col("job_role") != "")
    & col("industry").isNotNull()
    & (col("industry") != "")
    & col("education_level").isNotNull()
    & (col("education_level") != "")
    & col("automation_risk_score").between(0, 1)
    & col("task_repetition_level").between(0, 1)
    & col("creativity_requirement").between(0, 1)
    & col("physical_labor_level").between(0, 1)
    & col("analytical_complexity").between(0, 1)
    & col("social_interaction_level").between(0, 1)
    & col("avg_salary_usd").between(30000, 180000)
    & col("experience_required_years").between(0, 14)
)

good = typed.filter(is_valid)
bad = typed.filter(~is_valid)

curated = (
    good.withColumn("automation_risk_pct", sround(col("automation_risk_score") * 100.0, 2))
    .withColumn(
        "risk_level",
        when(col("automation_risk_score") * 100.0 <= 30, lit("Low"))
        .when(col("automation_risk_score") * 100.0 <= 70, lit("Medium"))
        .otherwise(lit("High")),
    )
    .withColumn("task_repetition_pct", sround(col("task_repetition_level") * 100.0, 2))
    .withColumn(
        "creativity_requirement_pct", sround(col("creativity_requirement") * 100.0, 2)
    )
    .withColumn("physical_labor_pct", sround(col("physical_labor_level") * 100.0, 2))
    .withColumn(
        "analytical_complexity_pct", sround(col("analytical_complexity") * 100.0, 2)
    )
    .withColumn(
        "social_interaction_pct", sround(col("social_interaction_level") * 100.0, 2)
    )
    .withColumn(
        "automation_exposure_pct",
        sround(
            (
                (col("task_repetition_level") * 100.0)
                + (col("physical_labor_level") * 100.0)
                + (col("analytical_complexity") * 100.0)
            )
            / 3.0,
            2,
        ),
    )
    .withColumn("avg_salary_usd", col("avg_salary_usd").cast("int"))
    .withColumn("experience_required_years", col("experience_required_years").cast("int"))
    .withColumn("training_hours_needed", col("training_hours_needed").cast("int"))
)

curated.write.mode("overwrite").option("header", True).csv(curated_prefix)
bad.write.mode("overwrite").option("header", True).csv(quarantine_prefix)

rows_input = typed.count()
rows_curated = curated.count()
rows_quarantine = bad.count()
unknown_count = curated.filter(col("ai_tool_availability") == "Unknown").count()

print(f"rows_input={rows_input}")
print(f"rows_curated={rows_curated}")
print(f"rows_quarantine={rows_quarantine}")
print(f"unknown_ai_tool={unknown_count}")

spark.stop()
