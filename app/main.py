"""
FastAPI backend for the Interview Question Generator.
"""

import os
import uuid
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

from app.graph import app as langgraph_app
from app.config import OUTPUT_DIR

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fastapi_app = FastAPI(title="Interview Question Generator", version="1.0.0")

# CORS for local development
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request/Response Models ---

class GenerateRequest(BaseModel):
    tech_stack: list[str]
    experience_years: int
    projects: str | None = ""
    session_id: str | None = None


class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    session_id: str
    markdown: str
    message: str


# --- Endpoints ---

@fastapi_app.post("/generate", response_model=ChatResponse)
async def generate_questions(request: GenerateRequest):
    """Initial question generation from structured form input."""
    session_id = request.session_id or str(uuid.uuid4())

    # Build initial state
    initial_state = {
        "messages": [
            HumanMessage(
                content=f"Generate interview questions for: {', '.join(request.tech_stack)} with {request.experience_years} years of experience"
            )
        ],
        "tech_stack": request.tech_stack,
        "experience_years": request.experience_years,
        "projects": request.projects or "",
        "seniority_level": "",
        "categories": [],
        "questions": {},
        "markdown_output": "",
        "output_file_path": "",
        "session_id": session_id,
        "action": "generate",
    }

    config = {"configurable": {"thread_id": session_id}}

    try:
        result = langgraph_app.invoke(initial_state, config)
    except Exception as e:
        logger.exception("Graph execution failed")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

    markdown = result.get("markdown_output", "")

    return ChatResponse(
        session_id=session_id,
        markdown=markdown,
        message="Questions generated successfully! You can now ask me to refine them.",
    )


@fastapi_app.post("/chat", response_model=ChatResponse)
async def chat_refine(request: ChatRequest):
    """Handle follow-up refinement requests via free-form chat."""
    session_id = request.session_id

    # Build refinement state update
    state_update = {
        "messages": [HumanMessage(content=request.message)],
        "action": "refine",
    }

    config = {"configurable": {"thread_id": session_id}}

    try:
        result = langgraph_app.invoke(state_update, config)
    except Exception as e:
        logger.exception("Refinement failed")
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")

    markdown = result.get("markdown_output", "")

    return ChatResponse(
        session_id=session_id,
        markdown=markdown,
        message="Questions updated based on your request.",
    )


@fastapi_app.get("/download/{session_id}")
async def download_markdown(session_id: str):
    """Download the generated markdown file."""
    filename = f"interview_{session_id}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found. Generate questions first.")

    return FileResponse(
        filepath,
        media_type="text/markdown",
        filename=filename,
    )


@fastapi_app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the frontend HTML."""
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    with open(frontend_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8080)
