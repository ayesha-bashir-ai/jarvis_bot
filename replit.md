# JARVIS AI Assistant

## Overview
JARVIS is an AI chat assistant with a FastAPI backend and a static HTML/CSS/JS frontend. The backend exposes a chat API that handles simple commands (time, date, jokes, opening sites) locally and falls back to an LLM (via OpenRouter) for general conversation.

## Project Layout
- `backend/` - FastAPI application (`backend/main.py` is the entry point used in this Replit setup)
- `frontend/` - Static site (`index.html`, `css/`, `js/`) served by FastAPI's StaticFiles
- `data/` - SQLite database file location (`jarvis.db`)
- `scripts/` - Helper scripts (`init_db.py`, `backup.py`, `migrate.py`)
- `tests/` - Pytest suites

## Replit Setup
- Single workflow `Start application` runs `uvicorn backend.main:app --host 0.0.0.0 --port 5000`.
- The FastAPI app serves both the JSON API (`/api/v1/chat`, `/api/health`) and the static frontend (mounted at `/`) on port 5000, so there is no separate frontend port and no port conflict.
- Frontend `js/app.js` uses an empty `apiEndpoint` by default so requests are issued against the same origin (works behind the Replit proxy).
- CORS is wide-open (`allow_origins=["*"]`) which is appropriate for development behind the iframe proxy.

## Environment Variables
- `OPENROUTER_API_KEY` (optional) - enables LLM-backed chat responses via OpenRouter (`openai/gpt-4o-mini`). When unset, the backend still serves all built-in commands and returns a friendly notice for free-form prompts.
- Other variables referenced by `backend/config.py` (`OPENAI_API_KEY`, `WEATHER_API_KEY`, `NEWS_API_KEY`, etc.) are optional and only used by additional services not wired into `main.py`.

## Deployment
Deploy as an autoscale web service running `uvicorn backend.main:app --host 0.0.0.0 --port 5000`.

## Notes / Recent Changes
- 2026-04-25: Imported from GitHub. Re-encoded `requirements.txt` from UTF-16 to UTF-8 so pip can read it. Rewrote `backend/main.py` to mount the static frontend, make `OPENROUTER_API_KEY` optional, fix the favicon path, and bind to port 5000. Updated `frontend/js/app.js` to call the API via a relative URL instead of the hardcoded Railway URL.
