"""
AI Provider Factory for Yatri Setu (Smart India Hackathon 2026)
"""

import logging
from app.core.config import settings
from app.services.ai.provider import BaseAIProvider
from app.services.ai.mock_provider import MockAIProvider
from app.services.ai.claude_provider import ClaudeAIProvider
from app.services.ai.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)

def get_ai_provider(provider_override: str = None) -> BaseAIProvider:
    provider_type = (provider_override or settings.AI_PROVIDER).lower().strip()
    
    if provider_type == "claude":
        return ClaudeAIProvider()
    elif provider_type == "openai":
        return OpenAIProvider()
    else:
        if provider_type != "mock":
            logger.warning(f"Unrecognized AI_PROVIDER '{provider_type}'. Defaulting to 'mock'.")
        return MockAIProvider()

__all__ = [
    "BaseAIProvider",
    "MockAIProvider",
    "ClaudeAIProvider",
    "OpenAIProvider",
    "get_ai_provider"
]
