import asyncio
import httpx
from readability import Document
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": "AI-Summary-App/0.1 (contact: your-email@example.com)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

async def fetch_article_text(url: str, timeout: float = 15.0) -> str:
    url = (url or "").strip()
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")

    last_err: Exception | None = None

    for attempt in range(3):
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                headers=DEFAULT_HEADERS,
                timeout=timeout,
            ) as client:
                r = await client.get(url)

            if r.status_code == 429:
                sleep_s = 1.0 * (2 ** attempt)
                await asyncio.sleep(sleep_s)
                last_err = httpx.HTTPStatusError("429 Too Many Requests", request=r.request, response=r)
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
            await asyncio.sleep(0.3)

    raise RuntimeError(f"Failed to fetch url after retries: {last_err}")
