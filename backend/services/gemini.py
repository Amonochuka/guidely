from google import genai
from google.genai import types

from services.settings import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TIMEOUT_MS


class GeminiConfigurationError(RuntimeError):
    """Raised when the required Gemini configuration is absent."""


def generate_answer(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise GeminiConfigurationError(
            "GEMINI_API_KEY is not set. Add it to the repository .env file."
        )

    client = genai.Client(
        api_key=GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=GEMINI_TIMEOUT_MS),
    )
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_level="medium"
            )
        ),
    )

    return response.text
