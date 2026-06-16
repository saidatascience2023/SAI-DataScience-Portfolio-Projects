
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import plotly.express as px

st.set_page_config(
    page_title="Customer Churn Prediction",
    page_icon="📉",
    layout="wide"
)

# ---------------------------
# Helper: synthetic training data
# ---------------------------
@st.cache_data
def create_sample_telco_data(n=1500, seed=42):
    np.random.seed(seed)

    tenure = np.random.randint(1, 73, n)
    monthly_charges = np.random.uniform(20, 120, n)
    contract = np.random.choice(["Month-to-month", "One year", "Two year"], n, p=[0.55, 0.25, 0.20])
    internet_service = np.random.choice(["DSL", "Fiber optic", "No"], n, p=[0.35, 0.45, 0.20])
    online_security = np.random.choice(["Yes", "No"], n, p=[0.35, 0.65])
    tech_support = np.random.choice(["Yes", "No"], n, p=[0.35, 0.65])
    payment_method = np.random.choice(
        ["Electronic check", "Mailed check", "Bank transfer", "Credit card"],
        n,
        p=[0.40, 0.20, 0.20, 0.20]
    )
    senior_citizen = np.random.choice([0, 1], n, p=[0.82, 0.18])

    # Churn probability logic inspired by common Telco churn patterns
    churn_score = (
        0.38 * (contract == "Month-to-month").astype(int)
        + 0.25 * (internet_service == "Fiber optic").astype(int)
        + 0.18 * (payment_method == "Electronic check").astype(int)
        + 0.15 * (online_security == "No").astype(int)
        + 0.15 * (tech_support == "No").astype(int)
        + 0.12 * senior_citizen
        + 0.22 * (tenure < 12).astype(int)
        + 0.16 * (monthly_charges > 80).astype(int)
        - 0.25 * (contract == "Two year").astype(int)
        - 0.18 * (tenure > 36).astype(int)
    )

    probability = 1 / (1 + np.exp(-(churn_score - 0.55) * 3))
    churn = (np.random.rand(n) < probability).astype(int)

    df = pd.DataFrame({
        "tenure": tenure,
        "MonthlyCharges": monthly_charges.round(2),
        "TotalCharges": (tenure * monthly_charges).round(2),
        "Contract": contract,
        "InternetService": internet_service,
        "OnlineSecurity": online_security,
        "TechSupport": tech_support,
        "PaymentMethod": payment_method,
        "SeniorCitizen": senior_citizen,
        "Churn": churn
    })

    return df


@st.cache_resource
def train_model():
    df = create_sample_telco_data()

    X = df.drop(columns=["Churn"])
    y = df["Churn"]

    X_encoded = pd.get_dummies(X, drop_first=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X_encoded, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        random_state=42,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    metrics = {
        "Accuracy": accuracy_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred),
        "Recall": recall_score(y_test, y_pred),
        "F1 Score": f1_score(y_test, y_pred)
    }

    feature_columns = X_encoded.columns.tolist()
    importances = pd.DataFrame({
        "Feature": feature_columns,
        "Importance": model.feature_importances_
    }).sort_values("Importance", ascending=False).head(10)

    return model, feature_columns, metrics, importances, df


def prepare_user_input(data, feature_columns):
    input_df = pd.DataFrame([data])
    input_encoded = pd.get_dummies(input_df)
    input_encoded = input_encoded.reindex(columns=feature_columns, fill_value=0)
    return input_encoded


# ---------------------------
# App UI
# ---------------------------
st.title("📉 Customer Churn Prediction App")
st.write(
    "This app predicts whether a customer is likely to churn using a Random Forest model. "
    "It demonstrates customer analytics, machine learning, feature engineering, and business decision support."
)

model, feature_columns, metrics, importances, sample_df = train_model()

with st.sidebar:
    st.header("Customer Profile")

    tenure = st.slider("Tenure (months)", 1, 72, 12)
    monthly_charges = st.slider("Monthly Charges", 20.0, 120.0, 75.0)
    total_charges = round(tenure * monthly_charges, 2)

    contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])
    internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
    online_security = st.selectbox("Online Security", ["Yes", "No"])
    tech_support = st.selectbox("Tech Support", ["Yes", "No"])
    payment_method = st.selectbox(
        "Payment Method",
        ["Electronic check", "Mailed check", "Bank transfer", "Credit card"]
    )
    senior_citizen = st.selectbox("Senior Citizen", [0, 1])

user_data = {
    "tenure": tenure,
    "MonthlyCharges": monthly_charges,
    "TotalCharges": total_charges,
    "Contract": contract,
    "InternetService": internet_service,
    "OnlineSecurity": online_security,
    "TechSupport": tech_support,
    "PaymentMethod": payment_method,
    "SeniorCitizen": senior_citizen
}

col1, col2, col3 = st.columns(3)
col1.metric("Model Accuracy", f"{metrics['Accuracy']:.2%}")
col2.metric("Recall", f"{metrics['Recall']:.2%}")
col3.metric("F1 Score", f"{metrics['F1 Score']:.2%}")

st.divider()

left, right = st.columns([1, 1])

with left:
    st.subheader("Customer Input Summary")
    st.dataframe(pd.DataFrame([user_data]), use_container_width=True)

    if st.button("Predict Churn Risk", type="primary"):
        X_user = prepare_user_input(user_data, feature_columns)
        prediction = model.predict(X_user)[0]
        probability = model.predict_proba(X_user)[0][1]

        if prediction == 1:
            st.error(f"⚠️ High Churn Risk: {probability:.2%}")
            st.write("This customer may need retention support.")
        else:
            st.success(f"✅ Low Churn Risk: {probability:.2%}")
            st.write("This customer is less likely to churn.")

        st.subheader("Suggested Retention Actions")
        if contract == "Month-to-month":
            st.write("- Offer a one-year or two-year contract discount.")
        if tech_support == "No":
            st.write("- Provide free or discounted technical support.")
        if online_security == "No":
            st.write("- Offer online security as a bundled service.")
        if monthly_charges > 80:
            st.write("- Review pricing plan and suggest a better package.")
        if payment_method == "Electronic check":
            st.write("- Encourage auto-payment through bank transfer or credit card.")

with right:
    st.subheader("Top Model Features")
    fig = px.bar(
        importances.sort_values("Importance"),
        x="Importance",
        y="Feature",
        orientation="h",
        title="Feature Importance from Random Forest"
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Project Summary")
st.write(
    """
    **Industry Domain:** Customer Analytics / Telecom / Business Intelligence  
    **Project Type:** Machine Learning Portfolio Project  
    **Model Used:** Random Forest Classifier  
    **Skills Demonstrated:** Data preprocessing, feature engineering, classification, model evaluation, feature importance, Streamlit deployment.
    """
)

st.info(
    "Note: This deployed demo uses synthetic Telco-style data for portfolio demonstration. "
    "The notebook workflow can be adapted to the original Telco Customer Churn dataset when available."
)
