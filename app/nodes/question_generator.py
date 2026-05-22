"""
Question Generator Node - Generates categorized interview questions with answers.
"""

import json
import logging
import os
from app.llm import call_llm
from app.config import QUESTION_COUNTS
from app.state import InterviewState

logger = logging.getLogger(__name__)

# Load prompt template
_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "question_generator.txt")
with open(_PROMPT_PATH, "r") as f:
    PROMPT_TEMPLATE = f.read()


def question_generator_node(state: InterviewState) -> dict:
    """
    Generate interview questions for each category based on the candidate profile.
    """
    tech_stack = state["tech_stack"]
    experience_years = state["experience_years"]
    seniority_level = state["seniority_level"]
    categories = state["categories"]
    projects = state.get("projects", "")
    print("CATEGIES:******", categories)
    questions_per_category = QUESTION_COUNTS.get(seniority_level, 4)

    # Fill in the prompt template
    prompt = PROMPT_TEMPLATE.format(
        tech_stack=", ".join(tech_stack),
        seniority_level=seniority_level,
        experience_years=experience_years,
        categories=", ".join(categories),
        questions_per_category=questions_per_category,
        projects=projects if projects else "Not specified",
    )

    response = call_llm(prompt=prompt, temperature=0.3, max_tokens=6000)

    # Parse LLM response
    try:
        cleaned = response.strip()
        # Strip markdown code fences if present (e.g. ```json ... ```)
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]  # remove first line (```json or ```)
            cleaned = cleaned.rsplit("```", 1)[0]  # remove trailing ```
        parsed = json.loads(cleaned.strip())
        questions = parsed.get("categories", {})
    except json.JSONDecodeError as e:
        logger.warning("Failed to parse question generator response: %s", e)
        logger.warning("Raw response: %s", response[:500])
        questions = {}

    # Validate structure
    validated_questions = {}
    for category, q_list in questions.items():
        if isinstance(q_list, list):
            validated_questions[category] = [
                {
                    "question": q.get("question", ""),
                    "answer": q.get("answer", ""),
                    "difficulty": q.get("difficulty", "medium"),
                }
                for q in q_list
                if isinstance(q, dict) and q.get("question")
            ]

    logger.info(
        "Generated questions: %d categories, %d total questions",
        len(validated_questions),
        sum(len(qs) for qs in validated_questions.values()),
    )

    return {"questions": validated_questions}
