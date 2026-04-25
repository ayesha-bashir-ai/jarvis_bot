from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
import time
import random
from datetime import datetime
from dotenv import load_dotenv

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

load_dotenv()

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

api_key = os.getenv("OPENROUTER_API_KEY")
client = None
if api_key and OpenAI is not None:
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
    except Exception as exc:
        print(f"Warning: failed to initialize OpenRouter client: {exc}")
        client = None
else:
    print("Warning: OPENROUTER_API_KEY not set; AI chat responses will be disabled.")

app = FastAPI(title="JARVIS AI Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if os.getenv("ENVIRONMENT", "development") != "production":
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


def handle_browser(message: str):
    msg = message.lower()

    sites = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "github": "https://github.com",
    }

    for site, url in sites.items():
        if f"open {site}" in msg:
            return {
                "message": f"Opening {site}",
                "action": "open_url",
                "url": url,
            }

    if "search" in msg:
        query = msg.replace("search", "").strip()
        url = f"https://google.com/search?q={query}"
        return {
            "message": f"Searching {query}",
            "action": "open_url",
            "url": url,
        }

    return None


@app.post("/api/v1/chat")
async def chat(req: ChatRequest):
    start = time.time()

    browser = handle_browser(req.message)
    if browser:
        return browser

    msg = req.message.lower()

    if "time" in msg:
        return {"message": datetime.now().strftime("%I:%M %p")}

    if "date" in msg:
        return {"message": datetime.now().strftime("%Y-%m-%d")}

    if "joke" in msg:
        return {
            "message": random.choice([
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "I told my PC I need a break - now it won't stop sending memes!",
                "Debugging: Being the detective in a crime movie where you are also the murderer.",
            ])
        }

    if client is None:
        return {
            "message": "AI chat is currently unavailable. Set the OPENROUTER_API_KEY environment variable to enable conversational responses. In the meantime, try asking for the time, date, a joke, or to open YouTube/Google/GitHub.",
        }

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are JARVIS, a helpful AI assistant."},
                {"role": "user", "content": req.message},
            ],
        )

        return {
            "message": response.choices[0].message.content,
            "execution_time": round(time.time() - start, 2),
        }

    except Exception as e:
        return {"message": "AI error occurred", "error": str(e)}


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "time": datetime.now().isoformat(),
        "ai_enabled": client is not None,
    }


@app.get("/health")
def health_legacy():
    return health()


@app.get("/favicon.ico")
async def favicon():
    favicon_path = os.path.join(STATIC_DIR, "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return JSONResponse(status_code=404, content={"detail": "favicon not found"})


if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
    )
