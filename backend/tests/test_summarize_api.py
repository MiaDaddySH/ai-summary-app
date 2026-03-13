import os

os.environ.setdefault("AZURE_OPENAI_API_KEY", "test-key")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
os.environ.setdefault("AZURE_OPENAI_DEPLOYMENT", "test-deployment")

from fastapi.testclient import TestClient
from app import main as main_module


client = TestClient(main_module.app)


def test_rejects_text_and_url_together():
    response = client.post("/summarize", json={"text": "hello", "url": "https://example.com"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Provide exactly one of 'text' or 'url'."


def test_rejects_empty_payload():
    response = client.post("/summarize", json={})
    assert response.status_code == 400
    assert response.json()["detail"] == "Provide exactly one of 'text' or 'url'."


def test_rejects_text_over_limit(monkeypatch):
    monkeypatch.setattr(main_module, "MAX_INPUT_CHARS", 5)
    response = client.post("/summarize", json={"text": "123456"})
    assert response.status_code == 413
    assert "Input text too long" in response.json()["detail"]


def test_summarizes_text_success(monkeypatch):
    async def fake_summarize_with_guard(text: str) -> str:
        return f"summary:{text}"

    monkeypatch.setattr(main_module, "summarize_with_guard", fake_summarize_with_guard)
    response = client.post("/summarize", json={"text": "hello"})
    assert response.status_code == 200
    assert response.json() == {"summary": "summary:hello", "source": "text"}


def test_returns_fetch_error_for_bad_url(monkeypatch):
    async def fake_fetch_article_text(url: str) -> str:
        raise RuntimeError("fetch failed")

    monkeypatch.setattr(main_module, "fetch_article_text", fake_fetch_article_text)
    response = client.post("/summarize", json={"url": "https://example.com"})
    assert response.status_code == 400
    assert "Failed to fetch/parse url" in response.json()["detail"]


def test_rejects_short_extracted_text(monkeypatch):
    async def fake_fetch_article_text(url: str) -> str:
        return "short text"

    monkeypatch.setattr(main_module, "fetch_article_text", fake_fetch_article_text)
    response = client.post("/summarize", json={"url": "https://example.com"})
    assert response.status_code == 400
    assert "Extracted text is too short" in response.json()["detail"]


def test_truncates_long_url_article_before_summarizing(monkeypatch):
    captured = {"text": ""}
    monkeypatch.setattr(main_module, "MAX_INPUT_CHARS", 10)

    async def fake_fetch_article_text(url: str) -> str:
        return "a" * 300

    async def fake_summarize_with_guard(text: str) -> str:
        captured["text"] = text
        return "ok"

    monkeypatch.setattr(main_module, "fetch_article_text", fake_fetch_article_text)
    monkeypatch.setattr(main_module, "summarize_with_guard", fake_summarize_with_guard)
    response = client.post("/summarize", json={"url": "https://example.com"})
    assert response.status_code == 200
    assert response.json() == {"summary": "ok", "source": "url"}
    assert len(captured["text"]) == 10


def test_maps_llm_timeout_to_504(monkeypatch):
    def fake_summarize_text(text: str) -> str:
        raise RuntimeError("LLM request timeout")

    monkeypatch.setattr(main_module, "summarize_text", fake_summarize_text)
    response = client.post("/summarize", json={"text": "hello"})
    assert response.status_code == 504
    assert "timeout" in response.json()["detail"].lower()


def test_maps_llm_runtime_error_to_502(monkeypatch):
    def fake_summarize_text(text: str) -> str:
        raise RuntimeError("upstream failure")

    monkeypatch.setattr(main_module, "summarize_text", fake_summarize_text)
    response = client.post("/summarize", json={"text": "hello"})
    assert response.status_code == 502
    assert "upstream failure" in response.json()["detail"]
