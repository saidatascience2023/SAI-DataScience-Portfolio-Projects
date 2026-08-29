import html
import re
from pathlib import Path

import PyPDF2
import streamlit as st


st.set_page_config(
    page_title="Resume & Portfolio Readiness Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


ROLE_PROFILES = {
    "Data Analyst": {
        "skills": {
            "Python": ["python"],
            "SQL": ["sql", "mysql", "postgresql", "sql server"],
            "Excel": ["excel", "pivot table", "power query"],
            "Tableau": ["tableau"],
            "Power BI": ["power bi", "powerbi"],
            "Pandas": ["pandas"],
            "Data visualization": ["data visualization", "data visualisation"],
            "Statistics": ["statistics", "statistical analysis"],
            "Dashboards": ["dashboard", "dashboards"],
        },
        "projects": [
            {
                "title": "Retail Sales Performance",
                "question": "Which products and regions contribute most to sales?",
                "evidence": "SQL summaries, data validation and a decision-focused dashboard",
            },
            {
                "title": "Customer Retention Analysis",
                "question": "Which customer groups show declining repeat purchases?",
                "evidence": "SQL joins, Python segmentation and practical recommendations",
            },
            {
                "title": "Operations Performance Analysis",
                "question": "Where are delays or service problems occurring most often?",
                "evidence": "Trend analysis, KPI definitions and Tableau storytelling",
            },
        ],
    },
    "Data Scientist": {
        "skills": {
            "Python": ["python"],
            "SQL": ["sql", "mysql", "postgresql"],
            "Machine learning": ["machine learning"],
            "Statistics": ["statistics", "statistical analysis"],
            "Pandas": ["pandas"],
            "NumPy": ["numpy"],
            "Scikit-learn": ["scikit-learn", "sklearn"],
            "Model evaluation": ["model evaluation", "cross-validation", "cross validation"],
            "Feature engineering": ["feature engineering"],
            "Data visualization": ["data visualization", "data visualisation"],
        },
        "projects": [
            {
                "title": "Customer Churn Risk",
                "question": "Which customers are at risk, and which factors are associated with churn?",
                "evidence": "Baseline comparison, model evaluation and actionable interpretation",
            },
            {
                "title": "Demand Forecasting",
                "question": "What demand should the business expect over the next period?",
                "evidence": "Time-based validation, error metrics and limitations",
            },
            {
                "title": "Recommendation Analysis",
                "question": "Which relevant products could be recommended to each customer group?",
                "evidence": "Method selection, offline evaluation and business safeguards",
            },
        ],
    },
    "Machine Learning Engineer": {
        "skills": {
            "Python": ["python"],
            "Machine learning": ["machine learning"],
            "Deep learning": ["deep learning"],
            "TensorFlow": ["tensorflow"],
            "PyTorch": ["pytorch"],
            "Docker": ["docker"],
            "Cloud": ["aws", "azure", "gcp", "google cloud"],
            "APIs": ["api", "fastapi", "flask"],
            "MLOps": ["mlops", "mlflow"],
            "Model deployment": ["model deployment", "deployed model", "deployment"],
        },
        "projects": [
            {
                "title": "Production-Ready Prediction API",
                "question": "How can a validated model be served reliably to another application?",
                "evidence": "FastAPI endpoint, tests, Docker and monitoring plan",
            },
            {
                "title": "Model Monitoring Workflow",
                "question": "How will the team detect data drift and performance degradation?",
                "evidence": "Logging, drift checks, alerts and retraining criteria",
            },
            {
                "title": "Reproducible ML Pipeline",
                "question": "How can training and deployment be repeated safely?",
                "evidence": "Versioning, automated pipeline and documented configuration",
            },
        ],
    },
    "Generative AI Engineer": {
        "skills": {
            "Python": ["python"],
            "LLMs": ["llm", "large language model"],
            "OpenAI API": ["openai", "openai api"],
            "Prompt engineering": ["prompt engineering", "prompt design"],
            "RAG": ["rag", "retrieval augmented generation"],
            "Vector databases": ["vector database", "pinecone", "weaviate", "chroma", "faiss"],
            "Embeddings": ["embedding", "embeddings"],
            "APIs": ["api", "fastapi", "flask"],
            "Evaluation": ["llm evaluation", "evaluation framework", "evals"],
            "Streamlit": ["streamlit"],
        },
        "projects": [
            {
                "title": "Grounded Knowledge Assistant",
                "question": "Can users receive useful answers supported by approved sources?",
                "evidence": "Retrieval design, citations, evaluation and failure handling",
            },
            {
                "title": "Customer Support Copilot",
                "question": "Which support tasks can be accelerated without removing human oversight?",
                "evidence": "Prompt workflow, escalation rules, test cases and safeguards",
            },
            {
                "title": "Document Review Assistant",
                "question": "How can users identify key information while preserving traceability?",
                "evidence": "Structured extraction, validation and privacy controls",
            },
        ],
    },
}


CUSTOM_CSS = """
<style>
    .stApp { background: #090909; color: #f7f3e8; }
    .block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem; }
    h1, h2, h3, h4 { color: #ffffff !important; }
    [data-testid="stWidgetLabel"] p,
    [data-testid="stFileUploader"] label p,
    .stSelectbox label p {
        color: #f7f3e8 !important;
        font-weight: 700 !important;
    }
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {
        color: #b8b8b8 !important;
    }
    .hero {
        padding: 1.7rem 1.9rem;
        border: 1px solid #d8aa2f;
        border-radius: 18px;
        background: linear-gradient(135deg, #171717 0%, #0c0c0c 100%);
        margin-bottom: 1.4rem;
    }
    .eyebrow { color: #d8aa2f; font-size: .82rem; font-weight: 800; letter-spacing: .08em; }
    .hero h1 { margin: .35rem 0 .45rem; font-size: 2.25rem; }
    .hero p { color: #d1d1d1; margin: 0; font-size: 1.03rem; }
    .result-card {
        background: #171717;
        border: 1px solid #3f3f3f;
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
        height: 100%;
    }
    .result-card strong { color: #d8aa2f; }
    .skill-chip {
        display: inline-block;
        margin: .22rem .28rem .22rem 0;
        padding: .38rem .65rem;
        border-radius: 999px;
        font-size: .88rem;
        font-weight: 650;
    }
    .found { background: #183a28; color: #8ee0ac; border: 1px solid #3f9b67; }
    .missing { background: #3b211d; color: #ffad9f; border: 1px solid #b45445; }
    .project-card {
        min-height: 205px;
        background: #171717;
        border: 1px solid #d8aa2f;
        border-radius: 15px;
        padding: 1rem;
    }
    .project-card h4 { color: #d8aa2f; margin: 0 0 .55rem; }
    .project-card p { color: #e6e6e6; font-size: .92rem; }
    .label { color: #8ee0ac; font-size: .78rem; font-weight: 800; letter-spacing: .05em; }
    .disclaimer {
        color: #b8b8b8; background: #131313; border-left: 3px solid #d8aa2f;
        padding: .8rem 1rem; border-radius: 6px;
    }
    div[data-testid="stMetric"] {
        background: #171717; border: 1px solid #d8aa2f; border-radius: 15px; padding: .9rem;
    }
    div[data-testid="stFileUploader"], div[data-baseweb="select"] > div {
        background: #171717;
    }
    [data-testid="stFileUploaderDropzone"] {
        background: #f7f3e8 !important;
        border: 1px solid #d8aa2f !important;
    }
    [data-testid="stFileUploaderDropzone"] div,
    [data-testid="stFileUploaderDropzone"] span,
    [data-testid="stFileUploaderDropzone"] small {
        color: #343434 !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        background: #d8aa2f !important;
        color: #111111 !important;
        border: 0 !important;
        font-weight: 750 !important;
    }
    [data-baseweb="select"] > div,
    [data-baseweb="select"] input {
        color: #1f1f1f !important;
    }
    [data-testid="stAlert"] {
        background: #171717 !important;
        border: 1px solid #d8aa2f !important;
    }
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] div {
        color: #f7f3e8 !important;
    }
    .stButton > button,
    .stLinkButton > a {
        background: #d8aa2f !important;
        color: #111111 !important;
        border: 1px solid #d8aa2f !important;
        font-weight: 750 !important;
    }
</style>
"""


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def extract_text_from_pdf(uploaded_file) -> str:
    uploaded_file.seek(0)
    reader = PyPDF2.PdfReader(uploaded_file)
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as exc:
            raise ValueError("The PDF is password protected and cannot be read.") from exc

    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text_parts.append(page_text)

    text = normalize_text(" ".join(text_parts))
    if not text:
        raise ValueError(
            "No readable text was found. The PDF may be scanned as an image. "
            "Please upload a text-based PDF or TXT file."
        )
    return text


def extract_text(uploaded_file) -> str:
    extension = Path(uploaded_file.name).suffix.lower()
    if extension == ".pdf":
        return extract_text_from_pdf(uploaded_file)
    if extension == ".txt":
        uploaded_file.seek(0)
        return normalize_text(uploaded_file.read().decode("utf-8", errors="replace"))
    raise ValueError("Please upload a PDF or TXT file.")


def phrase_exists(text: str, phrase: str) -> bool:
    pattern = rf"(?<!\w){re.escape(phrase.lower())}(?!\w)"
    return re.search(pattern, text) is not None


def evaluate_skills(resume_text: str, skill_map: dict) -> tuple[list[str], list[str]]:
    found, missing = [], []
    for skill, aliases in skill_map.items():
        if any(phrase_exists(resume_text, alias) for alias in aliases):
            found.append(skill)
        else:
            missing.append(skill)
    return found, missing


def evidence_score(resume_text: str) -> tuple[int, list[str]]:
    evidence_checks = {
        "Projects are mentioned": ["project", "portfolio", "case study"],
        "Results are quantified": [r"\b\d+(?:\.\d+)?%", r"\$\s?\d+", r"\b\d+[kKmM]\b"],
        "Business impact language is used": ["improved", "reduced", "increased", "saved", "recommended"],
        "Work is documented or linked": ["github", "portfolio", "tableau public", "streamlit"],
    }
    passed = []
    for label, patterns in evidence_checks.items():
        if any(re.search(pattern, resume_text, re.IGNORECASE) for pattern in patterns):
            passed.append(label)
    return round(len(passed) / len(evidence_checks) * 100), passed


def readiness_label(score: int) -> tuple[str, str]:
    if score >= 75:
        return "Strong foundation", "Your résumé shows many relevant skills. Strengthen the evidence behind them."
    if score >= 50:
        return "Developing foundation", "You have a useful starting point. Focus your next project on the most important gaps."
    return "Early foundation", "Start with one manageable project that demonstrates core role requirements."


def chips(items: list[str], css_class: str) -> str:
    if not items:
        return '<span class="skill-chip found">None</span>'
    return "".join(
        f'<span class="skill-chip {css_class}">{html.escape(item)}</span>' for item in items
    )


st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">SAI DATASCIENCE • PORTFOLIO READINESS</div>
        <h1>Resume & Portfolio Readiness Analyzer</h1>
        <p>Compare the skills shown on your résumé with a target role, then identify stronger portfolio evidence to build next.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

input_col, role_col = st.columns([1.25, 1], gap="large")
with input_col:
    uploaded_file = st.file_uploader(
        "Upload your résumé",
        type=["pdf", "txt"],
        help="Use a text-based PDF or TXT file. Your file is processed only during this session.",
    )
with role_col:
    selected_role = st.selectbox("Choose your target role", list(ROLE_PROFILES))
    st.caption("This assessment is educational and does not predict hiring or ATS decisions.")


if uploaded_file is None:
    st.info("Upload a résumé to generate your readiness summary and project direction.")
    st.stop()


try:
    resume_text = extract_text(uploaded_file)
except Exception as exc:
    st.error(str(exc))
    st.stop()


profile = ROLE_PROFILES[selected_role]
found_skills, missing_skills = evaluate_skills(resume_text, profile["skills"])
skill_score = round(len(found_skills) / len(profile["skills"]) * 100)
portfolio_score, evidence_found = evidence_score(resume_text)
overall_score = round(skill_score * 0.65 + portfolio_score * 0.35)
label, guidance = readiness_label(overall_score)

st.divider()
st.subheader(f"Readiness summary for {selected_role}")

metric1, metric2, metric3 = st.columns(3)
metric1.metric("Overall readiness", f"{overall_score}%")
metric2.metric("Role-skill coverage", f"{skill_score}%")
metric3.metric("Portfolio evidence", f"{portfolio_score}%")

st.progress(overall_score / 100)
st.markdown(
    f'<div class="disclaimer"><strong>{html.escape(label)}:</strong> {html.escape(guidance)}</div>',
    unsafe_allow_html=True,
)

found_col, missing_col = st.columns(2, gap="large")
with found_col:
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.subheader("Skills found")
    st.markdown(chips(found_skills, "found"), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
with missing_col:
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.subheader("Skills not clearly shown")
    st.markdown(chips(missing_skills, "missing"), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.caption(
    "A missing term does not prove that you lack the skill. It means the skill was not clearly detected in the uploaded résumé."
)

st.divider()
st.subheader("Portfolio project directions")
st.write("Choose one project you can complete well. Start with the business question, then select the data and tools.")

project_columns = st.columns(3, gap="medium")
for column, project in zip(project_columns, profile["projects"]):
    with column:
        st.markdown(
            f"""
            <div class="project-card">
                <h4>{html.escape(project['title'])}</h4>
                <div class="label">BUSINESS QUESTION</div>
                <p>{html.escape(project['question'])}</p>
                <div class="label">PORTFOLIO EVIDENCE</div>
                <p>{html.escape(project['evidence'])}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()
interview_col, action_col = st.columns([1.1, 1], gap="large")
with interview_col:
    st.subheader("Interview questions to prepare")
    questions = [
        "Why did you choose this business problem?",
        "Who was the stakeholder and what decision did they need to make?",
        "How did you evaluate and prepare the data?",
        "Why did you choose these methods and tools?",
        "What was the most important insight?",
        "What were the limitations and next steps?",
    ]
    for question in questions:
        st.markdown(f"- {question}")

with action_col:
    st.subheader("Your recommended next step")
    priority_skills = missing_skills[:3]
    if priority_skills:
        st.write("Build evidence for these priority areas:")
        for skill in priority_skills:
            st.markdown(f"- **{skill}**")
    else:
        st.write("Your core skills are visible. Focus on stronger project outcomes and documentation.")

    if evidence_found:
        with st.expander("Portfolio evidence detected"):
            for item in evidence_found:
                st.markdown(f"- {item}")

    st.link_button(
        "Explore the AI Career Accelerator",
        "https://saidatascience.com/ai-career-accelerator/",
        use_container_width=True,
    )

st.divider()
st.markdown(
    """
    <div class="disclaimer">
        <strong>Important:</strong> This tool uses transparent keyword and evidence checks. It is not an ATS, does not use a hiring model, and does not guarantee interviews or employment. Review the recommendations using your target job descriptions and professional judgment.
    </div>
    """,
    unsafe_allow_html=True,
)
