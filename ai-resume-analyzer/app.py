#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import PyPDF2
import re

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

ROLE_SKILLS = {
    "Data Analyst": [
        "python", "sql", "excel", "power bi", "tableau",
        "pandas", "data visualization", "statistics", "dashboard"
    ],
    "Data Scientist": [
        "python", "sql", "machine learning", "statistics",
        "pandas", "numpy", "scikit-learn", "model evaluation",
        "feature engineering", "data visualization"
    ],
    "Machine Learning Engineer": [
        "python", "machine learning", "deep learning", "tensorflow",
        "pytorch", "docker", "aws", "api", "mlops",
        "model deployment"
    ],
    "Generative AI Engineer": [
        "python", "llm", "openai", "langchain", "prompt engineering",
        "rag", "vector database", "embeddings", "api", "streamlit"
    ]
}

def extract_text_from_pdf(uploaded_file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + " "
    return text.lower()

def extract_text(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    else:
        return uploaded_file.read().decode("utf-8").lower()

def find_skills(resume_text, required_skills):
    found = []
    missing = []

    for skill in required_skills:
        if skill.lower() in resume_text:
            found.append(skill)
        else:
            missing.append(skill)

    return found, missing

def calculate_score(found, total):
    if total == 0:
        return 0
    return round((len(found) / total) * 100)

st.title("📄 AI Resume Analyzer")
st.write("Upload your resume and check how well it matches your target AI/Data role.")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader(
        "Upload Resume",
        type=["pdf", "txt"]
    )

with col2:
    selected_role = st.selectbox(
        "Select Target Role",
        list(ROLE_SKILLS.keys())
    )

if uploaded_file:
    resume_text = extract_text(uploaded_file)
    required_skills = ROLE_SKILLS[selected_role]

    found_skills, missing_skills = find_skills(resume_text, required_skills)
    score = calculate_score(found_skills, len(required_skills))

    st.divider()

    st.subheader("Resume Match Score")

    if score >= 75:
        st.success(f"Your resume match score is {score}%")
    elif score >= 50:
        st.warning(f"Your resume match score is {score}%")
    else:
        st.error(f"Your resume match score is {score}%")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("✅ Skills Found")
        if found_skills:
            for skill in found_skills:
                st.write(f"- {skill.title()}")
        else:
            st.write("No matching skills found.")

    with col4:
        st.subheader("❌ Missing Skills")
        if missing_skills:
            for skill in missing_skills:
                st.write(f"- {skill.title()}")
        else:
            st.write("Great! No major skills missing.")

    st.divider()

    st.subheader("📌 Project Suggestions")

    if selected_role == "Data Analyst":
        st.write("- Sales Dashboard using Python or Power BI")
        st.write("- Customer Analysis Dashboard")
        st.write("- SQL Business Case Study")

    elif selected_role == "Data Scientist":
        st.write("- Customer Churn Prediction")
        st.write("- House Price Prediction")
        st.write("- Recommendation System")

    elif selected_role == "Machine Learning Engineer":
        st.write("- Deploy ML Model using Streamlit")
        st.write("- Dockerized ML App")
        st.write("- Model API using FastAPI")

    elif selected_role == "Generative AI Engineer":
        st.write("- AI Resume Analyzer")
        st.write("- AI Chatbot using LLM")
        st.write("- RAG-based PDF Question Answering App")

    st.divider()

    st.subheader("🎤 Interview Questions to Prepare")

    questions = [
        f"Tell me about a project related to {selected_role}.",
        "How did you clean and prepare your data?",
        "Which tools or libraries did you use?",
        "What challenges did you face in your project?",
        "How would you improve this project in the future?"
    ]

    for q in questions:
        st.write(f"- {q}")

else:
    st.info("Please upload a resume to begin.")

