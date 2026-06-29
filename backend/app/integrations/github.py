import asyncio
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

_GITHUB_API = "https://api.github.com"


class GitHubClient:
    def __init__(self, token: str, username: str) -> None:
        self._username = username
        self._client = httpx.AsyncClient(
            base_url=_GITHUB_API,
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=10.0,
        )

    async def fetch_repos(
        self,
        query: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        for attempt in range(2):
            try:
                response = await self._client.get(
                    f"/users/{self._username}/repos",
                    # sort=updated puts the most recently active repos first — more useful for the voice tool
                    params={"sort": "updated", "per_page": limit},
                )
                response.raise_for_status()
                break
            except httpx.HTTPStatusError as exc:
                # Only retry on GitHub 5xx — 4xx (bad token, rate limit) should surface immediately
                if exc.response.status_code >= 500 and attempt == 0:
                    await asyncio.sleep(1)
                else:
                    raise

        repos = response.json()

        if query:
            q = query.lower()
            # Client-side filter — GitHub's search API would require a separate endpoint and auth scope
            repos = [
                r for r in repos
                if q in r.get("name", "").lower()
                or q in (r.get("description") or "").lower()
            ]

        return [
            {
                "name": r["name"],
                "description": r.get("description"),
                "url": r["html_url"],
                "language": r.get("language"),
                "stars": r.get("stargazers_count", 0),
                "updated_at": r.get("updated_at"),
            }
            for r in repos
        ]

    async def fetch_profile(self) -> dict:
        for attempt in range(2):
            try:
                response = await self._client.get(f"/users/{self._username}")
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code >= 500 and attempt == 0:
                    await asyncio.sleep(1)
                else:
                    raise
        return {}

    async def aclose(self) -> None:
        await self._client.aclose()
