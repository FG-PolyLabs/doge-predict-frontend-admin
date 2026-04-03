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
- [ ] Create GCS bucket `fg-polylabs-doge-predict-data`
- [ ] Create BigQuery dataset `doge_predict` with tables (see schema section below)
- [ ] Set up Cloud Run service `doge-predict-api`
- [ ] Set up Cloud Run job `doge-predict-sync`
- [ ] Configure Cloud Scheduler for periodic syncs
- [ ] Enable GitHub Pages for both frontends
- [ ] Set up CORS on GCS bucket

## Phase 1: Polymarket Daily/Weekly Crypto Markets (CURRENT PRIORITY)

Track the daily and weekly crypto up-or-down markets on Polymarket.

**Markets to track:**
- Daily crypto markets: `https://polymarket.com/crypto/daily` (e.g. "Will BTC go up today?")
- Weekly crypto markets: `https://polymarket.com/crypto/weekly` (e.g. "Will ETH go up this week?")

**Data pipeline (modeled after cloud-predict-analytics weather app):**

### Backend — Polymarket Client
- [x] Create `app/services/polymarket_client.py` — Gamma API + CLOB API client
  - [x] `get_events(slug)` — fetch events by slug from Gamma API
  - [x] `get_market(market_id)` — fetch single market details
  - [x] `get_price_history(token_id, start_ts, end_ts, fidelity)` — CLOB price history
  - [x] `discover_crypto_daily_markets()` — find active daily crypto markets
  - [x] `discover_crypto_weekly_markets()` — find active weekly crypto markets

### Backend — BigQuery Schemas
- [x] Create `sql/` directory with schema definitions
- [x] `tracked_markets` table — markets being tracked (slug, title, category, platform, token_ids, active)
- [x] `market_snapshots` table — time-series price/odds data (market_id, timestamp, yes_price, no_price, volume, liquidity, spread)
  - Partitioned by `date`, clustered by `market_slug`
  - Composite key: `(market_slug, outcome_tag, timestamp)` for dedup

### Backend — Sync Job
- [x] Implement `jobs/sync_markets.py` — scheduled Polymarket fetcher
  - [x] Discover active daily/weekly crypto markets
  - [x] For each market: fetch price history with configurable fidelity (default 60min)
  - [x] Round timestamps to 15-min boundaries (matching weather app pattern)
  - [x] MERGE into BigQuery (idempotent, no duplicates)
  - [x] Support `--dry-run`, `--fidelity`, `--market-type` flags
- [ ] Implement `jobs/export_data.py` — export BQ → JSON → GCS + GitHub
- [ ] Set up Cloud Scheduler: daily at 01:00 UTC for daily markets, weekly on Monday for weekly

### Backend — API Endpoints
- [ ] `GET /markets` — list tracked markets with current odds
- [ ] `GET /markets/<slug>/snapshots` — time-series snapshot data for a market
- [ ] `GET /markets/<slug>/snapshots-at?ts=` — snapshot closest to timestamp
- [ ] `POST /markets/discover` — trigger market discovery

### Admin Frontend — Markets Page
- [ ] Markets list page with current YES/NO prices
- [ ] Market detail view with price history chart (Chart.js)
- [ ] Source selector (GitHub/GCS/API)

## Phase 2: Token Price Data

After Polymarket tracking is working, add underlying crypto price data:

- [ ] Track actual ticker prices for tokens in tracked markets (BTC, ETH, SOL, etc.)
- [ ] Implement CoinGecko price fetching (`jobs/sync_prices.py`)
  - [ ] `/simple/price` for current prices
  - [ ] `/coins/{id}/market_chart` for historical data
- [ ] `price_snapshots` BQ table — token price time-series
- [ ] Correlate token prices with Polymarket odds for strategy development
- [ ] Display price charts alongside market odds in admin frontend

## Phase 3: Strategy & Backtesting

- [ ] Design strategy schema (what parameters define a strategy?)
- [ ] Strategy CRUD API endpoints
- [ ] Implement backtesting engine
  - [ ] Historical data loading from BQ
  - [ ] Strategy evaluation loop
  - [ ] PnL calculation
  - [ ] Performance metrics (Sharpe, max drawdown, win rate)
- [ ] Backtest API endpoints (trigger, status, results)
- [ ] Backtest results export to data repo

## Admin Frontend (remaining)

- [ ] Snapshots page layout with charts
- [ ] Strategies page layout (create/edit strategies with parameter forms)
- [ ] Backtests page layout (trigger backtests, view results, charts)
- [ ] Add Chart.js for price/performance visualization
- [ ] Health check dashboard on debug page

## Public Frontend

- [ ] Token price charts
- [ ] Market overview (trending markets, best odds)
- [ ] Strategy leaderboard (public backtest results)
- [ ] Landing page design
