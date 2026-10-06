"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .coingecko import CoinGeckoClient, CoinGeckoError
from .config import get_settings
from .schemas import ProjectListResponse
from .service import ScreenerService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create shared resources on startup and release them on shutdown."""
    settings = get_settings()
    client = CoinGeckoClient(settings)
    app.state.service = ScreenerService(client, settings)
    yield
    await client.aclose()


app = FastAPI(
    title="Crypto Screener API",
    description="Filtered CoinGecko project list for early-stage, low-FDV projects.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(get_settings().cors_origins),
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}


@app.get("/api/projects", response_model=ProjectListResponse)
async def list_projects(
    refresh: bool = Query(False, description="Bypass the in-memory cache."),
    require_preview: bool = Query(
        True,
        description="Keep only coins with preview_listing == true (the task's rule). "
        "Set to false to skip just that rule.",
    ),
) -> ProjectListResponse:
    """Return projects that satisfy the screening criteria."""
    service: ScreenerService = app.state.service
    try:
        return await service.get_projects(
            refresh=refresh, require_preview=require_preview
        )
    except CoinGeckoError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
