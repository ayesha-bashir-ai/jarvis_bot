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
import webbrowser

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
            webbrowser.open(url)
            return f"Opening {site}"

    if "search" in msg:
        q = msg.replace("search", "").strip()
        url = f"https://google.com/search?q={q}"
        webbrowser.open(url)
        return f"Searching {q}"

    return None

# -------------------
# CHAT API
# -------------------
@app.post("/api/v1/chat")
async def chat(req: ChatRequest):
    start = time.time()

    browser = handle_browser(req.message)
    if browser:
        return {
            "message": browser,
            "tools_used": ["browser"],
            "execution_time": time.time() - start
        }

    msg = req.message.lower()

    if "time" in msg:
        return {"message": datetime.now().strftime("%I:%M %p")}

    if "joke" in msg:
        return {"message": random.choice([
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "I told my PC I need a break — now it won’t stop sending memes!"
        ])}

    # -------------------
    # AI RESPONSE
    # -------------------
    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are JARVIS AI assistant."},
                {"role": "user", "content": req.message}
            ]
        )

        return {
            "message": response.choices[0].message.content,
            "execution_time": time.time() - start
        }

    except Exception as e:
        return {"message": str(e)}

# -------------------
# ROUTES
# -------------------
@app.get("/")
def root():
    return {"status": "JARVIS ONLINE"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# -------------------
# RUN SERVER (LOCAL ONLY)
# -------------------
if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )