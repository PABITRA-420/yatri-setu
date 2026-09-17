"""
AI Provider Factory for Yatri Setu (Smart India Hackathon 2026).
Coordinates primary provider (Gemini), secondary fallback (Groq), and final deterministic fallback (MockAIProvider).
"""

import logging
from typing import Optional

from app.core.config import settings
from app.services.ai.provider import BaseAIProvider
from app.services.ai.mock_provider import MockAIProvider
from app.services.ai.gemini_provider import GeminiAIProvider
from app.services.ai.groq_provider import GroqAIProvider
from app.services.ai.claude_provider import ClaudeAIProvider
from app.services.ai.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


def get_ai_provider(provider_override: Optional[str] = None) -> BaseAIProvider:
    """
    Constructs the configured AI provider with an automatic, resilient fallback chain:
    Gemini (Primary) -> Groq (Secondary Fallback) -> MockAIProvider (Final Deterministic Fallback).
    """
    provider_type = (provider_override or settings.AI_PROVIDER).lower().strip()

    if provider_type == "gemini":
        mock_final = MockAIProvider(provider_name="mock")
        fallback_mode = (settings.AI_FALLBACK_PROVIDER or "groq").lower().strip()
        if fallback_mode == "groq":
            groq_fallback = GroqAIProvider(fallback_provider=mock_final, is_fallback_mode=True)
            return GeminiAIProvider(fallback_provider=groq_fallback)
        return GeminiAIProvider(fallback_provider=mock_final)

    elif provider_type == "groq":
        mock_final = MockAIProvider(provider_name="mock")
        return GroqAIProvider(fallback_provider=mock_final, is_fallback_mode=False)

    elif provider_type == "openai":
        return OpenAIProvider()

    elif provider_type == "claude":
        return ClaudeAIProvider()

    elif provider_type == "mock":
        return MockAIProvider()

    else:
        logger.warning(f"Unrecognized AI_PROVIDER '{provider_type}'. Defaulting to MockAIProvider.")
        return MockAIProvider()


__all__ = [
    "BaseAIProvider",
    "MockAIProvider",
    "GeminiAIProvider",
    "GroqAIProvider",
    "ClaudeAIProvider",
    "OpenAIProvider",
    "get_ai_provider"
]
