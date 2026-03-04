from fastapi import FastAPI
from pydantic import BaseModel
from app.services.summarizer import summarize_text

app = FastAPI()


class SummaryRequest(BaseModel):
    text: str


class SummaryResponse(BaseModel):
    summary: str


@app.post("/summarize", response_model=SummaryResponse)
def summarize(req: SummaryRequest):
    summary = summarize_text(req.text)
    return {"summary": summary}