from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
import time
import random
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# -------------------
# LOAD ENV
# -------------------
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise Exception("OPENROUTER_API_KEY not found")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

# -------------------
# APP SETUP
# -------------------
app = FastAPI(title="JARVIS AI Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------
# REQUEST MODEL
# -------------------
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

# -------------------
# BROWSER TOOL
# -------------------
def handle_browser(message: str):
    msg = message.lower()

    sites = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "github": "https://github.com"
    }

    for site, url in sites.items():
        if f"open {site}" in msg:
            return {
                "message": f"Opening {site}",
                "action": "open_url",
                "url": url
            }

    if "search" in msg:
        query = msg.replace("search", "").strip()
        url = f"https://google.com/search?q={query}"
        return {
            "message": f"Searching {query}",
            "action": "open_url",
            "url": url
        }

    return None

# -------------------
# CHAT API
# -------------------
@app.post("/api/v1/chat")
async def chat(req: ChatRequest):
    start = time.time()

    # 1. Browser tool first
    browser = handle_browser(req.message)
    if browser:
        return browser

    msg = req.message.lower()

    # 2. Simple commands
    if "time" in msg:
        return {
            "message": datetime.now().strftime("%I:%M %p")
        }

    if "date" in msg:
        return {
            "message": datetime.now().strftime("%Y-%m-%d")
        }

    if "joke" in msg:
        return {
            "message": random.choice([
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "I told my PC I need a break — now it won’t stop sending memes!",
                "Debugging: Being the detective in a crime movie where you are also the murderer."
            ])
        }

    # 3. AI RESPONSE
    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are JARVIS, a helpful AI assistant."},
                {"role": "user", "content": req.message}
            ]
        )

        return {
            "message": response.choices[0].message.content,
            "execution_time": round(time.time() - start, 2)
        }

    except Exception as e:
        return {
            "message": "AI error occurred",
            "error": str(e)
        }

# -------------------
# ROUTES
# -------------------
@app.get("/")
def root():
    return {"status": "JARVIS ONLINE"}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "time": datetime.now().isoformat()
    }

# -------------------
# RUN SERVER (LOCAL ONLY)
# -------------------
if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )