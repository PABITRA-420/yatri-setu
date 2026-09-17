"""
Google Gemini AI Provider for Yatri Setu (Smart India Hackathon 2026).
Primary AI provider for natural language itinerary generation and optimization.
Gracefully degrades to Groq fallback or MockAIProvider on missing key, timeout, 429, or error.
"""

import json
import logging
from typing import Dict, Any, Optional
import httpx
from pydantic import ValidationError

from app.core.config import settings
from app.services.ai.provider import BaseAIProvider
from app.services.ai.prompts import (
    SYSTEM_PROMPT,
    format_itinerary_context_prompt,
    format_optimization_prompt
)
from app.models.itinerary import ItineraryContext, AIItineraryOutput

logger = logging.getLogger(__name__)


def _clean_json_text(raw_text: str) -> str:
    """Strips markdown code fences from LLM responses."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


class GeminiAIProvider(BaseAIProvider):
    """
    Primary AI provider connecting to Google Gemini API (v1beta) via httpx.
    Non-authoritative: used strictly for travel narrative enrichment and scheduling.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        fallback_provider: Optional[BaseAIProvider] = None
    ):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL or "gemini-3.6-flash"
        self._fallback_provider = fallback_provider

    @property
    def fallback_provider(self) -> BaseAIProvider:
        if self._fallback_provider is None:
            # Lazy import to avoid circular dependencies
            from app.services.ai.groq_provider import GroqAIProvider
            from app.services.ai.mock_provider import MockAIProvider
            self._fallback_provider = GroqAIProvider(fallback_provider=MockAIProvider())
        return self._fallback_provider

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def generate_itinerary(self, context: ItineraryContext) -> AIItineraryOutput:
        """Generates structured itinerary via Gemini API with fallback."""
        if not self.api_key or not self.api_key.strip():
            logger.info("GEMINI_API_KEY is not set or empty. Falling back to secondary provider.")
            return await self.fallback_provider.generate_itinerary(context)

        prompt = format_itinerary_context_prompt(context)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

        headers = {
            "x-goog-api-key": self.api_key.strip(),
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": prompt}]}
            ],
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "generationConfig": {
                "temperature": 0.4,
                "response_mime_type": "application/json"
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code != 200:
                    status_reason = (
                        "rate limit (HTTP 429)" if response.status_code == 429
                        else f"HTTP {response.status_code}"
                    )
                    logger.warning(
                        f"Gemini API returned status {response.status_code} ({status_reason}). "
                        f"Attempting fallback to {self.fallback_provider.provider_name}."
                    )
                    return await self.fallback_provider.generate_itinerary(context)

                data = response.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    logger.warning(
                        f"Gemini API returned 0 candidates. Attempting fallback to {self.fallback_provider.provider_name}."
                    )
                    return await self.fallback_provider.generate_itinerary(context)

                parts = candidates[0].get("content", {}).get("parts", [])
                raw_text = parts[0].get("text", "") if parts else ""
                clean_text = _clean_json_text(raw_text)

                validated = AIItineraryOutput.model_validate_json(clean_text)
                validated.provider_used = "gemini"
                if "(Enriched via Gemini" not in validated.overview_note:
                    validated.overview_note += f" (Enriched via Gemini {self.model})"
                return validated

        except httpx.TimeoutException:
            logger.warning(
                f"Gemini API request timed out (30s). Attempting fallback to {self.fallback_provider.provider_name}."
            )
            return await self.fallback_provider.generate_itinerary(context)

        except (ValidationError, json.JSONDecodeError) as val_err:
            logger.warning(
                f"Gemini API returned malformed response ({val_err}). "
                f"Attempting fallback to {self.fallback_provider.provider_name}."
            )
            return await self.fallback_provider.generate_itinerary(context)

        except Exception as e:
            logger.warning(
                f"Error calling Gemini API: {e}. Attempting fallback to {self.fallback_provider.provider_name}."
            )
            return await self.fallback_provider.generate_itinerary(context)

    async def optimize_itinerary(
        self,
        context: ItineraryContext,
        current_itinerary: Dict[str, Any],
        instruction: str,
        custom_instruction: Optional[str] = None
    ) -> AIItineraryOutput:
        """Adapts and optimizes an existing itinerary according to user directive via Gemini."""
        if not self.api_key or not self.api_key.strip():
            logger.info("GEMINI_API_KEY is not set or empty. Falling back to secondary provider for optimization.")
            return await self.fallback_provider.optimize_itinerary(
                context, current_itinerary, instruction, custom_instruction
            )

        prompt = format_optimization_prompt(context, current_itinerary, instruction, custom_instruction)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

        headers = {
            "x-goog-api-key": self.api_key.strip(),
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": prompt}]}
            ],
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "generationConfig": {
                "temperature": 0.4,
                "response_mime_type": "application/json"
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code != 200:
                    logger.warning(
                        f"Gemini API optimization returned HTTP {response.status_code}. "
                        f"Attempting fallback to {self.fallback_provider.provider_name}."
                    )
                    return await self.fallback_provider.optimize_itinerary(
                        context, current_itinerary, instruction, custom_instruction
                    )

                data = response.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    return await self.fallback_provider.optimize_itinerary(
                        context, current_itinerary, instruction, custom_instruction
                    )

                parts = candidates[0].get("content", {}).get("parts", [])
                raw_text = parts[0].get("text", "") if parts else ""
                clean_text = _clean_json_text(raw_text)

                validated = AIItineraryOutput.model_validate_json(clean_text)
                validated.provider_used = "gemini"
                return validated

        except Exception as e:
            logger.warning(
                f"Error calling Gemini API optimization: {e}. "
                f"Attempting fallback to {self.fallback_provider.provider_name}."
            )
            return await self.fallback_provider.optimize_itinerary(
                context, current_itinerary, instruction, custom_instruction
            )
