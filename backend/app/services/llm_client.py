# backend/app/services/llm_client.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_OPENAI_API_KEY")

if not AZURE_ENDPOINT or not AZURE_KEY:
    missing = [k for k, v in {
        "AZURE_OPENAI_ENDPOINT": AZURE_ENDPOINT,
        "AZURE_OPENAI_API_KEY": AZURE_KEY,
    }.items() if not v]
    raise RuntimeError(f"Missing env vars: {missing}")

# OpenAI-compatible Azure endpoint
# NOTE: /openai/v1/ is the OpenAI-compatible route on Azure
client = OpenAI(
    api_key=AZURE_KEY,
    base_url=f"{AZURE_ENDPOINT.rstrip('/')}/openai/v1/",
)