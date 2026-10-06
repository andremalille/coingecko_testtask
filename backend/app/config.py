"""Application settings loaded from environment variables."""

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    """Immutable runtime configuration for the backend."""

    api_key: str
    base_url: str
    max_market_pages: int
    detail_concurrency: int
    cache_ttl_seconds: int
    cors_origins: tuple[str, ...]

    @property
    def is_pro(self) -> bool:
        """Return True when the configured base URL points to the Pro API."""
        return "pro-api" in self.base_url


@lru_cache
def get_settings() -> Settings:
    """Build the settings object once from the process environment."""
    origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return Settings(
        api_key=os.getenv("COINGECKO_API_KEY", "").strip(),
        base_url=os.getenv(
            "COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3"
        ).rstrip("/"),
        max_market_pages=int(os.getenv("MAX_MARKET_PAGES", "4")),
        detail_concurrency=int(os.getenv("DETAIL_CONCURRENCY", "3")),
        cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "300")),
        cors_origins=tuple(o.strip() for o in origins.split(",") if o.strip()),
    )
