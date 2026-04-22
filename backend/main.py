from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import webbrowser
import os
import time
import random
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load env
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise Exception("OPENROUTER_API_KEY not found")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
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

def handle_browser_command(message: str):
    msg = message.lower()

    sites = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "github": "https://github.com",
    }

    for site, url in sites.items():
        if f"open {site}" in msg:
            webbrowser.open(url)
            return f"Opening {site}"

    if "search" in msg:
        query = msg.replace("search", "")
        url = f"https://google.com/search?q={query}"
        webbrowser.open(url)
        return f"Searching {query}"

    return None

@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    start = time.time()

    browser = handle_browser_command(request.message)
    if browser:
        return {"message": browser, "tools_used": ["browser"]}

    if "time" in request.message.lower():
        return {"message": datetime.now().strftime("%I:%M %p")}

    if "joke" in request.message.lower():
        return {"message": random.choice([
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "I told my computer I needed a break, now it won’t stop sending me KitKats!"
        ])}

    try:
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are JARVIS AI assistant."},
                {"role": "user", "content": request.message}
            ]
        )

        return {
            "message": response.choices[0].message.content,
            "execution_time": time.time() - start
        }

    except Exception as e:
        return {"message": str(e)}

@app.get("/")
def root():
    return {"status": "JARVIS ONLINE"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)