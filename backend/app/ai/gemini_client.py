import json
import asyncio
import logging
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

def _get_model(use_pro: bool = False) -> genai.GenerativeModel:
    model_name = "gemini-1.5-pro" if use_pro else settings.GEMINI_MODEL
    return genai.GenerativeModel(model_name)

async def call_gemini(prompt: str, use_pro: bool = False) -> str:
    """Call Gemini API with retry logic for rate limits."""
    model = _get_model(use_pro)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = await asyncio.to_thread(
                model.generate_content, prompt
            )
            return response.text
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 1
                logger.warning(f"Rate limited. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Gemini API error: {e}")
                raise

async def call_gemini_json(prompt: str, use_pro: bool = False) -> dict:
    """Call Gemini and parse JSON response."""
    raw = await call_gemini(prompt, use_pro)
    # Strip markdown code blocks if present
    cleaned = raw.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return json.loads(cleaned.strip())
