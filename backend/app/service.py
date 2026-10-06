"""Screener service: orchestrates CoinGecko calls, filtering and caching."""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any

from .coingecko import CoinGeckoClient
from .config import Settings
from .filters import extract_tvl_usd, passes_market_filters, passes_tvl_filter
from .schemas import Project, ProjectListResponse

logger = logging.getLogger(__name__)


class ScreenerService:
    """Builds the filtered project list and caches it in memory."""

    def __init__(self, client: CoinGeckoClient, settings: Settings) -> None:
        """Create the service."""
        self._client = client
        self._settings = settings
        self._lock = asyncio.Lock()
        self._cached: list[Project] = []
        self._cached_at: float | None = None
        self._generated_at: datetime = datetime.now(timezone.utc)

    def _cache_is_fresh(self) -> bool:
        """Return True when a cached result exists and has not expired."""
        if self._cached_at is None:
            return False
        return time.monotonic() - self._cached_at < self._settings.cache_ttl_seconds

    async def get_projects(
        self, refresh: bool = False, require_preview: bool = True
    ) -> ProjectListResponse:
        """Return the screened projects."""
        async with self._lock:
            from_cache = not refresh and self._cache_is_fresh()
            if not from_cache:
                self._cached = await self._build_projects()
                self._cached_at = time.monotonic()
                self._generated_at = datetime.now(timezone.utc)
            projects = [
                p for p in self._cached if p.preview_listing or not require_preview
            ]
            return ProjectListResponse(
                count=len(projects),
                generated_at=self._generated_at,
                cached=from_cache,
                projects=projects,
            )

    async def _build_projects(self) -> list[Project]:
        """Run both filtering stages against live CoinGecko data."""
        candidates = await self._collect_candidates()
        logger.info("%d candidates passed market-level filters", len(candidates))

        semaphore = asyncio.Semaphore(self._settings.detail_concurrency)

        async def check(coin: dict[str, Any]) -> Project | None:
            async with semaphore:
                detail = await self._client.get_coin_detail(coin["id"])
            if not detail or not passes_tvl_filter(detail):
                return None
            preview = detail.get("preview_listing") is True
            return self._to_project(coin, extract_tvl_usd(detail) or 0.0, preview)

        results = await asyncio.gather(*(check(c) for c in candidates))
        return [p for p in results if p is not None]

    async def _collect_candidates(self) -> list[dict[str, Any]]:
        """Scan market pages and keep rows that pass the market-level filters."""
        candidates: list[dict[str, Any]] = []
        for page in range(1, self._settings.max_market_pages + 1):
            rows = await self._client.get_markets_page(page)
            if not rows:
                break
            candidates.extend(r for r in rows if passes_market_filters(r))
        return candidates

    @staticmethod
    def _to_project(coin: dict[str, Any], tvl: float, preview_listing: bool) -> Project:
        """Convert a ``/coins/markets`` row plus detail data into a ``Project``."""
        return Project(
            id=coin["id"],
            symbol=coin["symbol"],
            name=coin["name"],
            image=coin.get("image"),
            market_cap=coin["market_cap"],
            fdv=coin["fully_diluted_valuation"],
            total_volume_24h=coin["total_volume"],
            tvl=tvl,
            max_supply=coin["max_supply"],
            total_supply=coin["total_supply"],
            preview_listing=preview_listing,
            current_price=coin.get("current_price"),
            market_cap_rank=coin.get("market_cap_rank"),
        )
