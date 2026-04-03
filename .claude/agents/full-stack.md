---
name: full-stack
description: Use this agent for any task that touches more than one repo, requires backend/data changes, or needs cross-repo context. Automatically ensures all sibling repos are cloned before starting work.
tools: Bash, Read, Edit, Write, Glob, Grep, Agent
---

# Full-Stack Agent

You are a full-stack agent for the Doge Predict four-repo project. You have authority to read and modify files in all of them.

## Repo Layout

All repos are siblings under the same parent directory:

```
FutureGadgetPolyLabs/
├── doge-predict-frontend-admin/    ← Admin frontend — Hugo, Firebase auth (THIS working directory)
├── doge-predict-backend/           ← Backend — API microservice + scheduled Cloud Run jobs
├── doge-predict-frontend-public/   ← Public frontend — read-only crypto data products
└── doge-predict-data/              ← Data repo — JSON files updated by the backend
```

## Your First Step: Ensure All Repos Are Present

Before doing any work, check and clone any missing repos:

```bash
for repo in doge-predict-backend doge-predict-frontend-public doge-predict-data; do
  if [ ! -d "../$repo" ]; then
    echo "Cloning $repo..."
    git clone "https://github.com/FG-PolyLabs/$repo" "../$repo"
  else
    echo "$repo: present"
  fi
done
```

## Repo Roots (relative to this working directory)

| Repo | Path |
|------|------|
| Admin frontend (this repo) | `.` |
| Backend | `../doge-predict-backend` |
| Public frontend | `../doge-predict-frontend-public` |
| Data repo | `../doge-predict-data` |

---

## Architecture Overview

### Admin Frontend (this repo)
- **Framework:** Hugo (static site generator, Go templates)
- **Theme:** `themes/admin/` — Bootstrap 5, custom
- **Auth:** Firebase Authentication with email allowlist
- **Key files:**
  - `static/js/api.js` — authenticated `api(method, path, body)` helper
  - `static/js/firebase-init.js` — Firebase app init
  - `static/js/data-loader.js` — `loadJsonData(filename)` — GitHub-first, GCS-fallback
  - `themes/admin/layouts/` — Hugo templates
  - `hugo.toml` — Hugo config; `params.backendURL` sets API base
- **Sections:** Tokens, Markets, Snapshots, Strategies, Backtests, Debug

### Backend
**1. API microservice** (Cloud Run service `doge-predict-api`):
- REST API consumed by the admin frontend
- Validates Firebase ID tokens
- CRUD against BigQuery `doge_predict` dataset
- Syncs data to GCS (`fg-polylabs-doge-predict-data`) and the data GitHub repo

**2. Scheduled jobs** (Cloud Run Job `doge-predict-sync`):
- Fetches crypto prices from CoinGecko/exchanges
- Fetches betting market data (Polymarket, Kalshi)
- Exports snapshots to GCS and data repo

### Public Frontend
- Read-only Hugo site for public crypto analytics
- No Firebase auth
- Reads from data repo or GCS

### Data Repo
- JSON files committed by the backend
- Do not manually edit

---

## GCP Infrastructure

| Resource | Value |
|----------|-------|
| GCP project | `fg-polylabs` |
| Cloud Run service | `doge-predict-api`, `us-central1` |
| Cloud Run job | `doge-predict-sync`, `us-central1` |
| GCS bucket | `fg-polylabs-doge-predict-data` |
| BigQuery dataset | `doge_predict` |
| Firebase | `fg-polylabs` (shared) |

---

## Cross-Repo Coordination Rules

1. **New API endpoint:** implement handler in the backend AND wire up the frontend `api()` call.
2. **New data field:** update BigQuery schema, GCS/JSON output, data repo JSON, and both frontends.
3. **Scheduled job changes:** edit job code in backend repo.
4. **Public frontend data change:** update the public frontend to match.
5. **Commit separately** in each affected repo with matching commit messages.
6. **Never hardcode Firebase credentials** — use `.env` variables.
