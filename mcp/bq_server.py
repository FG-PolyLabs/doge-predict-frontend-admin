"""
MCP server for read-only BigQuery access to the doge_predict dataset.

Usage (stdio, for Claude Code):
    python mcp/bq_server.py

Requires:
    pip install mcp google-cloud-bigquery
    gcloud auth application-default login

## Quick Reference

Primary tables for market data:
  - tracked_markets: 7 daily crypto up-or-down markets (BTC, ETH, DOGE, SOL, XRP, BNB, HYPE)
  - market_snapshots_v2: hourly odds snapshots with YES/NO prices + orderbook costs
  - tracked_tokens: the 7 crypto tokens being tracked
  - price_snapshots: hourly CoinGecko price data (90 days backfilled)

Common queries:
  -- Today's BTC market odds over time:
  SELECT measured_at, yes_price, no_price, yes_buy, yes_sell
  FROM doge_predict.market_snapshots_v2
  WHERE ticker = 'btc' AND date = CURRENT_DATE()
  ORDER BY measured_at

  -- Latest odds for all daily markets:
  SELECT ticker, yes_price, no_price, measured_at, expires_at
  FROM doge_predict.market_snapshots_v2
  WHERE category = 'crypto_daily'
  QUALIFY ROW_NUMBER() OVER (PARTITION BY market_slug ORDER BY measured_at DESC) = 1

  -- Correlate BTC price with market odds:
  SELECT s.measured_at, s.yes_price, p.price_usd
  FROM doge_predict.market_snapshots_v2 s
  JOIN doge_predict.price_snapshots p ON s.ticker = p.ticker
    AND TIMESTAMP_TRUNC(s.measured_at, HOUR) = TIMESTAMP_TRUNC(p.timestamp, HOUR)
  WHERE s.ticker = 'btc' AND s.date = CURRENT_DATE()
"""

import json
import re
from google.cloud import bigquery
from mcp.server.fastmcp import FastMCP

PROJECT = "fg-polylabs"
DATASET = "doge_predict"

TABLES = {
    "tracked_markets": (
        "Markets being tracked from polymarket.com/crypto/daily. "
        "7 daily up-or-down markets: BTC, ETH, DOGE, SOL, XRP, BNB, HYPE. "
        "Columns: market_id, slug (e.g. bitcoin-up-or-down-on-april-4-2026), title, "
        "category (crypto_daily|crypto_weekly), platform, yes/no_token_id, active, end_date"
    ),
    "market_snapshots_v2": (
        "PRIMARY table for market odds data. One row per market per measurement time. "
        "Hourly snapshots of YES/NO prices + directional orderbook costs. "
        "Key columns: market_slug, ticker, category, measured_at (when recorded), "
        "expires_at (when market resolves), yes_price, no_price (mid prices 0-1), "
        "yes_buy (cost to buy YES = YES best ask), yes_sell (proceeds selling YES = YES best bid), "
        "no_buy, no_sell (same for NO side), *_depth (bid/ask depth), volume, liquidity. "
        "Partitioned by date, clustered by ticker+category. "
        "Dedup key: (market_slug, measured_at)"
    ),
    "tracked_tokens": (
        "7 crypto tokens: btc, eth, doge, sol, xrp, bnb, hype. "
        "Columns: ticker, coingecko_id, name, active"
    ),
    "price_snapshots": (
        "Hourly CoinGecko price data for all 7 tokens. 90 days backfilled. "
        "Columns: ticker, coingecko_id, date, timestamp, price_usd, market_cap, volume_24h. "
        "Partitioned by date, clustered by ticker"
    ),
    "strategies": (
        "Betting strategy definitions. Types: always_yes, always_no, momentum, contrarian, spread_filter. "
        "Columns: strategy_id, name, strategy_type, params (JSON), tickers, intervals, active"
    ),
    "backtest_runs": (
        "Backtest results. Columns: run_id, strategy_id, strategy_name, start/end_date, "
        "initial/final_capital, total_pnl, total_return, num_trades, win_rate, sharpe_ratio, max_drawdown"
    ),
    "backtest_trades": (
        "Individual trades in a backtest. Columns: trade_id, run_id, market_slug, ticker, "
        "direction (yes|no), entry_price, exit_price, pnl, spread_at_entry"
    ),
    "market_resolutions": (
        "Ground-truth resolution outcomes for resolved markets. "
        "Columns: market_slug, ticker, category, expires_at, resolved_yes (bool), "
        "final_yes_price, final_no_price, volume"
    ),
    "v_resolution_stats": (
        "VIEW: Resolution stats by ticker + category. "
        "Columns: ticker, category, total_markets, yes_wins, no_wins, yes_pct, no_pct, earliest, latest. "
        "Example: SELECT * FROM doge_predict.v_resolution_stats ORDER BY category, ticker"
    ),
    "v_resolution_totals": (
        "VIEW: Resolution totals by category (+ ALL row). "
        "Columns: category, total_markets, yes_wins, no_wins, yes_pct"
    ),
    "market_snapshots": "(LEGACY v1 — use market_snapshots_v2 instead)",
}

mcp = FastMCP(
    "doge-predict-bq",
    instructions=(
        "Read-only BigQuery access to the doge_predict dataset in the fg-polylabs GCP project. "
        "Contains crypto betting market odds from Polymarket (daily up-or-down markets), "
        "token prices from CoinGecko, strategy definitions, and backtest results. "
        "The primary odds table is market_snapshots_v2 (not market_snapshots). "
        "7 tokens tracked: BTC, ETH, DOGE, SOL, XRP, BNB, HYPE."
    ),
)
client = bigquery.Client(project=PROJECT)


@mcp.tool()
def list_tables() -> str:
    """List all tables in the doge_predict dataset with descriptions."""
    lines = [f"## Tables in `{DATASET}`\n"]
    for name, desc in TABLES.items():
        lines.append(f"- **{name}**: {desc}")
    return "\n".join(lines)


@mcp.tool()
def get_schema(table_name: str) -> str:
    """Return column names, types, and approximate row count for a table."""
    if table_name not in TABLES:
        return f"Unknown table `{table_name}`. Use list_tables() to see available tables."

    ref = f"{PROJECT}.{DATASET}.{table_name}"
    table = client.get_table(ref)

    lines = [f"## {table_name}", f"Rows (approx): {table.num_rows}\n"]
    lines.append("| Column | Type | Mode |")
    lines.append("|--------|------|------|")
    for field in table.schema:
        lines.append(f"| {field.name} | {field.field_type} | {field.mode} |")

    return "\n".join(lines)


_DML_RE = re.compile(
    r"\b(INSERT|UPDATE|DELETE|MERGE|TRUNCATE|DROP|ALTER|CREATE)\b", re.IGNORECASE
)


@mcp.tool()
def query(sql: str, max_rows: int = 200) -> str:
    """
    Run a read-only SQL query against BigQuery. DML is blocked.
    Results are returned as a JSON array (max 200 rows by default).
    Billing is capped at 50 MB per query.
    """
    if _DML_RE.search(sql):
        return "Blocked: DML / DDL statements are not allowed through this tool."

    max_rows = min(max_rows, 200)

    job_config = bigquery.QueryJobConfig(
        maximum_bytes_billed=50_000_000,  # 50 MB safety cap
        use_legacy_sql=False,
    )

    rows = client.query(sql, job_config=job_config).result()

    results = []
    for i, row in enumerate(rows):
        if i >= max_rows:
            break
        results.append(dict(row))

    header = f"Returned {len(results)} rows"
    if len(results) == max_rows:
        header += f" (capped at {max_rows})"

    return header + "\n\n```json\n" + json.dumps(results, indent=2, default=str) + "\n```"


if __name__ == "__main__":
    mcp.run(transport="stdio")
