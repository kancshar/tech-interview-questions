"""
State schema for the Interview Question Generator LangGraph app.
"""

from typing import Annotated, Any
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class InterviewState(TypedDict):
    """State that flows through the LangGraph interview question generator."""

    # Conversation history (append-only via add_messages reducer)
    messages: Annotated[list[BaseMessage], add_messages]

    # Parsed profile information
    tech_stack: list[str]
    experience_years: int
    projects: str  # Optional: candidate's project descriptions
    seniority_level: str  # "junior", "mid", "senior", "staff"

    # Generated content
    categories: list[str]
    questions: dict[str, list[dict[str, Any]]]
    # Format: {"category": [{"question": str, "answer": str, "difficulty": str}]}

    # Output
    markdown_output: str
    output_file_path: str

    # Routing
    session_id: str
    action: str  # "generate" or "refine"
