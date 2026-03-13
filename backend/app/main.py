import os
from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from app.services.summarizer import summarize_text
from app.services.article_fetcher import fetch_article_text

app = FastAPI(title="AI Summary API (Azure OpenAI)")
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "12000"))

class SummarizeRequest(BaseModel):
    text: str | None = None
    url: str | None = None

class SummarizeResponse(BaseModel):
    summary: str
    source: str  # "text" or "url"


async def summarize_with_guard(text: str) -> str:
    try:
        return await run_in_threadpool(summarize_text, text)
    except RuntimeError as e:
        msg = str(e)
        status_code = 504 if "timeout" in msg.lower() else 502
        raise HTTPException(status_code=status_code, detail=msg)
    except Exception:
        raise HTTPException(status_code=502, detail="LLM service unavailable.")


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(payload: SummarizeRequest = Body(...)):
    text = (payload.text or "").strip()
    url = (payload.url or "").strip()

    if bool(text) == bool(url):
        raise HTTPException(status_code=400, detail="Provide exactly one of 'text' or 'url'.")

    if text:
        if len(text) > MAX_INPUT_CHARS:
            raise HTTPException(
                status_code=413,
                detail=f"Input text too long. Max {MAX_INPUT_CHARS} characters.",
            )
        summary = await summarize_with_guard(text)
        return {"summary": summary, "source": "text"}

    if url:
        try:
            article_text = await fetch_article_text(url)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch/parse url: {e}")

        if len(article_text) < 200:
            raise HTTPException(
                status_code=400,
                detail="Extracted text is too short (possible paywall/cookie wall). Try paste text instead."
            )

        if len(article_text) > MAX_INPUT_CHARS:
            article_text = article_text[:MAX_INPUT_CHARS]

        summary = await summarize_with_guard(article_text)
        return {"summary": summary, "source": "url"}

    raise HTTPException(status_code=400, detail="Invalid request.")
