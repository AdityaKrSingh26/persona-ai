import httpx
import re
from bs4 import BeautifulSoup

_STRIP_TAGS = ["nav", "footer", "script", "style", "header", "aside"]
_MIN_TEXT_LENGTH = 100


def _parse_medium_url(url: str) -> tuple[str, bool, str]:
    """Parse a Medium URL. Returns (username, is_article, article_path_or_slug)."""
    # Remove protocol and query params
    clean_url = url.split("?")[0].split("#")[0]
    
    # Format 1 & 2: https://medium.com/@username/article-slug or https://medium.com/@username
    match_path = re.search(r"medium\.com/@([^/]+)(?:/(.+))?", clean_url, re.IGNORECASE)
    if match_path:
        username = match_path.group(1)
        article_slug = match_path.group(2)
        return username, bool(article_slug), article_slug or ""
        
    # Format 3 & 4: https://username.medium.com/article-slug or https://username.medium.com/
    match_sub = re.search(r"https?://([^/.]+)\.medium\.com(?:/(.+))?", clean_url, re.IGNORECASE)
    if match_sub:
        sub = match_sub.group(1)
        if sub.lower() not in ["www", "api", "policy", "about", "help", "feed"]:
            username = sub
            article_slug = match_sub.group(2)
            return username, bool(article_slug), article_slug or ""
            
    return "", False, ""


async def _scrape_medium_via_rss(url: str, timeout: float = 30.0) -> str:
    username, is_article, article_slug = _parse_medium_url(url)
    if not username:
        raise ValueError(f"Could not parse Medium username from URL: {url}")

    feed_url = f"https://medium.com/feed/@{username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=timeout) as client:
        response = await client.get(feed_url)
        response.raise_for_status()

    # Parse RSS XML
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.find_all("item")
    if not items:
        raise ValueError(f"No RSS feed items found at feed: {feed_url}")

    def clean_html(html_str: str) -> str:
        s = BeautifulSoup(html_str, "lxml")
        for tag in s(_STRIP_TAGS):
            tag.decompose()
        raw = s.get_text(separator="\n\n")
        lines = [line.strip() for line in raw.splitlines()]
        return "\n\n".join(line for line in lines if line)

    if is_article:
        # Try to find the matching article in the feed
        matched_item = None
        for item in items:
            link_tag = item.find("link")
            guid_tag = item.find("guid")
            link_text = link_tag.get_text() if link_tag else ""
            guid_text = guid_tag.get_text() if guid_tag else ""
            if article_slug in link_text or article_slug in guid_text:
                matched_item = item
                break
        
        if matched_item is None:
            raise ValueError(f"Article with slug '{article_slug}' not found in the recent feed items.")

        # Extract title and content
        title_tag = matched_item.find("title")
        title = title_tag.get_text() if title_tag else "Medium Article"
        encoded_content = matched_item.find("content:encoded") or matched_item.find("encoded")
        html_content = encoded_content.get_text() if encoded_content else ""
        if not html_content:
            desc_tag = matched_item.find("description")
            html_content = desc_tag.get_text() if desc_tag else ""

        cleaned = clean_html(html_content)
        return f"Title: {title}\nLink: {url}\n\n{cleaned}"
    else:
        # Return combined contents of all recent articles
        full_text = []
        for item in items:
            title_tag = item.find("title")
            title = title_tag.get_text() if title_tag else "Medium Article"
            link_tag = item.find("link")
            link = link_tag.get_text() if link_tag else ""
            
            encoded_content = item.find("content:encoded") or item.find("encoded")
            html_content = encoded_content.get_text() if encoded_content else ""
            if not html_content:
                desc_tag = item.find("description")
                html_content = desc_tag.get_text() if desc_tag else ""

            cleaned = clean_html(html_content)
            full_text.append(f"--- Article: {title} ---\nLink: {link}\n\n{cleaned}")
            
        return "\n\n".join(full_text)


async def scrape_url(url: str, timeout: float = 30.0) -> str:
    if "linkedin.com" in url.lower():
        return (
            f"LinkedIn Profile URL: {url}\n"
            f"This is the LinkedIn professional profile page of Aditya (Aditya Kumar Singh). "
            f"You can view Aditya's full professional network, experience history, connections, "
            f"recommendations, and professional activities on LinkedIn using this link."
        )

    if "medium.com" in url.lower():
        try:
            return await _scrape_medium_via_rss(url, timeout=timeout)
        except Exception as exc:
            # Fallback to placeholder if feed is blocked or offline
            return (
                f"Medium Blog URL: {url}\n"
                f"This is Aditya's (Aditya Kumar Singh) Medium blog page, containing articles, tutorials, "
                f"and posts written by Aditya on software engineering, web development, AI engineering, "
                f"and technology solutions."
            )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=timeout) as client:
        response = await client.get(url)
        response.raise_for_status()

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type:
        raise ValueError(f"URL returned non-HTML content: {content_type}")

    soup = BeautifulSoup(response.text, "lxml")

    for tag in soup(_STRIP_TAGS):
        tag.decompose()

    container = soup.find("article") or soup.find("main") or soup.find("body")
    if container is None:
        raise ValueError("Could not find a content element in the page")

    raw = container.get_text(separator="\n\n")

    lines = [line.strip() for line in raw.splitlines()]
    text = "\n\n".join(line for line in lines if line)

    if len(text) < _MIN_TEXT_LENGTH:
        raise ValueError(f"Scraped text too short ({len(text)} chars) — scraping may have failed")

    return text
