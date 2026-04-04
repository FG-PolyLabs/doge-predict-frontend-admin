# Doge Predict — Project TODO

Last updated: 2026-04-03

## Setup & Infrastructure

- [x] Create all four GitHub repos (frontend-admin, backend, data, frontend-public)
- [x] Scaffold admin frontend with crypto sections (Tokens, Markets, Snapshots, Strategies, Backtests, Debug)
- [x] Scaffold backend (Flask API + Cloud Run jobs)
- [x] Scaffold data repo (empty JSON files)
- [x] Scaffold public frontend (Hugo, read-only)
- [x] Create MCP server for BigQuery (`mcp/bq_server.py`)
- [x] Set up Firebase (reusing `collection-showcase-auth`)
- [x] Create `.env` file with Firebase credentials
- [x] Set up GitHub Actions secrets/variables for admin frontend
- [x] Create GCS bucket `fg-polylabs-doge-predict-data` (public, CORS enabled)
- [x] Create BigQuery dataset `doge_predict` with `tracked_markets` and `market_snapshots` tables
- [ ] Create a `GITHUB_TOKEN` (fine-grained PAT) for the backend to commit to the data repo
- [ ] Set up Cloud Run service `doge-predict-api`
- [ ] Set up Cloud Run job `doge-predict-sync`
- [ ] Configure Cloud Scheduler (every 5-15 min for market sync)
- [ ] Enable GitHub Pages for both frontends
- [ ] Set up GitHub Actions secrets for backend repo (WIF_PROVIDER, WIF_SERVICE_ACCOUNT)

## Phase 1: Polymarket Crypto Markets — DONE (core), remaining items below

**What's working:**
- [x] Polymarket client (`polymarket_client.py`) — Gamma API + CLOB API
- [x] Market discovery via slug pattern `{ticker}-updown-{interval}-{timestamp}`
- [x] 7 tickers: BTC, ETH, DOGE, SOL, XRP, BNB, HYPE
- [x] 2 intervals: 5m, 15m
- [x] Orderbook data: best bid/ask, spread, bid/ask depth (top 10 levels)
- [x] Price history fetching with 15-min rounded timestamps
- [x] `sync_markets.py` job — discover + fetch + MERGE into BigQuery (idempotent)
- [x] `export_data.py` — BQ → JSON → GCS (+ GitHub when token is set)
- [x] BigQuery schemas: `tracked_markets`, `market_snapshots` (partitioned, clustered)
- [x] First live sync: 86 markets, 221 snapshots in BQ
- [x] GCS export: `tracked_markets.json`, `market_snapshots.json` live on bucket
- [x] Markets admin page with Chart.js price history and orderbook stats

**Remaining Phase 1:**
- [ ] Set `GITHUB_TOKEN` in backend `.env` so export pushes to data repo
- [ ] Deploy backend to Cloud Run
- [ ] Set up Cloud Scheduler to run `sync_markets` every 5 min
- [ ] Backend API endpoints:
  - [ ] `GET /markets` — list tracked markets with current odds
  - [ ] `GET /markets/<slug>/snapshots` — time-series data for a market
  - [ ] `POST /markets/discover` — trigger market discovery
  - [ ] `POST /sync/markets` — trigger sync from admin UI

## Phase 2: Token Price Data

Add underlying crypto prices to correlate with Polymarket odds:

- [ ] Implement CoinGecko price fetching (`jobs/sync_prices.py`)
  - [ ] `/simple/price` for current prices
  - [ ] `/coins/{id}/market_chart` for historical data
- [ ] `tracked_tokens` BQ table + `price_snapshots` BQ table
- [ ] Sync job running hourly
- [ ] Correlate token prices with Polymarket odds for strategy signals
- [ ] Display price charts alongside market odds in admin frontend

## Phase 3: Strategy & Backtesting

- [ ] Design strategy schema (parameters, entry/exit rules)
- [ ] Strategy CRUD API endpoints
- [ ] Backtesting engine
  - [ ] Load historical snapshots + price data from BQ
  - [ ] Simulate entries at best_ask, exits at best_bid (realistic spread)
  - [ ] PnL, Sharpe, max drawdown, win rate
- [ ] Backtest API endpoints
- [ ] Results export to data repo

## Admin Frontend (remaining pages)

- [ ] Snapshots page — filterable snapshot browser
- [ ] Strategies page — create/edit strategy definitions
- [ ] Backtests page — trigger backtests, view results with charts
- [ ] Health check dashboard on debug page (data freshness, job status)

## Public Frontend

- [ ] Token price charts
- [ ] Market overview (trending markets, best odds)
- [ ] Strategy leaderboard (public backtest results)
- [ ] Landing page design
