import httpx


class EmbeddingsClient:
    def __init__(self, api_key: str, endpoint: str) -> None:
        self._client = httpx.AsyncClient(
            base_url=endpoint,
            headers={"Authorization": f"Bearer {api_key}"},
            # 60s because large batches can take several seconds on the free-tier API
            timeout=60.0,
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        response = await self._client.post(
            "/embeddings",
            json={
                "model": "text-embedding-3-small",
                "input": texts,
                # 1536 matches the pgvector column dimension — changing either requires a re-index
                "dimensions": 1536,
            },
        )
        response.raise_for_status()
        data = response.json()["data"]
        # Sort by index to guarantee order matches input
        data.sort(key=lambda item: item["index"])
        return [item["embedding"] for item in data]

    async def aclose(self) -> None:
        await self._client.aclose()
