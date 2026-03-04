from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Summary API")

class SummaryRequest(BaseModel):
    text: str

class SummaryResponse(BaseModel):
    summary: str

@app.post("/summarize", response_model=SummaryResponse)
def summarize(req: SummaryRequest):
    # 先用假数据跑通全链路，后面再接 LLM
    text = req.text.strip()
    if not text:
        return {"summary": "Please provide text."}
    return {"summary": text[:120] + ("..." if len(text) > 120 else "")}