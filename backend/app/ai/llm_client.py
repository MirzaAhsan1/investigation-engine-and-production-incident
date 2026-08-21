import requests

from app.core.config import settings


class LLMClient:

    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()

        # Ollama config
        self.url = settings.OLLAMA_URL
        self.model = settings.LLM_MODEL
        self.timeout = settings.LLM_TIMEOUT

        # Gemini config
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.gemini_model = settings.GEMINI_MODEL

    def generate(self, prompt: str) -> str:
        if self.provider == "gemini":
            return self._generate_gemini(prompt)
        return self._generate_ollama(prompt)

    # ==========================================================
    # OLLAMA (local)
    # ==========================================================
    def _generate_ollama(self, prompt: str) -> str:
        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "format": "json",
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                    },
                },
                timeout=(5, self.timeout),
            )
            response.raise_for_status()
            return response.json()["response"]

        except requests.Timeout:
            raise Exception("LLM request timeout (ollama)")

        except requests.RequestException as exc:
            raise Exception(f"LLM request failed (ollama): {exc}")

    # ==========================================================
    # GEMINI (API - free tier)
    # ==========================================================
    def _generate_gemini(self, prompt: str) -> str:
        if not self.gemini_api_key:
            raise Exception("GEMINI_API_KEY not set in .env")

        endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.gemini_model}:generateContent?key={self.gemini_api_key}"
        )

        try:
            response = requests.post(
                endpoint,
                json={
                    "contents": [
                        {"parts": [{"text": prompt}]}
                    ],
                    "generationConfig": {
                        "temperature": 0.1,
                        "topP": 0.9,
                        "responseMimeType": "application/json",
                    },
                },
                timeout=(5, self.timeout),
            )
            response.raise_for_status()

            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

        except requests.Timeout:
            raise Exception("LLM request timeout (gemini)")

        except requests.RequestException as exc:
            raise Exception(f"LLM request failed (gemini): {exc}")

        except (KeyError, IndexError) as exc:
            raise Exception(f"Unexpected Gemini response format: {exc}")