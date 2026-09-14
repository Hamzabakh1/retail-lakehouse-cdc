"""Small, dependency-free CDC pipeline used as an executable portfolio reference."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SAMPLE_EVENTS: list[dict[str, Any]] = [
    {"event_id": "s-1001", "occurred_at": "2026-09-01T08:12:00Z", "operation": "upsert", "store_id": "CAS-01", "sale_amount": 129.90},
    {"event_id": "s-1002", "occurred_at": "2026-09-01T10:27:00Z", "operation": "upsert", "store_id": "CAS-01", "sale_amount": 85.00},
    {"event_id": "s-1003", "occurred_at": "2026-09-02T09:03:00Z", "operation": "upsert", "store_id": "RAB-02", "sale_amount": 210.50},
    {"event_id": "s-1002", "occurred_at": "2026-09-01T10:27:00Z", "operation": "upsert", "store_id": "CAS-01", "sale_amount": 85.00},
    {"event_id": "s-1004", "occurred_at": "2026-09-02T12:10:00Z", "operation": "upsert", "store_id": "RAB-02", "sale_amount": -7.00},
]


def validate(event: dict[str, Any]) -> str | None:
    required = ("event_id", "occurred_at", "operation", "store_id", "sale_amount")
    if any(not event.get(field) for field in required[:-1]) or "sale_amount" not in event:
        return "missing_required_field"
    if event["operation"] != "upsert":
        return "unsupported_operation"
    if not isinstance(event["sale_amount"], (int, float)) or event["sale_amount"] <= 0:
        return "non_positive_sale_amount"
    try:
        datetime.fromisoformat(event["occurred_at"].replace("Z", "+00:00"))
    except ValueError:
        return "invalid_timestamp"
    return None


def transform(events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    seen: set[str] = set()
    silver: list[dict[str, Any]] = []
    quarantine: list[dict[str, Any]] = []
    for event in events:
        if event.get("event_id") in seen:
            continue
        seen.add(event.get("event_id", ""))
        reason = validate(event)
        if reason:
            quarantine.append({**event, "quarantine_reason": reason})
        else:
            silver.append(event)
    silver.sort(key=lambda item: item["occurred_at"])
    totals: defaultdict[tuple[str, str], float] = defaultdict(float)
    for event in silver:
        totals[(event["occurred_at"][:10], event["store_id"])] += float(event["sale_amount"])
    gold = [
        {"sales_date": date, "store_id": store, "gross_sales": round(amount, 2)}
        for (date, store), amount in sorted(totals.items())
    ]
    return silver, quarantine, gold


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def run(output: Path, events: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    bronze = events or SAMPLE_EVENTS
    silver, quarantine, gold = transform(bronze)
    source_total = round(sum(item["sale_amount"] for item in silver), 2)
    gold_total = round(sum(item["gross_sales"] for item in gold), 2)
    if source_total != gold_total:
        raise ValueError("reconciliation_failed")
    audit = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "bronze_events": len(bronze),
        "silver_events": len(silver),
        "quarantined_events": len(quarantine),
        "gold_rows": len(gold),
        "reconciliation_status": "passed",
        "watermark": max((item["occurred_at"] for item in silver), default=None),
    }
    for name, payload in (("bronze_events.json", bronze), ("silver_sales.json", silver), ("quarantine.json", quarantine), ("gold_daily_sales.json", gold), ("run_audit.json", audit)):
        write_json(output / name, payload)
    return audit


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the retail CDC lakehouse reference pipeline.")
    parser.add_argument("--output", type=Path, default=Path("runtime"))
    args = parser.parse_args()
    audit = run(args.output)
    print(json.dumps(audit, indent=2))
