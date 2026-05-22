# Interview Question Generator

A multi-agent LangGraph application that generates tailored interview questions based on a candidate's tech stack and years of experience. Questions are categorized, balanced by difficulty, and output as a downloadable `.md` file.

## Architecture

The app uses 4 specialized LangGraph agents:

| Agent | Responsibility |
|-------|---------------|
| **Profile Analyzer** | Infers seniority level, identifies primary/secondary skills, determines question categories |
| **Question Generator** | Generates balanced questions per category with short answers and difficulty tags |
| **Formatter** | Assembles structured markdown and writes `.md` file to disk |
| **Refinement Agent** | Handles follow-up requests (add/remove questions, change difficulty, focus on a category) |

### Flow

```
[Initial Request]
Form Input → Profile Analyzer → Question Generator → Formatter → .md file

[Refinement]
Chat Message → Refinement Agent → Formatter → Updated .md file
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your PepGenX credentials
```

Required environment variables:
- `OKTA_CLIENT_ID` / `OKTA_CLIENT_SECRET` — Okta OAuth2 credentials
- `PEPGENX_API_KEY` / `PEPGENX_TEAM_ID` / `PEPGENX_PROJECT_ID` — PepGenX API access
- Or set `PEPGENX_BEARER_TOKEN` directly for local development

### 3. Run the application

```bash
python -m app.main
```

Open http://127.0.0.1:8080 in your browser.

## Usage

1. **Enter your profile** — Fill in the tech stack (comma-separated) and years of experience in the form
2. **Generate** — Click "Generate Questions" to get categorized interview questions
3. **Refine** — Use the chat to modify results:
   - "Add 3 more system design questions"
   - "Make the Python questions harder"
   - "Remove behavioral questions"
   - "Add a section on microservices"
4. **Download** — Click "Download .md" to save the file

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/generate` | Initial question generation from structured input |
| `POST` | `/chat` | Free-form refinement requests |
| `GET` | `/download/{session_id}` | Download generated `.md` file |
| `GET` | `/` | Serve frontend UI |

### POST /generate

```json
{
  "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
  "experience_years": 5
}
```

### POST /chat

```json
{
  "message": "Add more database questions",
  "session_id": "uuid-from-generate-response"
}
```

## Project Structure

```
interview-repo/
├── app/
│   ├── config.py              # Seniority thresholds, question counts
│   ├── graph.py               # LangGraph StateGraph with routing
│   ├── llm.py                 # Wrapper around PepGenXService
│   ├── main.py                # FastAPI endpoints
│   ├── pepgenx_service.py     # Enterprise LLM service (PepGenX + Okta)
│   ├── state.py               # InterviewState schema
│   ├── nodes/
│   │   ├── profile_analyzer.py
│   │   ├── question_generator.py
│   │   ├── formatter.py
│   │   └── refinement.py
│   └── prompts/
│       ├── profile_analyzer.txt
│       ├── question_generator.txt
│       └── refinement.txt
├── frontend/
│   └── index.html             # Hybrid UI (form + chat)
├── output/                    # Generated .md files
├── requirements.txt
└── .env.example
```

## Tech Stack

- **LangGraph** — Multi-agent orchestration with state management
- **FastAPI** — Backend API
- **PepGenX** — Enterprise LLM (via Okta OAuth2)
- **Vanilla JS** — Frontend (no build step)
