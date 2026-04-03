"""
MCP server for read-only BigQuery access to the doge_predict dataset.

Usage (stdio, for Claude Code):
    python mcp/bq_server.py

Requires:
    pip install mcp google-cloud-bigquery
    gcloud auth application-default login
"""

import json
import re
from google.cloud import bigquery
from mcp.server.fastmcp import FastMCP

PROJECT = "fg-polylabs"
DATASET = "doge_predict"

TABLES = {
    "tracked_markets": "Crypto betting markets being tracked (market_id, slug, title, category=crypto_daily|crypto_weekly, platform, yes/no_token_id, active, end_date)",
    "market_snapshots": "Time-series price/odds snapshots (market_slug, outcome_tag=yes|no, timestamp, price 0-1, volume, liquidity). Partitioned by date, clustered by market_slug. Dedup key: (market_slug, outcome_tag, timestamp)",
    "tracked_tokens": "Crypto tokens being tracked (symbol, name, platform, coingecko_id, active)",
    "price_snapshots": "Token price time-series (token, price_usd, market_cap, volume_24h, timestamp)",
    "strategies": "Defined betting strategies (name, description, type, params JSON, active)",
    "backtest_runs": "Backtest execution results (strategy_id, start/end_date, initial/final_capital, sharpe, max_drawdown, win_rate)",
    "backtest_trades": "Individual trades within a backtest run (run_id, market_id, direction, entry/exit_price, pnl, timestamp)",
}

mcp = FastMCP(
    "doge-predict-bq",
    instructions=(
        "Read-only BigQuery access to the doge_predict dataset in the fg-polylabs GCP project. "
        "Contains crypto price data, betting market odds, strategies, and backtest results."
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
