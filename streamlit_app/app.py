import json
import re
from pathlib import Path

import streamlit as st  # type: ignore[import-not-found]
import pandas as pd  # type: ignore[import-untyped]
import plotly.express as px  # type: ignore[import-not-found]

st.set_page_config(page_title="AI Job Impact Explorer", layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: #05070d;
    color: #f8fafc;
}
.title {
    font-size: 45px;
    font-weight: 900;
    color: #ef4444;
}
.section {
    color: #60a5fa;
    font-size: 24px;
    font-weight: 800;
    margin-top: 32px;
}
.card {
    background: #0f172a;
    padding: 18px;
    border-radius: 12px;
    margin-top: 20px;
    font-size: 18px;
    border: 1px solid #1e3a8a;
}
.sidebar-text {
    color: #9ca3af;
    font-size: 14px;
    line-height: 1.5;
}
.reco-wrapper {
    background: #0f172a;
    border: 1px solid #1e3a8a;
    border-radius: 18px;
    padding: 22px;
    margin-top: 18px;
    margin-bottom: 30px;
}
.reco-intro {
    color: #cbd5e1;
    font-size: 14px;
    line-height: 1.5;
    margin-bottom: 18px;
}
.reco-card {
    background: #111827;
    border-left: 4px solid #3b82f6;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 14px;
}
.reco-title {
    color: #93c5fd;
    font-size: 16px;
    font-weight: 800;
    margin-bottom: 14px;
}
.reco-item {
    background: #0b1220;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 10px;
    color: #e5e7eb;
    font-size: 14px;
    line-height: 1.5;
}
.reco-job {
    color: #ffffff;
    font-weight: 800;
    margin-right: 6px;
}
.reco-advice {
    color: #d1d5db;
}
</style>
""", unsafe_allow_html=True)

df = pd.read_csv("automation_risk_enriched.csv")
if "domain" not in df.columns:
    # Compatibilite avec les anciennes sorties sans colonne domain.
    df["domain"] = df["industry"]

st.markdown('<div class="title">AI Job Impact Explorer</div>', unsafe_allow_html=True)

st.sidebar.markdown("""
<div class="sidebar-text">
Aujourd’hui, l’intelligence artificielle transforme profondément le monde du travail.
Quels domaines seront les plus impactés ? Quels métiers devront évoluer ?
<br><br>
Les analyses globales ne sont pas filtrées. Les sections ciblées permettent ensuite d’explorer un domaine ou un métier précis.
</div>
""", unsafe_allow_html=True)

avg_risk = df["automation_risk_pct"].mean()

st.markdown(f"""
<div class="card">
<b>Risque moyen d’automatisation :</b> {avg_risk:.1f}%
</div>
""", unsafe_allow_html=True)

# ======================
# DOMAINES — NON FILTRABLE
# ======================
st.markdown('<div class="section">Quels domaines sont les plus impactés ?</div>', unsafe_allow_html=True)

domain_df = (
    df.groupby("domain")["automation_risk_pct"]
    .mean()
    .sort_values()
    .reset_index()
)

fig = px.bar(
    domain_df,
    x="automation_risk_pct",
    y="domain",
    orientation="h",
    text=domain_df["automation_risk_pct"].round(1).astype(str) + "%",
    color_discrete_sequence=["#3b82f6"]
)

fig.update_traces(textposition="outside", hoverinfo="skip")
fig.update_layout(
    plot_bgcolor="#05070d",
    paper_bgcolor="#05070d",
    font_color="white",
    xaxis=dict(range=[0, 105], gridcolor="rgba(148,163,184,0.15)"),
    yaxis=dict(title=""),
    margin=dict(l=20, r=70, t=20, b=20)
)

st.plotly_chart(fig, width="stretch")

# ======================
# TOP METIERS — NON FILTRABLE
# ======================
st.markdown('<div class="section">Quels métiers sont les plus à risque ?</div>', unsafe_allow_html=True)

top_jobs = (
    df.groupby("job_role")["automation_risk_pct"]
    .mean()
    .sort_values()
    .tail(10)
    .reset_index()
)

fig2 = px.bar(
    top_jobs,
    x="automation_risk_pct",
    y="job_role",
    orientation="h",
    text=top_jobs["automation_risk_pct"].round(1).astype(str) + "%",
    color_discrete_sequence=["#60a5fa"]
)

fig2.update_traces(textposition="outside", hoverinfo="skip")
fig2.update_layout(
    plot_bgcolor="#05070d",
    paper_bgcolor="#05070d",
    font_color="white",
    xaxis=dict(range=[0, 105], gridcolor="rgba(148,163,184,0.15)"),
    yaxis=dict(title=""),
    margin=dict(l=20, r=70, t=20, b=20)
)

st.plotly_chart(fig2, width="stretch")

# ======================
# FACTEURS PAR MÉTIER — FILTRE LOCAL
# ======================
st.markdown('<div class="section">Pourquoi ce métier est-il à risque ?</div>', unsafe_allow_html=True)

selected_job = st.selectbox(
    "Choisir un métier",
    sorted(df["job_role"].dropna().unique())
)

job_df = df[df["job_role"] == selected_job]

factors = pd.DataFrame({
    "Facteur": [
        "Répétitivité",
        "Créativité",
        "Travail physique",
        "Complexité analytique",
        "Interaction sociale"
    ],
    "Valeur": [
        job_df["task_repetition_pct"].mean(),
        job_df["creativity_requirement_pct"].mean(),
        job_df["physical_labor_pct"].mean(),
        job_df["analytical_complexity_pct"].mean(),
        job_df["social_interaction_pct"].mean()
    ]
})

fig4 = px.bar(
    factors,
    x="Valeur",
    y="Facteur",
    orientation="h",
    text=factors["Valeur"].round(1).astype(str) + "%",
    color_discrete_sequence=["#60a5fa"]
)

fig4.update_traces(textposition="outside", hoverinfo="skip")
fig4.update_layout(
    plot_bgcolor="#05070d",
    paper_bgcolor="#05070d",
    font_color="white",
    xaxis=dict(range=[0, 105], gridcolor="rgba(148,163,184,0.15)"),
    yaxis=dict(title=""),
    margin=dict(l=20, r=70, t=20, b=20)
)

st.plotly_chart(fig4, width="stretch")

# ======================
# INDICATEURS ENRICHIS — DÉCISIONS STRATÉGIQUES
# ======================
enriched_cols = {
    "avg_salary_usd",
    "experience_required_years",
    "job_demand_index",
    "job_growth_rate",
    "skill_complexity_score",
    "training_hours_needed",
    "ai_dependency_current",
    "ai_dependency_future"
}

if enriched_cols.issubset(df.columns):
    st.markdown('<div class="section">Quels métiers combinent risque élevé et forte valeur économique ?</div>', unsafe_allow_html=True)

    strategic_jobs = (
        df.groupby("job_role", as_index=False)[
            ["automation_risk_pct", "avg_salary_usd", "job_demand_index"]
        ]
        .mean()
        .sort_values("automation_risk_pct", ascending=False)
        .head(20)
    )

    fig5 = px.scatter(
        strategic_jobs,
        x="automation_risk_pct",
        y="avg_salary_usd",
        size="job_demand_index",
        color="job_demand_index",
        hover_name="job_role",
        color_continuous_scale="Blues",
        labels={
            "automation_risk_pct": "Risque d'automatisation (%)",
            "avg_salary_usd": "Salaire moyen (USD)",
            "job_demand_index": "Demande marché"
        }
    )
    fig5.update_layout(
        plot_bgcolor="#05070d",
        paper_bgcolor="#05070d",
        font_color="white",
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig5, width="stretch")

    st.markdown('<div class="section">Quels métiers demandent le plus d’investissement en montée en compétences ?</div>', unsafe_allow_html=True)

    upskilling_jobs = (
        df.groupby("job_role", as_index=False)[
            ["training_hours_needed", "ai_dependency_future"]
        ]
        .mean()
        .sort_values("training_hours_needed", ascending=False)
        .head(12)
    )

    fig6 = px.bar(
        upskilling_jobs.sort_values("training_hours_needed"),
        x="training_hours_needed",
        y="job_role",
        orientation="h",
        color="ai_dependency_future",
        color_continuous_scale="Blues",
        text=upskilling_jobs.sort_values("training_hours_needed")["training_hours_needed"].round(0).astype(int).astype(str) + " h",
        labels={
            "training_hours_needed": "Heures de formation nécessaires",
            "ai_dependency_future": "Dépendance IA future"
        }
    )
    fig6.update_traces(textposition="outside")
    fig6.update_layout(
        plot_bgcolor="#05070d",
        paper_bgcolor="#05070d",
        font_color="white",
        margin=dict(l=20, r=40, t=20, b=20)
    )
    st.plotly_chart(fig6, width="stretch")

    st.markdown('<div class="section">Top 10 métiers impactés : niveau d’étude / risque</div>', unsafe_allow_html=True)
    top5_edu_risk = (
        df.groupby("job_role", as_index=False)[
            ["automation_risk_pct", "experience_required_years"]
        ]
        .mean()
        .sort_values("automation_risk_pct", ascending=False)
        .head(10)
    )
    top5_edu_risk["education_score"] = top5_edu_risk["experience_required_years"].clip(lower=0)

    fig7 = px.scatter(
        top5_edu_risk,
        x="education_score",
        y="automation_risk_pct",
        text="job_role",
        color="automation_risk_pct",
        color_continuous_scale="Blues",
        labels={
            "education_score": "Années d'étude/expérience requises",
            "automation_risk_pct": "Risque d'automatisation (%)"
        }
    )
    fig7.update_traces(textposition="top center")
    fig7.update_layout(
        plot_bgcolor="#05070d",
        paper_bgcolor="#05070d",
        font_color="white",
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig7, width="stretch")

    st.markdown('<div class="section">Top 10 métiers impactés : salaire / risque</div>', unsafe_allow_html=True)
    top5_salary_risk = (
        df.groupby("job_role", as_index=False)[
            ["automation_risk_pct", "avg_salary_usd"]
        ]
        .mean()
        .sort_values("automation_risk_pct", ascending=False)
        .head(10)
    )

    fig8 = px.scatter(
        top5_salary_risk,
        x="avg_salary_usd",
        y="automation_risk_pct",
        text="job_role",
        color="automation_risk_pct",
        color_continuous_scale="Blues",
        labels={
            "avg_salary_usd": "Salaire moyen (USD)",
            "automation_risk_pct": "Risque d'automatisation (%)"
        }
    )
    fig8.update_traces(textposition="top center")
    fig8.update_layout(
        plot_bgcolor="#05070d",
        paper_bgcolor="#05070d",
        font_color="white",
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig8, width="stretch")

# ======================
# RECOMMANDATIONS GENAI
# ======================
st.markdown('<div class="section">Recommandations stratégiques</div>', unsafe_allow_html=True)


def clean_text(text: str) -> str:
    text = text.replace("#", "")
    text = text.replace("**", "")
    text = text.replace("|", "")
    text = text.replace("---", "")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {
        "Personnes exposées": [],
        "Entreprises": [],
        "Postes à préserver": []
    }

    current = None

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        lower = line.lower()

        if lower.startswith("1.") or "personnes exposées" in lower:
            current = "Personnes exposées"
            continue

        if lower.startswith("2.") or "entreprises" in lower:
            current = "Entreprises"
            continue

        if lower.startswith("3.") or "postes à préserver" in lower or "postes a preserver" in lower:
            current = "Postes à préserver"
            continue

        if current:
            line = re.sub(r"^\d+\.\s*", "", line)
            line = re.sub(r"^-+\s*", "", line).strip()

            if ":" in line:
                sections[current].append(line)

    return sections


def render_items(items: list[str]) -> str:
    html = ""
    for item in items:
        if ":" in item:
            job, advice = item.split(":", 1)
            html += f"""
            <div class="reco-item">
                <span class="reco-job">{job.strip()}</span>
                <span class="reco-advice">{advice.strip()}</span>
            </div>
            """
    return html


recommendation_path = Path("recommendations.json")

if recommendation_path.exists():
    with open(recommendation_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    raw_text = data.get("recommendations", "")
    cleaned = clean_text(raw_text)
    sections = split_sections(cleaned)

    st.markdown("""
    <div class="reco-wrapper">
        <div class="reco-intro">
        Recommandations générées à partir des métiers les plus exposés et les moins exposés.
        Chaque ligne associe un métier, un risque principal et une action recommandée.
        </div>
    """, unsafe_allow_html=True)

    title_map = {
        "Personnes exposées": "Exposition critique des métiers : stratégies de reconversion prioritaires",
        "Entreprises": "Leviers d’investissement : automatisation ciblée et allocation des ressources",
        "Postes à préserver": "Rôles stratégiques à préserver : augmentation par l’intelligence artificielle"
    }

    for key, display_title in title_map.items():
        items = sections.get(key, [])
        if items:
            st.markdown(f"""
            <div class="reco-card">
                <div class="reco-title">{display_title}</div>
                {render_items(items)}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.warning("Le fichier recommendations.json n’est pas encore disponible. Télécharge-le depuis S3/genai et place-le à côté de app.py.")