from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import webbrowser
import os
from openai import OpenAI
from datetime import datetime
import re
import time
import random

app = FastAPI(title="JARVIS AI Assistant")

# CORS - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    user_id: Optional[str] = "user1"

# Initialize OpenRouter client
api_key = os.getenv("OPENROUTER_API_KEY")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

def handle_browser_command(message: str) -> str:
    msg = message.lower()

    websites = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "github": "https://github.com",
        "reddit": "https://reddit.com",
        "twitter": "https://twitter.com",
        "facebook": "https://facebook.com",
        "instagram": "https://instagram.com",
        "linkedin": "https://linkedin.com",
        "amazon": "https://amazon.com",
        "netflix": "https://netflix.com",
        "spotify": "https://spotify.com",
    }

    for site, url in websites.items():
        if f"open {site}" in msg:
            webbrowser.open(url)
            return f"Opening {site.title()} for you! 🚀"

    if "search" in msg:
        query = msg.replace("search", "").replace("for", "").strip()
        if query:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return f"Searching for '{query}'... 🔍"

    return None


@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    start = time.time()

    # Browser commands
    browser_response = handle_browser_command(request.message)
    if browser_response:
        return {
            "message": browser_response,
            "session_id": request.session_id,
            "message_id": 1,
            "tokens_used": 0,
            "tools_used": ["browser"],
            "execution_time": time.time() - start
        }

    msg_lower = request.message.lower()

    # Simple responses
    if "capital of pakistan" in msg_lower:
        return {
            "message": "The capital of Pakistan is Islamabad.",
            "session_id": request.session_id,
            "message_id": 1,
            "tokens_used": 50,
            "tools_used": [],
            "execution_time": time.time() - start
        }

    if "time" in msg_lower:
        return {
            "message": f"The current time is {datetime.now().strftime('%I:%M %p')}",
            "session_id": request.session_id,
            "message_id": 1,
            "tokens_used": 50,
            "tools_used": [],
            "execution_time": time.time() - start
        }

    if "joke" in msg_lower:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you call a fake noodle? An impasta!",
            "Why did the scarecrow win an award? He was outstanding in his field!"
        ]
        return {
            "message": random.choice(jokes),
            "session_id": request.session_id,
            "message_id": 1,
            "tokens_used": 50,
            "tools_used": [],
            "execution_time": time.time() - start
        }

    # AI response (OpenRouter)
    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are JARVIS, a helpful AI assistant. Answer clearly and concisely."},
                {"role": "user", "content": request.message}
            ],
            temperature=0.7,
            max_tokens=500
        )

        ai_message = response.choices[0].message.content
        tokens = getattr(response.usage, "total_tokens", 100)

        return {
            "message": ai_message,
            "session_id": request.session_id,
            "message_id": 1,
            "tokens_used": tokens,
            "tools_used": ["ai"],
            "execution_time": time.time() - start
        }

    except Exception as e:
        return {
            "message": f"Error: {str(e)}",
            "session_id": request.session_id,
            "message_id": 0,
            "tokens_used": 0,
            "tools_used": [],
            "execution_time": time.time() - start
        }


@app.get("/")
async def root():
    return {"name": "JARVIS AI Assistant", "status": "online"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# ✅ FIXED ENTRY POINT (IMPORTANT)
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🤖 JARVIS AI Assistant Starting...")
    print("=" * 50)
    print("📍 Server: http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("🌐 Try: 'open YouTube', 'what is the capital of Pakistan'")
    print("=" * 50 + "\n")

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)