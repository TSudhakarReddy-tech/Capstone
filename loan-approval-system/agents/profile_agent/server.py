# Profile Agent - handles customer profile analysis
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Profile Agent MCP")

class Applicant(BaseModel):
    income: float
    loan_amount: float
    employment_years: int
    credit_score: int | None = None

@app.post("/analyze")
async def analyze_profile(data: Applicant):
    # Mock Profile Agent logic
    income_stability = "High" if data.income > 5000 else "Low"
    employment_risk = "Low" if data.employment_years > 2 else "High"

    return {
        "income_stability": income_stability,
        "employment_risk": employment_risk,
        "income": data.income,
        "employment_years": data.employment_years
    }