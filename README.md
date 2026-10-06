# Crypto Screener

FastAPI backend plus React (Vite) frontend that screens CoinGecko projects.

## Project structure

```
.
├── README.md
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── pytest.ini
│   ├── app/
│   │   ├── main.py        # FastAPI app, routes, CORS
│   │   ├── config.py      # Environment-based settings
│   │   ├── coingecko.py   # Async CoinGecko client with retries
│   │   ├── filters.py     # Pure filtering rules
│   │   ├── service.py     # Orchestration and in-memory cache
│   │   └── schemas.py     # Response models
│   └── tests/test_filters.py
└── frontend/
    ├── package.json
    ├── vite.config.js     # Dev proxy: /api -> http://localhost:8000
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── api.js
        ├── styles.css
        ├── components/{Filters,ProjectTable}.jsx
        └── utils/{filterSort,format}.js
```

## Setup

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # optionally add COINGECKO_API_KEY
uvicorn app.main:app --reload --env-file .env
pytest                        # run unit tests
```

API: `GET http://localhost:8000/api/projects` (add `?refresh=true` to bypass the cache).
Interactive docs: `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev                   # http://localhost:5173
```

## How filtering works

1. **Stage 1** (`/coins/markets`, bulk, 250 coins per page): market cap > 0,
   max supply == total supply, FDV < $100M, 24h volume > $50k.
2. **Stage 2** (`/coins/{id}`, only for stage 1 survivors): `preview_listing == true`
   and TVL (`market_data.total_value_locked.usd`) > $50k.

The result is cached in memory (default 5 minutes).

## Assumptions

- Only the top `MAX_MARKET_PAGES * 250` coins by market cap are scanned (default 1,000),
  because the free API is rate limited and has no server-side filtering.
- Coins with a missing (null) max supply, total supply, FDV or TVL are excluded.
- "Max supply equals total supply" requires both to be known and positive.
- `preview_listing` and TVL are read from the coin detail endpoint; if CoinGecko
  does not expose them for your plan, the list may be empty.
- All thresholds are strict (`>` / `<`) and in USD.
- The frontend FDV filter, search (name or symbol) and sorting run client-side.

## Next steps

- Persist the cache (Redis) and refresh it with a background job.
- Server-side query params for search, sort and FDV filter plus pagination.
- Frontend tests (Vitest) and backend integration tests with a mocked CoinGecko.
- Docker Compose for one-command startup.