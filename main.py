import os
import re
import time
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from openai import AsyncOpenAI
from pydantic import BaseModel

from cleaner import fetch_and_clean
from prompt import SYSTEM_PROMPT, build_user_prompt

load_dotenv()

app = FastAPI(title="Beautify")
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# In-memory preview storage with a max cap to prevent unbounded growth
MAX_PREVIEWS = 100
previews: dict[str, dict] = {}


class BeautifyRequest(BaseModel):
    url: str
    color_palette: str | None = None
    instructions: str | None = None


class BeautifyResponse(BaseModel):
    preview_url: str
    id: str


def strip_code_fences(text: str) -> str:
    """Remove markdown code fences that GPT sometimes wraps around HTML."""
    text = text.strip()
    text = re.sub(r"^```(?:html)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


def _evict_oldest():
    """Remove the oldest preview if we've exceeded the cap."""
    while len(previews) > MAX_PREVIEWS:
        oldest_key = min(previews, key=lambda k: previews[k]["created_at"])
        del previews[oldest_key]


@app.get("/")
async def index():
    return FileResponse("static/index.html")


@app.post("/api/beautify", response_model=BeautifyResponse)
async def beautify(req: BeautifyRequest):
    url = req.url.strip()

    # Basic URL validation
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    t0 = time.time()

    # 1. Fetch and clean
    print(f"[beautify] Fetching {url} ...")
    try:
        page_data = await fetch_and_clean(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not fetch URL: {e}")

    cleaned_len = len(page_data["cleaned_html"])
    print(f"[beautify] Fetched & cleaned in {time.time() - t0:.1f}s — {cleaned_len} chars")

    # 2. Call LLM
    user_prompt = build_user_prompt(
        page_data["cleaned_html"],
        page_data["title"],
        page_data["original_url"],
        color_palette=req.color_palette,
        instructions=req.instructions,
    )

    print(f"[beautify] Sending to {MODEL} ({len(user_prompt)} chars prompt) ...")
    t1 = time.time()
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=16000,
            timeout=180.0,
        )
    except Exception as e:
        print(f"[beautify] LLM failed after {time.time() - t1:.1f}s: {e}")
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    raw_html = response.choices[0].message.content
    tokens = response.usage
    print(f"[beautify] LLM responded in {time.time() - t1:.1f}s — "
          f"tokens: {tokens.prompt_tokens} in / {tokens.completion_tokens} out")

    if not raw_html:
        raise HTTPException(status_code=500, detail="LLM returned empty response")

    redesigned_html = strip_code_fences(raw_html)

    # Basic sanity check
    if "<html" not in redesigned_html.lower() and "<!doctype" not in redesigned_html.lower():
        raise HTTPException(status_code=500, detail="LLM did not return valid HTML")

    # 3. Store and return
    preview_id = uuid.uuid4().hex[:8]
    previews[preview_id] = {
        "html": redesigned_html,
        "original_url": url,
        "title": page_data["title"],
        "created_at": time.time(),
    }
    _evict_oldest()

    print(f"[beautify] Done in {time.time() - t0:.1f}s total — /preview/{preview_id}")
    return BeautifyResponse(preview_url=f"/preview/{preview_id}", id=preview_id)


@app.get("/preview/{preview_id}")
async def preview(preview_id: str):
    entry = previews.get(preview_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Preview not found or expired")
    return HTMLResponse(content=entry["html"])


@app.get("/api/history")
async def history():
    """Return list of recent beautifications."""
    items = []
    for pid, entry in sorted(previews.items(), key=lambda x: x[1]["created_at"], reverse=True):
        items.append({
            "id": pid,
            "preview_url": f"/preview/{pid}",
            "original_url": entry["original_url"],
            "title": entry["title"],
        })
    return items
