import httpx
from readability import Document
from bs4 import BeautifulSoup

# 一些站点会对默认 UA 直接返回空/机器人页
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

def fetch_article_text(url: str, timeout: float = 15.0) -> str:
    url = (url or "").strip()
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")

    with httpx.Client(follow_redirects=True, headers=DEFAULT_HEADERS, timeout=timeout) as client:
        r = client.get(url)
        r.raise_for_status()

    # readability 提取“正文 HTML”
    doc = Document(r.text)
    article_html = doc.summary()

    # 用 BeautifulSoup 把正文 HTML 转为纯文本
    soup = BeautifulSoup(article_html, "lxml")

    # 去掉脚本/样式
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    # 清理空行
    lines = [ln.strip() for ln in text.splitlines()]
    cleaned = "\n".join([ln for ln in lines if ln])

    return cleaned