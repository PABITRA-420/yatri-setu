"""
OpenAI Provider for Yatri Setu (Smart India Hackathon 2026)
Uses OpenAI Chat Completions API via httpx with automatic fallback to MockAIProvider on missing key or error.
"""

import json
import logging
from typing import Dict, Any, Optional
import httpx

from app.core.config import settings
from app.services.ai.provider import BaseAIProvider
from app.services.ai.mock_provider import MockAIProvider
from app.services.ai.prompts import (
    SYSTEM_PROMPT,
    format_itinerary_context_prompt,
    format_optimization_prompt
)
from app.models.itinerary import ItineraryContext, AIItineraryOutput

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseAIProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self._fallback_provider = MockAIProvider()

    @property
    def provider_name(self) -> str:
        return "openai"

    async def generate_itinerary(self, context: ItineraryContext) -> AIItineraryOutput:
        if not self.api_key or not self.api_key.strip():
            logger.info("OPENAI_API_KEY is not set or empty. Safely falling back to MockAIProvider.")
            output = await self._fallback_provider.generate_itinerary(context)
            output.overview_note += " (Generated via Yatri Setu Himalayan Adaptive Engine; OpenAI key not configured)"
            return output

        prompt = format_itinerary_context_prompt(context)
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key.strip()}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "response_format": {"type": "json_object"},
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.4
                    }
                )
                if response.status_code != 200:
                    status_reason = "rate limit (HTTP 429)" if response.status_code == 429 else f"HTTP {response.status_code}"
                    logger.warning(f"OpenAI API returned status {response.status_code}. Falling back to MockAIProvider: {status_reason}")
                    output = await self._fallback_provider.generate_itinerary(context)
                    output.overview_note += f" (Generated via Yatri Setu Himalayan Adaptive Engine; OpenAI {status_reason} fallback)"
                    return output

                data = response.json()
                content_text = data["choices"][0]["message"]["content"].strip()
                validated = AIItineraryOutput.model_validate_json(content_text)
                if "(Enriched via OpenAI" not in validated.overview_note:
                    validated.overview_note += f" (Enriched via OpenAI {self.model})"
                return validated

        except httpx.TimeoutException:
            logger.warning("OpenAI API request timed out (30s). Falling back to MockAIProvider.")
            output = await self._fallback_provider.generate_itinerary(context)
            output.overview_note += " (Generated via Yatri Setu Himalayan Adaptive Engine; OpenAI timeout fallback)"
            return output
        except Exception as e:
            logger.warning(f"Error calling OpenAI API: {e}. Falling back to MockAIProvider.")
            output = await self._fallback_provider.generate_itinerary(context)
            output.overview_note += " (Generated via Yatri Setu Himalayan Adaptive Engine; provider error fallback)"
            return output

    async def optimize_itinerary(
        self,
        context: ItineraryContext,
        current_itinerary: Dict[str, Any],
        instruction: str,
        custom_instruction: Optional[str] = None
    ) -> AIItineraryOutput:
        if not self.api_key:
            logger.warning("OPENAI_API_KEY is not set. Falling back to MockAIProvider.")
            return await self._fallback_provider.optimize_itinerary(
                context, current_itinerary, instruction, custom_instruction
            )

        prompt = format_optimization_prompt(context, current_itinerary, instruction, custom_instruction)
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "response_format": {"type": "json_object"},
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.4
                    }
                )
                if response.status_code != 200:
                    logger.error(f"OpenAI API optimization returned status {response.status_code}: {response.text}")
                    return await self._fallback_provider.optimize_itinerary(
                        context, current_itinerary, instruction, custom_instruction
                    )

                data = response.json()
                content_text = data["choices"][0]["message"]["content"].strip()
                return AIItineraryOutput.model_validate_json(content_text)

        except Exception as e:
            logger.exception(f"Error calling OpenAI API optimization: {e}. Falling back to MockAIProvider.")
            return await self._fallback_provider.optimize_itinerary(
                context, current_itinerary, instruction, custom_instruction
            )
