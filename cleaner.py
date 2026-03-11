import httpx
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin, urlparse

MAX_CLEANED_LENGTH = 15_000
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Only remove tags that are truly useless for redesign
REMOVE_TAGS = {"script", "noscript", "iframe"}

# Event handlers and tracking attrs — remove these but keep class/id
REMOVE_ATTR_PREFIXES = ("on", "data-tracking", "data-analytics", "data-ad")


async def fetch_and_clean(url: str) -> dict:
    """Fetch a URL and return cleaned HTML suitable for LLM redesign."""
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=15.0,
        headers={"User-Agent": USER_AGENT},
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract title
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else urlparse(url).netloc

    # Remove unwanted tags
    for tag_name in REMOVE_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # Remove HTML comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Remove <style> tags (the LLM will write new CSS) and stylesheet links
    for tag in soup.find_all("style"):
        tag.decompose()
    for link in soup.find_all("link", rel="stylesheet"):
        link.decompose()

    # Remove tracking pixels (1x1 images)
    for img in soup.find_all("img"):
        width = img.get("width", "")
        height = img.get("height", "")
        if width in ("0", "1") or height in ("0", "1"):
            img.decompose()

    # Convert relative URLs to absolute for images and links
    base_url = url
    base_tag = soup.find("base", href=True)
    if base_tag:
        base_url = urljoin(url, base_tag["href"])

    for img in soup.find_all("img", src=True):
        img["src"] = urljoin(base_url, img["src"])
    for a in soup.find_all("a", href=True):
        a["href"] = urljoin(base_url, a["href"])
    for source in soup.find_all("source", srcset=True):
        source["srcset"] = urljoin(base_url, source["srcset"])

    # Strip event-handler and tracking attributes, but keep class/id for context
    for tag in soup.find_all(True):
        attrs_to_remove = [
            attr for attr in tag.attrs
            if any(attr.startswith(p) for p in REMOVE_ATTR_PREFIXES)
            or attr in ("jsaction", "jscontroller", "jsname", "jsmodel")
        ]
        for attr in attrs_to_remove:
            del tag[attr]

    # Collapse truly empty leaf divs/spans (no text, no meaningful children)
    # Work bottom-up to avoid destroying parents of content
    for tag in reversed(soup.find_all(["div", "span"])):
        if not tag.get_text(strip=True) and not tag.find_all(
            ["img", "svg", "a", "input", "button", "form", "video", "picture"]
        ):
            tag.decompose()

    cleaned_html = str(soup)

    # Truncate if too long — keep head + first N body elements
    if len(cleaned_html) > MAX_CLEANED_LENGTH:
        cleaned_html = _truncate_html(soup, MAX_CLEANED_LENGTH)

    return {
        "cleaned_html": cleaned_html,
        "title": title,
        "original_url": url,
    }


def _truncate_html(soup: BeautifulSoup, max_length: int) -> str:
    """Truncate HTML intelligently by keeping head and first body elements."""
    head = soup.find("head")
    body = soup.find("body")

    if not body:
        return str(soup)[:max_length]

    head_html = str(head) if head else ""
    budget = max_length - len(head_html) - len("<html><body></body></html>")

    parts = []
    current_length = 0
    for child in body.children:
        child_str = str(child)
        if current_length + len(child_str) > budget:
            break
        parts.append(child_str)
        current_length += len(child_str)

    body_html = "".join(parts)
    return f"<html>{head_html}<body>{body_html}</body></html>"
