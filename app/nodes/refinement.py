"""
Refinement Agent Node - Handles follow-up modification requests.
"""

import json
import logging
import os
from app.llm import call_llm
from app.state import InterviewState

logger = logging.getLogger(__name__)

# Load prompt template
_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "refinement.txt")
with open(_PROMPT_PATH, "r") as f:
    PROMPT_TEMPLATE = f.read()


def refinement_node(state: InterviewState) -> dict:
    """
    Process a user's refinement request and update the question set.
    """
    messages = state["messages"]
    tech_stack = state["tech_stack"]
    experience_years = state["experience_years"]
    seniority_level = state["seniority_level"]
    questions = state["questions"]

    # Get the latest user message
    user_message = ""
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "human":
            user_message = msg.content
            break

    if not user_message:
        logger.warning("No user message found for refinement")
        return {}

    # Build the prompt
    prompt = PROMPT_TEMPLATE.format(
        current_questions=json.dumps({"categories": questions}, indent=2),
        tech_stack=", ".join(tech_stack),
        seniority_level=seniority_level,
        experience_years=experience_years,
        user_message=user_message,
    )

    response = call_llm(prompt=prompt, temperature=0.3, max_tokens=6000)

    # Parse response
    try:
        parsed = json.loads(response.strip())
        updated_questions = parsed.get("categories", {})
    except json.JSONDecodeError:
        logger.warning("Failed to parse refinement response, keeping existing questions")
        return {}

    # Validate structure
    validated_questions = {}
    for category, q_list in updated_questions.items():
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

    if validated_questions:
        logger.info(
            "Refinement applied: %d categories, %d total questions",
            len(validated_questions),
            sum(len(qs) for qs in validated_questions.values()),
        )
        return {"questions": validated_questions}

    return {}
