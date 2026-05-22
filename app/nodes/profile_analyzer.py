"""
Profile Analyzer Node - Parses tech stack, infers seniority, determines categories.
"""

import json
import logging
import os
from app.llm import call_llm
from app.config import get_seniority
from app.state import InterviewState

logger = logging.getLogger(__name__)

# Load prompt template
_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "profile_analyzer.txt")
with open(_PROMPT_PATH, "r") as f:
    SYSTEM_PROMPT = f.read()


def profile_analyzer_node(state: InterviewState) -> dict:
    """
    Analyze the candidate profile. When called from the structured form,
    tech_stack and experience_years are already populated. This node
    infers seniority and determines question categories via LLM.
    """
    tech_stack = state["tech_stack"]
    experience_years = state["experience_years"]
    projects = state.get("projects", "")

    # Determine seniority from years
    seniority_level = get_seniority(experience_years)

    # Build prompt for LLM to determine categories
    user_prompt = (
        f"Candidate Profile:\n"
        f"- Tech Stack: {', '.join(tech_stack)}\n"
        f"- Years of Experience: {experience_years}\n"
        f"- Seniority Level: {seniority_level}\n"
    )
    if projects:
        user_prompt += f"- Projects: {projects}\n"
    user_prompt += "\nAnalyze this profile and determine the interview question categories."

    response = call_llm(prompt=user_prompt, system_prompt=SYSTEM_PROMPT)

    # Parse LLM response
    try:
        analysis = json.loads(response.strip())
        categories = analysis.get("categories", [])
    except json.JSONDecodeError:
        logger.warning("Failed to parse LLM response as JSON, using default categories")
        categories = _default_categories(tech_stack, seniority_level)

    if not categories:
        categories = _default_categories(tech_stack, seniority_level)

    logger.info(
        "Profile analyzed: seniority=%s, categories=%s",
        seniority_level,
        categories,
    )

    return {
        "seniority_level": seniority_level,
        "categories": categories,
    }


def _default_categories(tech_stack: list[str], seniority_level: str) -> list[str]:
    """Fallback categories if LLM parsing fails."""
    categories = ["Core Fundamentals", "Problem Solving & Algorithms"]

    # Add a category for each tech (up to 3)
    for tech in tech_stack[:3]:
        categories.append(tech)

    if seniority_level in ("mid", "senior", "staff"):
        categories.append("System Design & Architecture")

    if seniority_level in ("senior", "staff"):
        categories.append("Leadership & Best Practices")

    return categories
