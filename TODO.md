# Doge Predict — Project TODO

Last updated: 2026-04-02

## Setup & Infrastructure

- [x] Create all four GitHub repos (frontend-admin, backend, data, frontend-public)
- [x] Scaffold admin frontend with crypto sections (Tokens, Markets, Snapshots, Strategies, Backtests, Debug)
- [x] Scaffold backend (Flask API + Cloud Run jobs)
- [x] Scaffold data repo (empty JSON files)
- [x] Scaffold public frontend (Hugo, read-only)
- [x] Create MCP server for BigQuery (`mcp/bq_server.py`)
- [ ] Set up Firebase project (or reuse existing `fg-polylabs`)
- [ ] Create `.env` file with actual Firebase credentials
- [ ] Create GCS bucket `fg-polylabs-doge-predict-data`
- [ ] Create BigQuery dataset `doge_predict` with tables:
  - [ ] `tracked_tokens`
  - [ ] `price_snapshots`
  - [ ] `betting_markets`
  - [ ] `market_snapshots`
  - [ ] `strategies`
  - [ ] `backtest_runs`
  - [ ] `backtest_trades`
- [ ] Set up Cloud Run service `doge-predict-api`
- [ ] Set up Cloud Run job `doge-predict-sync`
- [ ] Configure Cloud Scheduler for periodic syncs
- [ ] Set up GitHub Actions secrets/variables for all repos
- [ ] Enable GitHub Pages for both frontends
- [ ] Set up CORS on GCS bucket

## Backend — Data Ingestion

- [ ] Implement CoinGecko price fetching (`jobs/sync_prices.py`)
- [ ] Implement Polymarket data fetching (`jobs/sync_markets.py`)
- [ ] Implement Kalshi data fetching (if applicable)
- [ ] Implement data export pipeline (BQ → JSON → GCS + GitHub)
- [ ] Token CRUD API endpoints (full implementation)
- [ ] Market CRUD API endpoints
- [ ] Snapshot query endpoints (with filters)
- [ ] Health check with data freshness

## Backend — Strategy & Backtesting

- [ ] Design strategy schema (what parameters define a strategy?)
- [ ] Strategy CRUD API endpoints
- [ ] Implement backtesting engine
  - [ ] Historical data loading from BQ
  - [ ] Strategy evaluation loop
  - [ ] PnL calculation
  - [ ] Performance metrics (Sharpe, max drawdown, win rate)
- [ ] Backtest API endpoints (trigger, status, results)
- [ ] Backtest results export to data repo

## Admin Frontend

- [ ] Markets page layout (`themes/admin/layouts/markets/list.html`)
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

## Data Sources to Investigate

- [ ] CoinGecko API — free tier limits, what data is available
- [ ] Polymarket API — market structure, resolution criteria
- [ ] Kalshi API — crypto-related markets
- [ ] Binance API — real-time price data
- [ ] Other prediction markets (Manifold, etc.)

## Questions to Resolve

- What specific crypto tokens to track initially? (BTC, ETH, DOGE, SOL, ...)
- What betting markets are most relevant? (price targets, date-based, etc.)
- What backtesting strategies to implement first? (momentum, mean-reversion, spread-based?)
- How frequently should prices be synced? (hourly? every 15min?)
- What's the initial capital assumption for backtests?
