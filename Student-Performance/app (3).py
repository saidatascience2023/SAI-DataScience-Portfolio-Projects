import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier


st.set_page_config(
    page_title="AI Placement Support Lab",
    page_icon="🎓",
    layout="wide",
)

GOLD = "#D9B12E"
LIGHT_GOLD = "#F5D96B"

st.markdown(
    f"""
    <style>
    .stApp {{ background: #070707; color: #f5f5f5; }}
    [data-testid="stSidebar"] {{ background: #111111; border-right: 1px solid #3b3215; }}
    .hero {{
        padding: 2rem 2.2rem; border: 1px solid {GOLD}; border-radius: 18px;
        background: linear-gradient(135deg, #17140b 0%, #090909 65%);
        margin-bottom: 1.2rem;
    }}
    .eyebrow {{ color: {GOLD}; font-size: .82rem; font-weight: 800; letter-spacing: .16em; }}
    .hero h1 {{ margin: .35rem 0 .45rem; font-size: 2.6rem; color: white; }}
    .hero p {{ color: #c9c9c9; font-size: 1.08rem; margin: 0; }}
    .result-good, .result-support {{ padding: 1.25rem; border-radius: 14px; margin: .5rem 0 1rem; }}
    .result-good {{ background: #10251a; border: 1px solid #43a66d; }}
    .result-support {{ background: #261e09; border: 1px solid {GOLD}; }}
    .mini-card {{ background: #171717; border: 1px solid #353535; padding: 1rem; border-radius: 12px; }}
    div[data-testid="stMetric"] {{ background: #151515; border: 1px solid #383018; padding: 1rem; border-radius: 12px; }}
    div.stButton > button {{ background: {GOLD}; color: #080808; border: 0; font-weight: 800; }}
    div.stButton > button:hover {{ background: {LIGHT_GOLD}; color: #080808; }}
    .responsible {{ border-left: 5px solid {GOLD}; background: #17140c; padding: 1rem 1.2rem; border-radius: 8px; }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def make_dataset(n=100, seed=42):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "student_id": [f"STU-{i:03d}" for i in range(1, n + 1)],
        "technical_score": np.clip(rng.normal(68, 14, n).round(), 30, 98).astype(int),
        "aptitude_score": np.clip(rng.normal(66, 15, n).round(), 25, 98).astype(int),
        "projects_completed": rng.choice([0, 1, 2, 3, 4, 5], n, p=[.08, .18, .29, .25, .14, .06]),
        "mock_interview_score": np.clip(rng.normal(64, 16, n).round(), 20, 98).astype(int),
        "attendance_percent": np.clip(rng.normal(80, 10, n).round(), 50, 100).astype(int),
    })
    risk = (
        (df.technical_score < 62).astype(int) * 2
        + (df.aptitude_score < 60).astype(int) * 2
        + (df.projects_completed < 2).astype(int) * 2
        + (df.mock_interview_score < 60).astype(int) * 2
        + (df.attendance_percent < 72).astype(int)
        + rng.binomial(1, .18, n)
    )
    df["needs_extra_preparation"] = np.where(risk >= 4, "Yes", "No")
    return df


@st.cache_resource
def train_model(df):
    features = [
        "technical_score", "aptitude_score", "projects_completed",
        "mock_interview_score", "attendance_percent",
    ]
    X = df[features]
    y = (df.needs_extra_preparation == "Yes").astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=.25, stratify=y, random_state=42
    )
    model = DecisionTreeClassifier(
        max_depth=4, min_samples_leaf=4, class_weight="balanced", random_state=42
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    return model, features, X_train, X_test, y_test, predictions


df = make_dataset()
model, features, X_train, X_test, y_test, test_predictions = train_model(df)

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">SAI DATASCIENCE • LIVE AI LAB</div>
      <h1>Can AI identify who may need extra preparation?</h1>
      <p>Change the student profile, ask the model, and inspect how the prediction was made.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

predict_tab, process_tab, insights_tab, responsibility_tab = st.tabs([
    "⚡ Live Predictor", "🔄 ML Process", "📊 Model Insights", "🛡️ Responsible AI"
])

with predict_tab:
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.subheader("Build a student profile")
        technical = st.slider("Technical score", 0, 100, 68)
        aptitude = st.slider("Aptitude score", 0, 100, 65)
        projects = st.slider("Projects completed", 0, 6, 2)
        interview = st.slider("Mock interview score", 0, 100, 62)
        attendance = st.slider("Attendance (%)", 0, 100, 80)

    with right:
        st.subheader("Model suggestion")
        profile = pd.DataFrame([[technical, aptitude, projects, interview, attendance]], columns=features)
        prediction = int(model.predict(profile)[0])
        probability = float(model.predict_proba(profile)[0][1])
        if prediction:
            st.markdown(
                f"<div class='result-support'><h2>Extra preparation may help</h2>"
                f"<p>Illustrative model confidence: <b>{probability:.0%}</b></p></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div class='result-good'><h2>On track in this demonstration</h2>"
                f"<p>Illustrative model confidence: <b>{1-probability:.0%}</b></p></div>",
                unsafe_allow_html=True,
            )

        support = []
        if technical < 65: support.append("technical practice")
        if aptitude < 65: support.append("aptitude practice")
        if projects < 2: support.append("one portfolio project")
        if interview < 65: support.append("mock interviews")
        if attendance < 75: support.append("consistent participation")
        st.markdown("**Possible support plan**")
        if support:
            for item in support:
                st.write(f"• {item.capitalize()}")
        else:
            st.write("• Continue practising and building evidence through projects")

        st.caption("Try changing one slider at a time. When does the prediction change?")

with process_tab:
    st.subheader("What just happened?")
    steps = [
        ("1", "Collect", "Synthetic past student examples"),
        ("2", "Prepare", "Select useful, permitted features"),
        ("3", "Train", "Learn patterns with a decision tree"),
        ("4", "Test", "Check predictions on unseen records"),
        ("5", "Use", "Suggest support—with human review"),
    ]
    cols = st.columns(5)
    for col, (number, title, detail) in zip(cols, steps):
        col.markdown(
            f"<div class='mini-card'><div class='eyebrow'>{number}</div>"
            f"<h3>{title}</h3><p>{detail}</p></div>", unsafe_allow_html=True
        )
    st.info("The model does not understand a student. It finds statistical patterns in the examples it was given.")

with insights_tab:
    accuracy = accuracy_score(y_test, test_predictions)
    a, b, c = st.columns(3)
    a.metric("Synthetic records", len(df))
    b.metric("Training records", len(X_train))
    c.metric("Test accuracy", f"{accuracy:.0%}")

    chart_left, chart_right = st.columns(2, gap="large")
    with chart_left:
        importance = pd.DataFrame({
            "Feature": [name.replace("_", " ").title() for name in features],
            "Importance": model.feature_importances_,
        }).sort_values("Importance")
        fig = px.bar(importance, x="Importance", y="Feature", orientation="h", title="What influenced the model?")
        fig.update_traces(marker_color=GOLD)
        fig.update_layout(template="plotly_dark", paper_bgcolor="#070707", plot_bgcolor="#111111")
        st.plotly_chart(fig, use_container_width=True)
    with chart_right:
        cm = confusion_matrix(y_test, test_predictions)
        cm_df = pd.DataFrame(cm, index=["Actual: On track", "Actual: Support"], columns=["Predicted: On track", "Predicted: Support"])
        fig = px.imshow(cm_df, text_auto=True, color_continuous_scale=[[0, "#181818"], [1, GOLD]], title="Confusion matrix")
        fig.update_layout(template="plotly_dark", paper_bgcolor="#070707")
        st.plotly_chart(fig, use_container_width=True)

    st.download_button(
        "Download the synthetic dataset (CSV)",
        df.to_csv(index=False).encode("utf-8"),
        "synthetic_placement_support_dataset.csv",
        "text/csv",
    )

with responsibility_tab:
    st.subheader("A prediction is not a decision")
    st.markdown(
        """
        <div class="responsible">
        <b>Educational demonstration only.</b> This app uses synthetic data. It must not be used for
        admissions, grading, hiring, interview selection, punishment, or labelling a real student.
        A mentor should review the evidence, speak with the student, and decide what support is appropriate.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("""
    - **Privacy:** use only authorized, necessary data.
    - **Fairness:** check whether errors affect some student groups more than others.
    - **Accuracy:** test with realistic cases and monitor mistakes.
    - **Transparency:** tell people when AI is being used.
    - **Human review:** people own high-impact decisions.
    """)

st.markdown("---")
st.caption("SAI DataScience • Unlock the Power of AI • Synthetic educational demonstration")
