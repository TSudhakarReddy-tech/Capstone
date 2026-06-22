# Risk Agent - evaluates loan risk factors
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Risk Agent MCP")

class Applicant(BaseModel):
    income: float
    loan_amount: float
    employment_years: int
    credit_score: int | None = None

@app.post("/analyze")
async def analyze_risk(data: Applicant):
    #Mock Risk Agent Logic
    dti = data.loan_amount / (data.income *12) if data.income > 0 else 1.0
    credit_risk = "Low" if (data.credit_score or 700) > 650 else "High"

    return {
        "dti": round(dti, 2),
        "credit_risk": credit_risk,
        "risk_score": int(dti * 100) if dti < 1 else 100
    }
