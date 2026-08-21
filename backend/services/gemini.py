from google import genai
from google.genai import types

from services.settings import GEMINI_API_KEY, GEMINI_MODEL


def generate_answer(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to the repository .env file."
        )

    client = genai.Client(api_key=GEMINI_API_KEY)
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
