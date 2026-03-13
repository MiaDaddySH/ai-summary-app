import asyncio
import os
import httpx
from dotenv import load_dotenv
from readability import Document
from bs4 import BeautifulSoup

load_dotenv()

DEFAULT_HEADERS = {
    "User-Agent": "AI-Summary-App/0.1 (contact: your-email@example.com)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}
FETCH_TIMEOUT_SECONDS = float(os.getenv("FETCH_TIMEOUT_SECONDS", "15"))
FETCH_MAX_RETRIES = int(os.getenv("FETCH_MAX_RETRIES", "2"))
FETCH_RETRY_BASE_DELAY_SECONDS = float(os.getenv("FETCH_RETRY_BASE_DELAY_SECONDS", "1.0"))
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def _is_retryable_error(err: Exception) -> bool:
    if isinstance(err, (httpx.TimeoutException, httpx.NetworkError)):
        return True
    if isinstance(err, httpx.HTTPStatusError):
        return err.response.status_code in RETRYABLE_STATUS_CODES
    return False


async def fetch_article_text(url: str, timeout: float | None = None) -> str:
    url = (url or "").strip()
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")
    request_timeout = timeout if timeout is not None else FETCH_TIMEOUT_SECONDS

    last_err: Exception | None = None

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

            return cleaned

        except Exception as e:
            last_err = e
            if attempt >= FETCH_MAX_RETRIES or not _is_retryable_error(e):
                break
            delay_s = FETCH_RETRY_BASE_DELAY_SECONDS * (2 ** attempt)
            await asyncio.sleep(delay_s)

    raise RuntimeError(f"Failed to fetch url after retries: {last_err}")
