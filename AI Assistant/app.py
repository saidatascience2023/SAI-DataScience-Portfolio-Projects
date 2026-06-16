import streamlit as st
import random

st.set_page_config(page_title="AI Interview Assistant", layout="wide")

st.title("🤖 AI Interview Assistant")
st.write("Prepare for Data Analyst, Data Scientist, ML Engineer, and AI Engineer interviews.")

role = st.selectbox(
    "Select your target role",
    ["Data Analyst", "Data Scientist", "ML Engineer", "AI Engineer"]
)

level = st.selectbox(
    "Select difficulty level",
    ["Beginner", "Intermediate", "Advanced"]
)

question_bank = {
    "Data Analyst": {
        "Technical": [
            "What is the difference between WHERE and HAVING in SQL?",
            "Explain the difference between INNER JOIN and LEFT JOIN.",
            "How do you handle missing values in a dataset?"
        ],
        "Coding": [
            "Write a Python program to find duplicate values in a list.",
            "Write a SQL query to find the second highest salary."
        ],
        "HR": [
            "Tell me about yourself.",
            "Why do you want to become a Data Analyst?"
        ]
    },
    "Data Scientist": {
        "Technical": [
            "What is overfitting and how can you prevent it?",
            "Explain precision, recall, and F1-score.",
            "What is the difference between supervised and unsupervised learning?"
        ],
        "Coding": [
            "Write Python code to split data into train and test sets.",
            "Write code to calculate accuracy of a model."
        ],
        "HR": [
            "Explain one data science project you have worked on.",
            "How do you communicate model results to non-technical people?"
        ]
    },
    "ML Engineer": {
        "Technical": [
            "What is model deployment?",
            "What is the difference between batch prediction and real-time prediction?",
            "How do you monitor a machine learning model in production?"
        ],
        "Coding": [
            "Write a simple Flask API for model prediction.",
            "Write code to save and load a machine learning model."
        ],
        "HR": [
            "Why are you interested in ML Engineering?",
            "Tell me about a time you solved a technical problem."
        ]
    },
    "AI Engineer": {
        "Technical": [
            "What is prompt engineering?",
            "What is the difference between an LLM and traditional ML model?",
            "What is RAG in Generative AI?"
        ],
        "Coding": [
            "Write a Python function to call an AI model API.",
            "Write a simple chatbot logic using if-else conditions."
        ],
        "HR": [
            "Why do you want to work in AI?",
            "How do you stay updated with AI tools?"
        ]
    }
}

model_answers = {
    "Technical": "Answer should explain the concept clearly, include examples, and connect it to real-world use.",
    "Coding": "Answer should include clean code, logic explanation, and edge case handling.",
    "HR": "Answer should be confident, professional, and connected to your experience or career goal."
}

if st.button("Generate Interview Questions"):
    st.subheader(f"Interview Practice for {role} - {level} Level")

    for category in ["Technical", "Coding", "HR"]:
        st.markdown(f"## {category} Questions")
        questions = random.sample(question_bank[role][category], min(2, len(question_bank[role][category])))

        for i, q in enumerate(questions, 1):
            st.markdown(f"**Q{i}. {q}**")
            st.info(f"Model Answer Guidance: {model_answers[category]}")
            st.write("**Follow-up Question:** Can you explain this with a real project example?")
            st.write("---")

st.sidebar.title("Skills Demonstrated")
st.sidebar.write("- Interview Preparation")
st.sidebar.write("- Career Readiness")
st.sidebar.write("- Role-Based Learning")
st.sidebar.write("- AI Portfolio Project")
