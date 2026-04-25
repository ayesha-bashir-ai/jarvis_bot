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

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_TEXT_CHARS = 20000  # cap text fed into the LLM
TEXT_EXTENSIONS = {
    ".txt", ".md", ".csv", ".tsv", ".json", ".yaml", ".yml", ".xml",
    ".html", ".htm", ".css", ".js", ".ts", ".jsx", ".tsx", ".py",
    ".rb", ".go", ".rs", ".java", ".c", ".cpp", ".h", ".sh", ".log",
    ".ini", ".toml", ".env",
}

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


# ---------- NEW: file upload endpoint ----------
def _safe_filename(name: str) -> str:
    name = os.path.basename(name or "upload")
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    return name[:120] or "upload"


@app.post("/api/v1/upload")
async def upload(
    file: UploadFile = File(...),
    message: str = Form(""),
    session_id: str = Form("default"),
):
    start = time.time()

    contents = await file.read()
    size = len(contents)
    if size == 0:
        return {"message": "The uploaded file was empty.", "error": "empty_file"}
    if size > MAX_UPLOAD_BYTES:
        return {
            "message": f"File is too large. Maximum size is {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.",
            "error": "file_too_large",
        }

    safe_session = re.sub(r"[^A-Za-z0-9._-]+", "_", session_id or "default")[:64] or "default"
    session_dir = os.path.join(UPLOAD_DIR, safe_session)
    os.makedirs(session_dir, exist_ok=True)

    safe_name = _safe_filename(file.filename or "upload")
    stamped_name = f"{int(time.time() * 1000)}_{safe_name}"
    saved_path = os.path.join(session_dir, stamped_name)
    with open(saved_path, "wb") as f:
        f.write(contents)

    mime = file.content_type or mimetypes.guess_type(safe_name)[0] or "application/octet-stream"
    ext = os.path.splitext(safe_name)[1].lower()

    user_note = (message or "").strip()
    size_kb = round(size / 1024, 1)
    base_ack = f"Got your file: {safe_name} ({size_kb} KB, {mime})."

    is_image = mime.startswith("image/")
    is_text = mime.startswith("text/") or ext in TEXT_EXTENSIONS

    # No AI configured -> just acknowledge.
    if client is None:
        kind_msg = ""
        if is_image:
            kind_msg = " I can describe images once an AI key is configured."
        elif is_text:
            try:
                preview = contents.decode("utf-8", errors="replace")[:300]
                kind_msg = f"\n\nPreview:\n{preview}"
            except Exception:
                kind_msg = ""
        return {
            "message": base_ack + kind_msg + " (AI is offline; set OPENROUTER_API_KEY to enable analysis.)",
            "filename": safe_name,
            "size": size,
            "mime": mime,
        }

    try:
        if is_image:
            b64 = base64.b64encode(contents).decode("ascii")
            data_url = f"data:{mime};base64,{b64}"
            prompt_text = user_note or "Describe this image in detail."
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are JARVIS, a helpful AI assistant."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {"type": "image_url", "image_url": {"url": data_url}},
                        ],
                    },
                ],
            )
            return {
                "message": response.choices[0].message.content,
                "filename": safe_name,
                "size": size,
                "mime": mime,
                "execution_time": round(time.time() - start, 2),
            }

        if is_text:
            try:
                text = contents.decode("utf-8", errors="replace")
            except Exception:
                text = ""
            truncated = len(text) > MAX_TEXT_CHARS
            text = text[:MAX_TEXT_CHARS]
            prompt_text = (
                user_note
                or "Summarize this file and point out anything important."
            )
            note = " (file was truncated for analysis)" if truncated else ""
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are JARVIS, a helpful AI assistant."},
                    {
                        "role": "user",
                        "content": (
                            f"{prompt_text}{note}\n\n"
                            f"--- File: {safe_name} ---\n{text}\n--- end of file ---"
                        ),
                    },
                ],
            )
            return {
                "message": response.choices[0].message.content,
                "filename": safe_name,
                "size": size,
                "mime": mime,
                "execution_time": round(time.time() - start, 2),
            }

        return {
            "message": base_ack + " I saved it, but I can't read this file type yet (only images and text-based files are analyzed).",
            "filename": safe_name,
            "size": size,
            "mime": mime,
        }

    except Exception as e:
        return {
            "message": "I saved your file but ran into an error while analyzing it.",
            "filename": safe_name,
            "size": size,
            "mime": mime,
            "error": str(e),
        }


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
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
