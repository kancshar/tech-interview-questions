"""
LangGraph StateGraph definition for the Interview Question Generator.

Flow:
  - Initial generation: profile_analyzer → question_generator → formatter → END
  - Refinement: refinement → formatter → END
  
Routing is determined by the `action` field in state.
"""

import logging
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.state import InterviewState
from app.nodes.profile_analyzer import profile_analyzer_node
from app.nodes.question_generator import question_generator_node
from app.nodes.formatter import formatter_node
from app.nodes.refinement import refinement_node

logger = logging.getLogger(__name__)


def route_entry(state: InterviewState) -> str:
    """Route based on action: 'generate' goes to full pipeline, 'refine' goes to refinement."""
    action = state.get("action", "generate")
    if action == "refine":
        return "refinement"
    return "profile_analyzer"


def build_graph() -> StateGraph:
    """Construct and compile the interview question generator graph."""
    graph = StateGraph(InterviewState)

    # Add nodes
    graph.add_node("profile_analyzer", profile_analyzer_node)
    graph.add_node("question_generator", question_generator_node)
    graph.add_node("formatter", formatter_node)
    graph.add_node("refinement", refinement_node)

    # Entry routing
    graph.add_conditional_edges(START, route_entry, {
        "profile_analyzer": "profile_analyzer",
        "refinement": "refinement",
    })

    # Generation pipeline
    graph.add_edge("profile_analyzer", "question_generator")
    graph.add_edge("question_generator", "formatter")
    graph.add_edge("formatter", END)

    # Refinement pipeline
    graph.add_edge("refinement", "formatter")

    return graph


# Compiled app with memory checkpointer for multi-turn conversations
memory = MemorySaver()
app = build_graph().compile(checkpointer=memory)
