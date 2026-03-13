import os
from dotenv import load_dotenv
from .llm_client import client

load_dotenv()

DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
if not DEPLOYMENT:
    raise RuntimeError("Missing env var: AZURE_OPENAI_DEPLOYMENT")
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "12000"))


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

    resp = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role": "system", "content": "You are a professional summarization assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=400,
    )

    return resp.choices[0].message.content or ""
