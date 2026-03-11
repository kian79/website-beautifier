# Beautify

A local demo tool that takes a URL, fetches the website, sends its HTML to GPT-4o for a UI redesign, and serves the beautified version on localhost.

## Prerequisites

- Python 3.11+
- An OpenAI API key with access to GPT-4o

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OpenAI API key
uvicorn main:app --reload
```

Open http://localhost:8000 in your browser.

## How it works

1. Paste a URL into the input field
2. The backend fetches and cleans the page HTML (strips scripts, styles, tracking)
3. The cleaned HTML is sent to GPT-4o with a redesign prompt
4. GPT-4o returns a self-contained HTML file with modern styling
5. The redesigned page is served at a unique preview URL

## Known limitations

- Works best with simple pages (landing pages, blogs, portfolios)
- Images may not load if the original site blocks hotlinking
- JavaScript-rendered content (SPAs) won't be captured — only the initial HTML
- All previews are stored in memory and lost on server restart
- Very large pages are truncated to keep token usage reasonable
