"""
Groq AI Provider for Yatri Setu (Smart India Hackathon 2026).
Ultra-low-latency secondary AI provider for natural language itinerary generation and optimization.
Serves as high-speed fallback when Gemini is unavailable or rate-limited.
Falls back seamlessly to MockAIProvider on missing key, timeout, 429, or error.
"""

import json
import logging
from typing import Dict, Any, Optional
import httpx
from pydantic import ValidationError

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


_UNSET = object()


class GroqAIProvider(BaseAIProvider):
    """
    Fallback AI provider connecting to Groq OpenAI-compatible chat completions API via httpx.
    Non-authoritative: used strictly for travel narrative enrichment and scheduling.
    """

    def __init__(
        self,
        api_key: Any = _UNSET,
        model: Optional[str] = None,
        fallback_provider: Optional[BaseAIProvider] = None,
        is_fallback_mode: bool = True
    ):
        self.api_key = api_key if api_key is not _UNSET else settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL or "openai/gpt-oss-120b"
        self._fallback_provider = fallback_provider or MockAIProvider()
        self.is_fallback_mode = is_fallback_mode

    @property
    def fallback_provider(self) -> BaseAIProvider:
        return self._fallback_provider

    @property
    def provider_name(self) -> str:
        return "groq"

    async def generate_itinerary(self, context: ItineraryContext) -> AIItineraryOutput:
        """Generates structured itinerary via Groq API with Mock fallback."""
        if not self.api_key or not self.api_key.strip():
            logger.info("GROQ_API_KEY is not set or empty. Falling back to MockAIProvider.")
            output = await self.fallback_provider.generate_itinerary(context)
            output.provider_used = self.fallback_provider.provider_name
            return output

        prompt = format_itinerary_context_prompt(context)
        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4
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
                        f"Groq API returned status {response.status_code} ({status_reason}). "
                        f"Falling back to {self.fallback_provider.provider_name}."
                    )
                    output = await self.fallback_provider.generate_itinerary(context)
                    output.provider_used = self.fallback_provider.provider_name
                    return output

                data = response.json()
                choices = data.get("choices", [])
                if not choices:
                    logger.warning(f"Groq API returned 0 choices. Falling back to {self.fallback_provider.provider_name}.")
                    output = await self.fallback_provider.generate_itinerary(context)
                    output.provider_used = self.fallback_provider.provider_name
                    return output

                content_text = choices[0].get("message", {}).get("content", "").strip()
                clean_text = _clean_json_text(content_text)

                validated = AIItineraryOutput.model_validate_json(clean_text)
                validated.provider_used = "groq_fallback" if self.is_fallback_mode else "groq"
                if "(Enriched via Groq" not in validated.overview_note:
                    validated.overview_note += f" (Enriched via Groq {self.model})"
                return validated

        except httpx.TimeoutException:
            logger.warning(
                f"Groq API request timed out (30s). Falling back to {self.fallback_provider.provider_name}."
            )
            output = await self.fallback_provider.generate_itinerary(context)
            output.provider_used = self.fallback_provider.provider_name
            return output

        except (ValidationError, json.JSONDecodeError) as val_err:
            logger.warning(
                f"Groq API returned malformed response ({val_err}). Falling back to {self.fallback_provider.provider_name}."
            )
            output = await self.fallback_provider.generate_itinerary(context)
            output.provider_used = self.fallback_provider.provider_name
            return output

        except Exception as e:
            logger.warning(
                f"Error calling Groq API: {e}. Falling back to {self.fallback_provider.provider_name}."
            )
            output = await self.fallback_provider.generate_itinerary(context)
            output.provider_used = self.fallback_provider.provider_name
            return output

    async def optimize_itinerary(
        self,
        context: ItineraryContext,
        current_itinerary: Dict[str, Any],
        instruction: str,
        custom_instruction: Optional[str] = None
    ) -> AIItineraryOutput:
        """Adapts and optimizes an existing itinerary according to user directive via Groq."""
        if not self.api_key or not self.api_key.strip():
            logger.info("GROQ_API_KEY is not set. Falling back to MockAIProvider for optimization.")
            output = await self.fallback_provider.optimize_itinerary(
                context, current_itinerary, instruction, custom_instruction
            )
            output.provider_used = self.fallback_provider.provider_name
            return output

        prompt = format_optimization_prompt(context, current_itinerary, instruction, custom_instruction)
        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)

                if response.status_code != 200:
                    logger.warning(
                        f"Groq API optimization returned HTTP {response.status_code}. "
                        f"Falling back to {self.fallback_provider.provider_name}."
                    )
                    output = await self.fallback_provider.optimize_itinerary(
                        context, current_itinerary, instruction, custom_instruction
                    )
                    output.provider_used = self.fallback_provider.provider_name
                    return output

                data = response.json()
                choices = data.get("choices", [])
                if not choices:
                    output = await self.fallback_provider.optimize_itinerary(
                        context, current_itinerary, instruction, custom_instruction
                    )
                    output.provider_used = self.fallback_provider.provider_name
                    return output

                content_text = choices[0].get("message", {}).get("content", "").strip()
                clean_text = _clean_json_text(content_text)

                validated = AIItineraryOutput.model_validate_json(clean_text)
                validated.provider_used = "groq_fallback" if self.is_fallback_mode else "groq"
                return validated

        except Exception as e:
            logger.warning(
                f"Error calling Groq API optimization: {e}. "
                f"Falling back to {self.fallback_provider.provider_name}."
            )
            output = await self.fallback_provider.optimize_itinerary(
                context, current_itinerary, instruction, custom_instruction
            )
            output.provider_used = self.fallback_provider.provider_name
            return output
