from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from graph import graph
import traceback

app = FastAPI(title="Loan Approval Gateway")

class Applicant(BaseModel):
    income: float
    loan_amount: float
    employment_years: int
    credit_score: int | None = None

@app.post("/process-loan")
async def process_loan(applicant: Applicant):
    try:
        result = await graph.ainvoke({
            "applicant_data": applicant.model_dump(),
            "profile_output": None,
            "risk_output": None,
            "decision_output": None,
            "compliance_output": None
        })
        return result
    except Exception as e:
        tb = traceback.format_exc()
        print("ERROR:", tb)  # will show in uvicorn terminal
        raise HTTPException(status_code=500, detail=tb)