from openai import OpenAI
from app.settings import settings
client = OpenAI(
    api_key=settings.azure_openai_api_key,
    base_url=f"{settings.azure_openai_endpoint.rstrip('/')}/openai/v1/",
)
