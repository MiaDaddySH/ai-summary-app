from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing env var: {name}")
    return value


def _get_int(name: str, default: int, min_value: int = 0) -> int:
    raw = os.getenv(name, str(default)).strip()
    value = int(raw)
    if value < min_value:
        raise RuntimeError(f"Invalid env var: {name} must be >= {min_value}")
    return value


def _get_float(name: str, default: float, min_value: float = 0.0) -> float:
    raw = os.getenv(name, str(default)).strip()
    value = float(raw)
    if value < min_value:
        raise RuntimeError(f"Invalid env var: {name} must be >= {min_value}")
    return value


@dataclass(frozen=True)
class Settings:
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment: str
    max_input_chars: int
    llm_timeout_seconds: float
    llm_max_retries: int
    llm_retry_base_delay_seconds: float
    fetch_timeout_seconds: float
    fetch_max_retries: int
    fetch_retry_base_delay_seconds: float


settings = Settings(
    azure_openai_api_key=_require_env("AZURE_OPENAI_API_KEY"),
    azure_openai_endpoint=_require_env("AZURE_OPENAI_ENDPOINT"),
    azure_openai_deployment=_require_env("AZURE_OPENAI_DEPLOYMENT"),
    max_input_chars=_get_int("MAX_INPUT_CHARS", 12000, min_value=1),
    llm_timeout_seconds=_get_float("LLM_TIMEOUT_SECONDS", 30.0, min_value=0.1),
    llm_max_retries=_get_int("LLM_MAX_RETRIES", 2, min_value=0),
    llm_retry_base_delay_seconds=_get_float("LLM_RETRY_BASE_DELAY_SECONDS", 1.0, min_value=0.0),
    fetch_timeout_seconds=_get_float("FETCH_TIMEOUT_SECONDS", 15.0, min_value=0.1),
    fetch_max_retries=_get_int("FETCH_MAX_RETRIES", 2, min_value=0),
    fetch_retry_base_delay_seconds=_get_float("FETCH_RETRY_BASE_DELAY_SECONDS", 1.0, min_value=0.0),
)
