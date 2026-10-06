"""Pydantic models describing the public REST API responses."""

from datetime import datetime

from pydantic import BaseModel


class Project(BaseModel):
    """A single cryptocurrency project that passed the screening filters."""

    id: str
    symbol: str
    name: str
    image: str | None = None
    market_cap: float
    fdv: float
    total_volume_24h: float
    tvl: float
    max_supply: float
    total_supply: float
    preview_listing: bool = False
    current_price: float | None = None
    market_cap_rank: int | None = None


class ProjectListResponse(BaseModel):
    """Envelope returned by GET /api/projects."""

    count: int
    generated_at: datetime
    cached: bool
    projects: list[Project]
