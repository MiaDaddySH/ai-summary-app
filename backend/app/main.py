from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
from app.services.summarizer import summarize_text
from app.services.article_fetcher import fetch_article_text

app = FastAPI(title="AI Summary API (Azure OpenAI)")

class SummarizeRequest(BaseModel):
    text: str | None = None
    url: str | None = None

class SummarizeResponse(BaseModel):
    summary: str
    source: str  # "text" or "url"


@app.post("/summarize", response_model=SummarizeResponse)
def summarize(payload: SummarizeRequest = Body(...)):
    if payload.text:
        return {"summary": summarize_text(payload.text), "source": "text"}

    if payload.url:
        try:
            article_text = fetch_article_text(payload.url)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch/parse url: {e}")

        if len(article_text) < 200:
            # 很多站点会返回“cookie wall / paywall / 机器人页”，正文会很短
            raise HTTPException(
                status_code=400,
                detail="Extracted text is too short (possible paywall/cookie wall). Try paste text instead."
            )

        return {"summary": summarize_text(article_text), "source": "url"}

    raise HTTPException(status_code=400, detail="Provide either 'text' or 'url'.")