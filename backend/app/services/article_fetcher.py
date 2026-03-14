import asyncio
import logging
import time
import httpx
from readability import Document
from bs4 import BeautifulSoup
from app.settings import settings

DEFAULT_HEADERS = {
    "User-Agent": "AI-Summary-App/0.1 (contact: your-email@example.com)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}
FETCH_TIMEOUT_SECONDS = settings.fetch_timeout_seconds
FETCH_MAX_RETRIES = settings.fetch_max_retries
FETCH_RETRY_BASE_DELAY_SECONDS = settings.fetch_retry_base_delay_seconds
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
logger = logging.getLogger("app.fetcher")


def _is_retryable_error(err: Exception) -> bool:
    if isinstance(err, (httpx.TimeoutException, httpx.NetworkError)):
        return True
    if isinstance(err, httpx.HTTPStatusError):
        return err.response.status_code in RETRYABLE_STATUS_CODES
    return False


async def fetch_article_text(url: str, timeout: float | None = None, request_id: str = "-") -> str:
    url = (url or "").strip()
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")
    request_timeout = timeout if timeout is not None else FETCH_TIMEOUT_SECONDS

    last_err: Exception | None = None
    start_at = time.perf_counter()

    for attempt in range(FETCH_MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                headers=DEFAULT_HEADERS,
                timeout=request_timeout,
            ) as client:
                r = await client.get(url)

            if r.status_code in RETRYABLE_STATUS_CODES:
                err = httpx.HTTPStatusError(
                    f"Retryable status code: {r.status_code}",
                    request=r.request,
                    response=r,
                )
                if attempt >= FETCH_MAX_RETRIES:
                    raise err
                last_err = err
                logger.warning(
                    "fetch.retry request_id=%s attempt=%s status_code=%s",
                    request_id,
                    attempt + 1,
                    r.status_code,
                )
                delay_s = FETCH_RETRY_BASE_DELAY_SECONDS * (2 ** attempt)
                await asyncio.sleep(delay_s)
                continue

            r.raise_for_status()

            doc = Document(r.text)
            article_html = doc.summary()

            soup = BeautifulSoup(article_html, "lxml")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()

            text = soup.get_text(separator="\n")
            lines = [ln.strip() for ln in text.splitlines()]
            cleaned = "\n".join([ln for ln in lines if ln])

            elapsed_ms = int((time.perf_counter() - start_at) * 1000)
            logger.info(
                "fetch.success request_id=%s attempts=%s elapsed_ms=%s text_chars=%s",
                request_id,
                attempt + 1,
                elapsed_ms,
                len(cleaned),
            )
            return cleaned

        except Exception as e:
            last_err = e
            retryable = _is_retryable_error(e)
            logger.warning(
                "fetch.error request_id=%s attempt=%s retryable=%s error_type=%s",
                request_id,
                attempt + 1,
                retryable,
                type(e).__name__,
            )
            if attempt >= FETCH_MAX_RETRIES or not retryable:
                break
            delay_s = FETCH_RETRY_BASE_DELAY_SECONDS * (2 ** attempt)
            await asyncio.sleep(delay_s)

    elapsed_ms = int((time.perf_counter() - start_at) * 1000)
    logger.error(
        "fetch.failed request_id=%s attempts=%s elapsed_ms=%s error=%s",
        request_id,
        FETCH_MAX_RETRIES + 1,
        elapsed_ms,
        last_err,
    )
    raise RuntimeError(f"Failed to fetch url after retries: {last_err}")
