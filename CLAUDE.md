# doge-predict-frontend-admin

## Project Overview

This is the **admin frontend** for the Doge Predict project — a Hugo-based site that lets authorized users browse and manage crypto betting data via a Firebase-authenticated UI.

The goal of this project is to track crypto price data, betting market odds, and backtest strategies to find profitable betting opportunities on crypto prediction markets.

## Repository Structure

This is a **four-repo project**. All repos are siblings under the same parent directory:

```
FutureGadgetPolyLabs/
├── doge-predict-frontend-admin/    ← Admin frontend — Hugo, Firebase auth (this repo)
├── doge-predict-backend/           ← Backend — REST API + scheduled Cloud Run jobs
├── doge-predict-frontend-public/   ← Public frontend — read-only crypto data products
└── doge-predict-data/              ← Data repo — JSON files auto-updated by the backend
```

| Repo | Role |
|------|------|
| `doge-predict-frontend-admin` | Admin frontend — authenticated CRUD UI (this repo) |
| `doge-predict-backend` | REST API microservice + scheduled jobs for crypto data |
| `doge-predict-frontend-public` | Public frontend — read-only crypto data products |
| `doge-predict-data` | Static JSON data files committed by the backend |

## Architecture

### This Repo — Admin Frontend
- **Framework:** [Hugo](https://gohugo.io/) — static site generator with Go templates
- **Theme:** Custom theme (`themes/admin/`) — minimal Bootstrap 5 layout
- **Auth:** Firebase Authentication. Users must sign in before the UI sends any write requests.
- **Data sources:** The admin frontend can read data three ways:
  1. JSON files from the data GitHub repo (primary)
  2. JSON files from a GCS bucket (fallback)
  3. Live API calls to the backend (for writes and immediate reads)
- **Backend communication:** All write requests include a Firebase ID token as `Authorization: Bearer <token>`. The `api()` helper in `static/js/api.js` handles token attachment automatically.

### Admin Sections
- **Tokens** — Manage tracked crypto tokens (BTC, ETH, DOGE, etc.)
- **Markets** — Browse and manage crypto betting markets (Polymarket, Kalshi, etc.)
- **Snapshots** — View price/odds snapshots taken by the backend
- **Strategies** — Define and manage betting strategies
- **Backtests** — Run and review backtests of strategies against historical data
- **Debug** — Health checks, data freshness, manual job triggers

### Backend
Two concerns in one repo:
1. **API microservice** — REST API consumed by this admin frontend; validates Firebase tokens; reads/writes BigQuery; updates GCS and the data repo
2. **Scheduled jobs** — Cloud Run Jobs that run on a schedule to fetch crypto prices, market odds, and sync data

### Public Frontend
- Read-only, no Firebase auth
- Displays crypto analytics, strategy performance, and market insights for the public
- Reads from the data repo or GCS only — never calls the write API

### Data Repo
- Plain JSON files committed by the backend (API-triggered or scheduled)
- Do not manually edit; the backend owns writes here

## GCP Infrastructure

| Resource | Value | Details |
|----------|-------|---------|
| GCP project | `fg-polylabs` | Shared project for all FG-PolyLabs projects |
| Cloud Run service | `doge-predict-api`, `us-central1` | REST API |
| Cloud Run job | `doge-predict-sync`, `us-central1` | Scheduled crypto data sync |
| GCS bucket | `fg-polylabs-doge-predict-data` | Exported JSON snapshots |
| BigQuery dataset | `doge_predict` | Source of truth |
| Firebase project | `fg-polylabs` | Auth provider (shared) |

## Key Files (This Repo)

| Path | Purpose |
|------|---------|
| `hugo.toml` | Hugo config — `params.backendURL` sets the API base |
| `themes/admin/layouts/` | Hugo templates (baseof, list, index) |
| `themes/admin/layouts/partials/` | head, navbar, footer, scripts partials |
| `static/js/firebase-init.js` | Firebase app init + global `authSignOut()` |
| `static/js/api.js` | Authenticated `api(method, path, body)` helper |
| `static/js/app.js` | Global `showToast()` utility |
| `static/js/data-loader.js` | `loadJsonData(filename)` — GitHub-first, GCS-fallback data fetching |
| `static/css/app.css` | Minimal style overrides on top of Bootstrap 5 |
| `mcp/bq_server.py` | MCP server for BigQuery read-only access |
| `content/tokens/_index.md` | Tracked tokens section |
| `content/markets/_index.md` | Betting markets section |
| `content/snapshots/_index.md` | Price snapshots section |
| `content/strategies/_index.md` | Betting strategies section |
| `content/backtests/_index.md` | Backtests section |
| `.env.example` | Template for Firebase + backend env vars |

## Auth Flow

1. User lands on the site and signs in via Firebase Auth (Google sign-in).
2. Firebase issues an ID token.
3. The frontend attaches the token as `Authorization: Bearer <token>` on all backend requests.
4. The backend validates the token via the Firebase Admin SDK before processing write operations.
5. Access is restricted to an allowlist of authorized emails (`ALLOWED_EMAILS`).

**Never hardcode Firebase credentials** — they belong in `.env` (gitignored).

## Development Notes

- Hugo config lives in `hugo.toml`
- Firebase config goes in `.env` — never commit this file (already in `.gitignore`)
- Environment variables are injected as `HUGO_PARAMS_*` and map to `.Site.Params.*` in templates
- To add a new CRUD section: create `content/<section>/_index.md`, add a nav link in `navbar.html`, and optionally add `themes/admin/layouts/<section>/list.html`

## Running the Dev Server

**Always** source `.env` first — Hugo does not auto-read `.env` files:

```bash
set -a && source .env && set +a && hugo server
```

## Cross-Repo Coordination Rules

1. **New API endpoint:** implement the handler in the backend AND wire up the `api()` call here.
2. **New data field:** update the BigQuery schema in the backend, the GCS/JSON output shape, the data repo's JSON structure, and both frontends that consume it.
3. **Scheduled job changes:** edit the job code in the backend repo; deploys as a separate Cloud Run Job.
4. **Public frontend data change:** if the data shape changes, update the public frontend to match.
5. **Commit separately** in each affected repo with matching/linked commit messages.
6. **Never hardcode Firebase credentials** — use environment variables.

## Custom Agents

A `full-stack` sub-agent is defined in `.claude/agents/full-stack.md`. It checks all four sibling repos and has full context on every repo's role, data flow, and GCP infrastructure.
