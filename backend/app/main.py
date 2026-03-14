import logging
import time
from uuid import uuid4
from fastapi import FastAPI, Body, HTTPException, Request
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from app.services.summarizer import summarize_text
from app.services.article_fetcher import fetch_article_text
from app.settings import settings

app = FastAPI(title="AI Summary API (Azure OpenAI)")
MAX_INPUT_CHARS = settings.max_input_chars
logger = logging.getLogger("app.api")
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

class SummarizeRequest(BaseModel):
    text: str | None = None
    url: str | None = None

class SummarizeResponse(BaseModel):
    summary: str
    source: str  # "text" or "url"


@app.middleware("http")
async def request_observability_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", "").strip() or uuid4().hex
    request.state.request_id = request_id
    start_at = time.perf_counter()
    logger.info(
        "request.start request_id=%s method=%s path=%s",
        request_id,
        request.method,
        request.url.path,
    )
    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = int((time.perf_counter() - start_at) * 1000)
        logger.exception(
            "request.error request_id=%s method=%s path=%s elapsed_ms=%s",
            request_id,
            request.method,
            request.url.path,
            elapsed_ms,
        )
        raise
    elapsed_ms = int((time.perf_counter() - start_at) * 1000)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request.end request_id=%s method=%s path=%s status_code=%s elapsed_ms=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


async def summarize_with_guard(text: str, request_id: str) -> str:
    try:
        return await run_in_threadpool(summarize_text, text, request_id)
    except RuntimeError as e:
        msg = str(e)
        status_code = 504 if "timeout" in msg.lower() else 502
        logger.warning(
            "llm.error request_id=%s status_code=%s detail=%s",
            request_id,
            status_code,
            msg,
        )
        raise HTTPException(status_code=status_code, detail=msg)
    except Exception:
        logger.exception("llm.error request_id=%s status_code=502", request_id)
        raise HTTPException(status_code=502, detail="LLM service unavailable.")


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: Request, payload: SummarizeRequest = Body(...)):
    request_id = request.state.request_id
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
        summary = await summarize_with_guard(text, request_id)
        return {"summary": summary, "source": "text"}

    if url:
        try:
            article_text = await fetch_article_text(url, request_id=request_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch/parse url: {e}")

        if len(article_text) < 200:
            raise HTTPException(
                status_code=400,
                detail="Extracted text is too short (possible paywall/cookie wall). Try paste text instead."
            )

        if len(article_text) > MAX_INPUT_CHARS:
            article_text = article_text[:MAX_INPUT_CHARS]

        summary = await summarize_with_guard(article_text, request_id)
        return {"summary": summary, "source": "url"}

    raise HTTPException(status_code=400, detail="Invalid request.")
