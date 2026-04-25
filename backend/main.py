from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
import time
import random
import base64
import mimetypes
import re
from datetime import datetime
from dotenv import load_dotenv

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

load_dotenv()

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_TEXT_CHARS = 20000

TEXT_EXTENSIONS = {
    ".txt", ".md", ".csv", ".json", ".py", ".js", ".html", ".css"
}

api_key = os.getenv("OPENROUTER_API_KEY")

client = None
if api_key and OpenAI:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

app = FastAPI(title="JARVIS AI Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


@app.post("/api/v1/chat")
async def chat(req: ChatRequest):
    msg = req.message.lower()

    if "time" in msg:
        return {"message": datetime.now().strftime("%I:%M %p")}

    if "date" in msg:
        return {"message": datetime.now().strftime("%Y-%m-%d")}

    if "joke" in msg:
        return {"message": random.choice([
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Debugging is like detective work.",
            "My code works… I have no idea why."
        ])}

    if client is None:
        return {"message": "AI disabled. Set OPENROUTER_API_KEY"}

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are JARVIS AI assistant."},
                {"role": "user", "content": req.message},
            ],
        )

        return {"message": response.choices[0].message.content}

    except Exception as e:
        return {"message": "AI error", "error": str(e)}


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "ai_enabled": client is not None,
        "time": datetime.now().isoformat()
    }


@app.get("/favicon.ico")
async def favicon():
    path = os.path.join(STATIC_DIR, "favicon.ico")
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse(status_code=404, content={"detail": "not found"})


if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
