from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import webbrowser
import os
from openai import OpenAI
from datetime import datetime
<<<<<<< HEAD
import re
import time
import random

app = FastAPI(title="JARVIS AI Assistant")

# CORS - Allow frontend to connect
=======
import time
import random
from dotenv import load_dotenv

# -------------------
# LOAD ENV VARIABLES
# -------------------
load_dotenv(dotenv_path="D:/jarvis_bot/.env")

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise Exception("❌ OPENROUTER_API_KEY not found in .env file")

# -------------------
# OPENROUTER CLIENT
# -------------------
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

# -------------------
# FASTAPI APP
# -------------------
app = FastAPI(title="JARVIS AI Assistant")

>>>>>>> d4f69ff (Initial commit - JARVIS AI Assistant)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
=======
# -------------------
# REQUEST MODEL
# -------------------
>>>>>>> d4f69ff (Initial commit - JARVIS AI Assistant)
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    user_id: Optional[str] = "user1"

<<<<<<< HEAD
# Initialize OpenRouter client
api_key = os.getenv("OPENROUTER_API_KEY")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

def handle_browser_command(message: str) -> str:
=======
# -------------------
# BROWSER COMMANDS
# -------------------
def handle_browser_command(message: str):
>>>>>>> d4f69ff (Initial commit - JARVIS AI Assistant)
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
<<<<<<< HEAD
            return f"Opening {site.title()} for you! 🚀"
=======
            return f"Opening {site.title()} 🚀"
>>>>>>> d4f69ff (Initial commit - JARVIS AI Assistant)

    if "search" in msg:
        query = msg.replace("search", "").replace("for", "").strip()
        if query:
<<<<<<< HEAD
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return f"Searching for '{query}'... 🔍"

    return None


=======
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            return f"Searching for: {query} 🔍"

    return None

# -------------------
# CHAT API
# -------------------
>>>>>>> d4f69ff (Initial commit - JARVIS AI Assistant)
@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    start = time.time()

<<<<<<< HEAD
    # Browser commands
=======
    # Browser tool
>>>>>>> d4f69ff (Initial commit - JARVIS AI Assistant)
    browser_response = handle_browser_command(request.message)
    if browser_response:
        return {
            "message": browser_response,
            "session_id": request.session_id,
<<<<<<< HEAD
            "message_id": 1,
            "tokens_used": 0,
=======
>>>>>>> d4f69ff (Initial commit - JARVIS AI Assistant)
            "tools_used": ["browser"],
            "execution_time": time.time() - start
        }

<<<<<<< HEAD
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
=======
    msg = request.message.lower()

    # Simple logic responses
    if "capital of pakistan" in msg:
        return {"message": "Islamabad is the capital of Pakistan."}

    if "time" in msg:
        return {"message": f"Current time: {datetime.now().strftime('%I:%M %p')}"}

    if "joke" in msg:
        jokes = [
            "Why don’t scientists trust atoms? Because they make up everything!",
            "Why did the computer get cold? It left its Windows open!",
            "Why do programmers prefer dark mode? Because light attracts bugs!"
        ]
        return {"message": random.choice(jokes)}

    # -------------------
    # AI RESPONSE (OPENROUTER)
    # -------------------
>>>>>>> d4f69ff (Initial commit - JARVIS AI Assistant)
    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
<<<<<<< HEAD
                {"role": "system", "content": "You are JARVIS, a helpful AI assistant. Answer clearly and concisely."},
=======
                {
                    "role": "system",
                    "content": "You are JARVIS, a helpful AI assistant. Be concise and smart."
                },
>>>>>>> d4f69ff (Initial commit - JARVIS AI Assistant)
                {"role": "user", "content": request.message}
            ],
            temperature=0.7,
            max_tokens=500
        )

<<<<<<< HEAD
        ai_message = response.choices[0].message.content
        tokens = getattr(response.usage, "total_tokens", 100)

        return {
            "message": ai_message,
            "session_id": request.session_id,
            "message_id": 1,
            "tokens_used": tokens,
=======
        return {
            "message": response.choices[0].message.content,
>>>>>>> d4f69ff (Initial commit - JARVIS AI Assistant)
            "tools_used": ["ai"],
            "execution_time": time.time() - start
        }

    except Exception as e:
<<<<<<< HEAD
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
=======
        return {"message": f"Error: {str(e)}"}

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
# RUN SERVER
# -------------------
if __name__ == "__main__":
    print("🤖 JARVIS AI STARTING...")

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True
    )
>>>>>>> d4f69ff (Initial commit - JARVIS AI Assistant)
