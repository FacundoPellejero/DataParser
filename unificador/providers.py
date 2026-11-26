import os
import time

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")

def gemini_call(prompt: str, model: str = DEFAULT_MODEL, retries: int = 3) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client()
    config = types.GenerateContentConfig(temperature=0)


    for attempt in range(retries):
        try:
            response = client.models.generate_content(model = model, contents = prompt, config = config)
            return response.text
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)