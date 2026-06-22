# Compliance Agent - ensures regulatory compliance
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Compliance Agent MCP")

class Notification(BaseModel):
    case_id:str
    classification:str
    applicant:dict

@app.post("/notify")
async def send_notification(data: Notification):
    # Mock compliance logging + notification
    print(f"[COMPLIANCE] Case {data.case_id}: {data.classification}")
    return {"status": "notified", "case_id": data.case_id}