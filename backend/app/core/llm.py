from openai import AsyncOpenAI

from app.core.config import settings


def llm_enabled() -> bool:
    return bool(settings.OPENROUTER_API_KEY)


def get_llm_client() -> AsyncOpenAI:
    headers = {
        "HTTP-Referer": settings.OPENROUTER_APP_URL,
        "X-Title": settings.OPENROUTER_APP_NAME,
    }
    return AsyncOpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
        default_headers=headers,
    )
