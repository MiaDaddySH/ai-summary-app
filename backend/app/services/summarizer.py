# backend/app/services/summarizer.py
import os
from dotenv import load_dotenv
from .llm_client import client

load_dotenv()

DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
if not DEPLOYMENT:
    raise RuntimeError("Missing env var: AZURE_OPENAI_DEPLOYMENT")


def summarize_text(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return "Please provide text."

    resp = client.chat.completions.create(
        model=DEPLOYMENT,  # Azure: deployment name
        messages=[
            {"role": "system", "content": "You summarize articles clearly and concisely."},
            {"role": "user", "content": f"Summarize the following article:\n\n{text}"},
        ],
        temperature=0.3,
        max_tokens=180,
    )

    return resp.choices[0].message.content or ""