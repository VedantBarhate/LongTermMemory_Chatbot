# pyrefly: ignore [missing-import]
from openrouter import OpenRouter

from config import OPENROUTER_API_KEY, MODEL_NAME


class OpenRouterClient:

    def __init__(self):
        if not OPENROUTER_API_KEY:
            raise ValueError(
                "OPENROUTER_API_KEY is not set in the .env file."
            )

        self.client = OpenRouter(
            api_key=OPENROUTER_API_KEY
        )

    def generate_response(self, messages):
        response = self.client.chat.send(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7
        )

        return response.choices[0].message.content