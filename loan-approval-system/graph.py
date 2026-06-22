from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
import httpx
from datetime import datetime
from uuid import uuid4
import json
import os
from dotenv import load_dotenv

load_dotenv()

class LoanState(TypedDict):
    applicant_data: dict
    profile_output: dict | None
    risk_output: dict | None
    decision_output: dict | None
    compliance_output: dict | None

llm = ChatOpenAI(
    model="global.anthropic.claude-sonnet-4-6",
    base_url="https://llmgw-wp.tekstac.com/v1",
    api_key=os.getenv("BEDROCK_API_KEY"),
    temperature=0
)

async def profile_node(state: LoanState) -> LoanState:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://localhost:8001/analyze",
            json=state["applicant_data"],
            timeout=10.0
        )
        resp.raise_for_status()
        state["profile_output"] = resp.json()
    return state

async def risk_node(state: LoanState) -> LoanState:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://localhost:8002/analyze",
            json=state["applicant_data"],
            timeout=10.0
        )
        resp.raise_for_status()
        state["risk_output"] = resp.json()
    return state

async def decision_node(state: LoanState) -> LoanState:
    prompt = f"""
    You are a loan underwriter. Based on:
    Profile: {json.dumps(state['profile_output'])}
    Risk: {json.dumps(state['risk_output'])}

    Return ONLY valid JSON:
    {{
        "classification": "Approve" | "Reject" | "Review",
        "risk_score": int,
        "confidence_level": float,
        "key_decision_factors": [str],
        "explanation": "2 sentences for audit trail"
    }}
    """
    resp = await llm.ainvoke(prompt)
    content = resp.content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    state["decision_output"] = json.loads(content)
    return state

async def compliance_node(state: LoanState) -> LoanState:
    payload = {
        "case_id": str(uuid4()),
        "classification": state["decision_output"]["classification"],
        "applicant": state["applicant_data"]
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://localhost:8004/notify",
            json=payload,
            timeout=10.0
        )
        resp.raise_for_status()
        state["compliance_output"] = resp.json()
    return state

builder = StateGraph(LoanState)
builder.add_node("profile", profile_node)
builder.add_node("risk", risk_node)
builder.add_node("decision", decision_node)
builder.add_node("compliance", compliance_node)

builder.set_entry_point("profile")
builder.add_edge("profile", "risk")
builder.add_edge("risk", "decision")
builder.add_edge("decision", "compliance")
builder.add_edge("compliance", END)

graph = builder.compile() # removed checkpointer to avoid crash