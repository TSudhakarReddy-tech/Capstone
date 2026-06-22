import streamlit as st
import httpx

st.set_page_config(page_title="Loan Approval System", layout="wide")
st.title("4-Agent Loan Approval System")

col1, col2 = st.columns(2)

with col1:
    income = st.number_input("Annual Income ($)", value=5000.0, step=100.0)
    loan_amount = st.number_input("Loan Amount ($)", value=20000.0, step=100.0)

with col2:
    employment_years = st.number_input("Employment Years", value=3, step=1)
    credit_score = st.number_input("Credit Score", value=720, step=1)

if st.button("Process Loan", type="primary"):
    payload = {
        "income": income,
        "loan_amount": loan_amount,
        "employment_years": employment_years,
        "credit_score": credit_score
    }
    
    with st.spinner("Running 4-agent workflow..."):
        try:
            resp = httpx.post("http://localhost:8000/process-loan", json=payload, timeout=30.0)
            resp.raise_for_status()
            result = resp.json()
        except httpx.HTTPStatusError as e:
            st.error(f"Backend returned {e.response.status_code}")
            st.code(e.response.text)
            st.stop()
        except Exception as e:
            st.error(f"Request failed: {e}")
            st.stop()

    st.divider()

    st.subheader("Decision Output")
    st.json(result.get("decision_output", result.get("decision")))

    st.subheader("Full Audit Trail")
    st.json({
        "profile_agent": result["profile_output"],
        "risk_agent": result["risk_output"],
        "compliance_agent": result["compliance_output"]
    })