"""
Anthropic Claude AI Provider for Yatri Setu (Smart India Hackathon 2026)
Uses Anthropic Messages API via httpx with automatic fallback to MockAIProvider on missing key or network error.
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

class ClaudeAIProvider(BaseAIProvider):
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model = settings.ANTHROPIC_MODEL
        self._fallback_provider = MockAIProvider()

    @property
    def provider_name(self) -> str:
        return "claude"

    async def generate_itinerary(self, context: ItineraryContext) -> AIItineraryOutput:
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY is not set. Falling back to MockAIProvider.")
            output = await self._fallback_provider.generate_itinerary(context)
            output.overview_note += " (Generated via Yatri Setu Himalayan Adaptive Engine; Claude key not configured)"
            return output

        prompt = format_itinerary_context_prompt(context)
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "max_tokens": 3000,
                        "system": SYSTEM_PROMPT,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ]
                    }
                )
                if response.status_code != 200:
                    logger.error(f"Claude API returned status {response.status_code}: {response.text}")
                    return await self._fallback_provider.generate_itinerary(context)

                data = response.json()
                content_text = data["content"][0]["text"].strip()

                # Clean markdown backticks if returned
                if content_text.startswith("```json"):
                    content_text = content_text[7:]
                if content_text.startswith("```"):
                    content_text = content_text[3:]
                if content_text.endswith("```"):
                    content_text = content_text[:-3]

                return AIItineraryOutput.model_validate_json(content_text.strip())

        except Exception as e:
            logger.exception(f"Error calling Claude API: {e}. Falling back to MockAIProvider.")
            return await self._fallback_provider.generate_itinerary(context)

    async def optimize_itinerary(
        self,
        context: ItineraryContext,
        current_itinerary: Dict[str, Any],
        instruction: str,
        custom_instruction: Optional[str] = None
    ) -> AIItineraryOutput:
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY is not set. Falling back to MockAIProvider.")
            return await self._fallback_provider.optimize_itinerary(
                context, current_itinerary, instruction, custom_instruction
            )

        prompt = format_optimization_prompt(context, current_itinerary, instruction, custom_instruction)
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "max_tokens": 3000,
                        "system": SYSTEM_PROMPT,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ]
                    }
                )
                if response.status_code != 200:
                    logger.error(f"Claude API optimization returned status {response.status_code}: {response.text}")
                    return await self._fallback_provider.optimize_itinerary(
                        context, current_itinerary, instruction, custom_instruction
                    )

                data = response.json()
                content_text = data["content"][0]["text"].strip()
                if content_text.startswith("```json"):
                    content_text = content_text[7:]
                if content_text.startswith("```"):
                    content_text = content_text[3:]
                if content_text.endswith("```"):
                    content_text = content_text[:-3]

                return AIItineraryOutput.model_validate_json(content_text.strip())

        except Exception as e:
            logger.exception(f"Error calling Claude API optimization: {e}. Falling back to MockAIProvider.")
            return await self._fallback_provider.optimize_itinerary(
                context, current_itinerary, instruction, custom_instruction
            )
