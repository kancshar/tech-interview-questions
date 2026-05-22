"""
LLM wrapper that provides a unified interface around PepGenXService
for use by LangGraph agent nodes.
"""

import logging
from typing import Optional
from app.pepgenx_service import PepGenXService

logger = logging.getLogger(__name__)

# Singleton instance
_service: Optional[PepGenXService] = None


def get_llm_service() -> PepGenXService:
    """Get or create the PepGenX service singleton."""
    global _service
    if _service is None:
        _service = PepGenXService()
    return _service


def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: int = 4000,
) -> str:
    """
    Call the PepGenX LLM with a user prompt and optional system prompt.

    Args:
        prompt: The user message/prompt
        system_prompt: Optional system instructions for the LLM
        temperature: Sampling temperature (0.0 = deterministic)
        max_tokens: Maximum tokens in response

    Returns:
        The LLM's text response

    Raises:
        RuntimeError: If the LLM call fails
    """
    service = get_llm_service()
    logger.info("Calling LLM: prompt_length=%d, system_prompt=%s", len(prompt), bool(system_prompt))

    response = service.generate_response(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response
