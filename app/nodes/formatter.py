"""
Formatter Node - Assembles questions into structured markdown and writes .md file.
"""

import os
import logging
from datetime import datetime
from app.config import OUTPUT_DIR
from app.state import InterviewState

logger = logging.getLogger(__name__)

DIFFICULTY_EMOJI = {
    "easy": "🟢",
    "medium": "🟡",
    "hard": "🔴",
}


def formatter_node(state: InterviewState) -> dict:
    """
    Format questions into a structured markdown document and write to disk.
    """
    tech_stack = state["tech_stack"]
    experience_years = state["experience_years"]
    seniority_level = state["seniority_level"]
    questions = state["questions"]
    session_id = state["session_id"]

    # Build markdown
    lines = []
    lines.append("# Interview Questions")
    lines.append("")
    lines.append("## Candidate Profile")
    lines.append(f"- **Tech Stack:** {', '.join(tech_stack)}")
    lines.append(f"- **Experience:** {experience_years} years")
    lines.append(f"- **Seniority Level:** {seniority_level.title()}")
    lines.append(f"- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary
    total_questions = sum(len(qs) for qs in questions.values())
    lines.append(f"**Total Questions:** {total_questions} across {len(questions)} categories")
    lines.append("")
    lines.append("| Difficulty | Count |")
    lines.append("|-----------|-------|")

    difficulty_counts = {"easy": 0, "medium": 0, "hard": 0}
    for qs in questions.values():
        for q in qs:
            d = q.get("difficulty", "medium")
            difficulty_counts[d] = difficulty_counts.get(d, 0) + 1

    for diff, count in difficulty_counts.items():
        emoji = DIFFICULTY_EMOJI.get(diff, "")
        lines.append(f"| {emoji} {diff.title()} | {count} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Questions by category
    for category, q_list in questions.items():
        lines.append(f"## {category}")
        lines.append("")

        for i, q in enumerate(q_list, 1):
            difficulty = q.get("difficulty", "medium")
            emoji = DIFFICULTY_EMOJI.get(difficulty, "")
            lines.append(f"### {i}. {q['question']} {emoji}")
            lines.append("")
            lines.append(f"**Answer:** {q['answer']}")
            lines.append("")
            lines.append(f"*Difficulty: {difficulty.title()}*")
            lines.append("")
            lines.append("---")
            lines.append("")

    markdown_output = "\n".join(lines)

    # Write to file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"interview_{session_id}.md"
    output_path = os.path.join(OUTPUT_DIR, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_output)

    logger.info("Markdown written to %s (%d chars)", output_path, len(markdown_output))

    return {
        "markdown_output": markdown_output,
        "output_file_path": output_path,
    }
