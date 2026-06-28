import httpx
from bs4 import BeautifulSoup

_STRIP_TAGS = ["nav", "footer", "script", "style", "header", "aside"]
_MIN_TEXT_LENGTH = 100


async def scrape_url(url: str, timeout: float = 30.0) -> str:
    async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
        response = await client.get(url)
        response.raise_for_status()

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type:
        raise ValueError(f"URL returned non-HTML content: {content_type}")

    # lxml is faster than html.parser and handles malformed markup more gracefully
    soup = BeautifulSoup(response.text, "lxml")

    for tag in soup(_STRIP_TAGS):
        tag.decompose()

    # Extract the most content-dense element
    container = soup.find("article") or soup.find("main") or soup.find("body")
    if container is None:
        raise ValueError("Could not find a content element in the page")

    raw = container.get_text(separator="\n\n")

    # Normalize whitespace — collapse blank lines, strip each line
    lines = [line.strip() for line in raw.splitlines()]
    text = "\n\n".join(line for line in lines if line)

    if len(text) < _MIN_TEXT_LENGTH:
        raise ValueError(f"Scraped text too short ({len(text)} chars) — scraping may have failed")

    return text
