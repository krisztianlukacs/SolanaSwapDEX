import httpx

from src.common.logging import setup_logger
from src.common.exceptions import JupiterAPIError
from src.config.settings import settings

logger = setup_logger("jupiter")


class JupiterClient:
    """Async HTTP client for Jupiter v6 API."""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.jupiter_api_url
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(30.0),
            )
        return self._client

    async def get(self, path: str, params: dict | None = None) -> dict:
        client = await self._get_client()
        try:
            response = await client.get(path, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info("GET %s -> %d", path, response.status_code)
            return data
        except httpx.HTTPStatusError as e:
            logger.error("Jupiter API error: %s %s -> %d", e.request.method, e.request.url, e.response.status_code)
            raise JupiterAPIError(f"Jupiter API returned {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error("Jupiter API request failed: %s", str(e))
            raise JupiterAPIError(f"Jupiter API request failed: {str(e)}") from e

    async def post(self, path: str, json: dict | None = None) -> dict:
        client = await self._get_client()
        try:
            response = await client.post(path, json=json)
            response.raise_for_status()
            data = response.json()
            logger.info("POST %s -> %d", path, response.status_code)
            return data
        except httpx.HTTPStatusError as e:
            logger.error("Jupiter API error: %s %s -> %d", e.request.method, e.request.url, e.response.status_code)
            raise JupiterAPIError(f"Jupiter API returned {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error("Jupiter API request failed: %s", str(e))
            raise JupiterAPIError(f"Jupiter API request failed: {str(e)}") from e

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
