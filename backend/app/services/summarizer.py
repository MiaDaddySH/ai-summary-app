import os
import time
from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError
from .llm_client import client

load_dotenv()

DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
if not DEPLOYMENT:
    raise RuntimeError("Missing env var: AZURE_OPENAI_DEPLOYMENT")
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "12000"))
LLM_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "2"))
LLM_RETRY_BASE_DELAY_SECONDS = float(os.getenv("LLM_RETRY_BASE_DELAY_SECONDS", "1.0"))
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def _is_retryable_error(err: Exception) -> bool:
    if isinstance(err, (APITimeoutError, APIConnectionError, RateLimitError)):
        return True
    if isinstance(err, APIStatusError):
        return err.status_code in RETRYABLE_STATUS_CODES
    return False


def _completion_with_retry(messages: list[dict[str, str]]):
    last_err: Exception | None = None
    for attempt in range(LLM_MAX_RETRIES + 1):
        try:
            return client.chat.completions.create(
                model=DEPLOYMENT,
                messages=messages,
                temperature=0.2,
                max_tokens=400,
                timeout=LLM_TIMEOUT_SECONDS,
            )
        except Exception as err:
            last_err = err
            if attempt >= LLM_MAX_RETRIES or not _is_retryable_error(err):
                break
            delay_s = LLM_RETRY_BASE_DELAY_SECONDS * (2 ** attempt)
            time.sleep(delay_s)
    raise RuntimeError(f"LLM request failed: {last_err}")


def summarize_text(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return "Please provide text."
    if len(text) > MAX_INPUT_CHARS:
        text = text[:MAX_INPUT_CHARS]

    prompt = (
        "Summarize the article in English and Chinese.\n"
        "Requirements:\n"
        "1) Use 5 bullet points.\n"
        "2) End with one short takeaway sentence.\n"
        "3) Be concise.\n\n"
        f"Article:\n{text}"
    )

    resp = _completion_with_retry(
        [
            {"role": "system", "content": "You are a professional summarization assistant."},
            {"role": "user", "content": prompt},
        ]
    )

    return resp.choices[0].message.content or ""
