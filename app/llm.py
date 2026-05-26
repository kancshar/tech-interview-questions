"""
LLM wrapper using Groq via LangChain (OpenAI-compatible)
for use by LangGraph agent nodes.
"""

import os
import logging
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

_llm: Optional[ChatOpenAI] = None


def get_llm_service() -> ChatOpenAI:
    """Get or create the Groq LLM singleton."""
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            openai_api_key=os.getenv("GROQ_API_KEY"),
            openai_api_base="https://api.groq.com/openai/v1",
            temperature=0.0,
            max_tokens=4000,
        )
    return _llm


def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: int = 4000,
) -> str:
    """
    Call Groq LLM with a user prompt and optional system prompt.
    """
    llm = get_llm_service()
    logger.info("Calling Groq: prompt_length=%d, system_prompt=%s", len(prompt), bool(system_prompt))

    messages = []
    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))
    messages.append(HumanMessage(content=prompt))

    response = llm.invoke(messages, temperature=temperature, max_tokens=max_tokens)
    return response.content
