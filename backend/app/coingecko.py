"""Thin async client for the CoinGecko REST API."""

import asyncio
import logging
import time
from typing import Any

import httpx

from .config import Settings

logger = logging.getLogger(__name__)

MARKETS_PER_PAGE = 250
MAX_RETRIES = 4


class CoinGeckoError(Exception):
    """Raised when CoinGecko cannot be reached or keeps returning errors."""


class CoinGeckoClient:
    """Async wrapper around the CoinGecko endpoints used by the screener."""

    def __init__(
        self, settings: Settings, client: httpx.AsyncClient | None = None
    ) -> None:
        """Create the client."""
        header = "x-cg-pro-api-key" if settings.is_pro else "x-cg-demo-api-key"
        headers = {"accept": "application/json"}
        if settings.api_key:
            headers[header] = settings.api_key
        self._client = client or httpx.AsyncClient(
            base_url=settings.base_url, headers=headers, timeout=30.0
        )
        self._throttle_lock = asyncio.Lock()
        self._last_request = 0.0
        # Demo plan allows ~30 calls/min; keyless access is far stricter.
        self._min_interval = 2.2 if settings.api_key else 6.0

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def _throttle(self) -> None:
        """Space out outgoing requests to stay under the API rate limit."""
        async with self._throttle_lock:
            wait = self._min_interval - (time.monotonic() - self._last_request)
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_request = time.monotonic()

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """GET a path with retries on rate limiting (429) and 5xx errors."""
        delay = 2.0
        last_error = "unknown error"
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                await self._throttle()
                response = await self._client.get(path, params=params)
            except httpx.HTTPError as exc:
                last_error = str(exc)
            else:
                if response.status_code == 200:
                    return response.json()
                if response.status_code == 404:
                    return None
                last_error = f"HTTP {response.status_code}"
                if response.status_code not in (429, 500, 502, 503, 504):
                    break
                retry_after = response.headers.get("retry-after")
                if retry_after and retry_after.isdigit():
                    delay = float(retry_after)
            logger.warning(
                "CoinGecko %s failed (%s), attempt %d", path, last_error, attempt
            )
            await asyncio.sleep(delay)
            delay *= 2
        raise CoinGeckoError(f"CoinGecko request {path} failed: {last_error}")

    async def get_markets_page(self, page: int) -> list[dict[str, Any]]:
        """Fetch one page of coins ordered by market cap (descending)."""
        data = await self._get(
            "/coins/markets",
            {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": MARKETS_PER_PAGE,
                "page": page,
                "sparkline": "false",
            },
        )
        return data or []

    async def get_coin_detail(self, coin_id: str) -> dict[str, Any] | None:
        """Fetch the detail payload of one coin, or None if it does not exist."""
        return await self._get(
            f"/coins/{coin_id}",
            {
                "localization": "false",
                "tickers": "false",
                "community_data": "false",
                "developer_data": "false",
                "sparkline": "false",
            },
        )
