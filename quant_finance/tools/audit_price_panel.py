#!/usr/bin/env python3
"""Audit the M02 synthetic price-panel fixture and compute explicit return fields."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path


REQUIRED = {
    "symbol", "session_date", "observed_at", "available_at", "asof_at", "close_raw",
    "close_adjusted", "cash_dividend", "split_factor", "source_id", "license_class",
}


def parse_utc(value: str) -> datetime:
    if not value.endswith("Z"):
        raise ValueError(f"timestamp must use UTC Z suffix: {value}")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo != timezone.utc:
        raise ValueError(f"timestamp must be UTC: {value}")
    return parsed


def audit(path: Path) -> dict:
    checks = []
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    fields = set(rows[0]) if rows else set()
    checks.append({"name": "required_fields", "status": "PASS" if REQUIRED <= fields else "FAIL", "missing": sorted(REQUIRED - fields)})
    failures: list[str] = []
    by_symbol: dict[str, list[dict]] = {}
    for idx, row in enumerate(rows, start=2):
        try:
            parse_utc(row["observed_at"])
            available = parse_utc(row["available_at"])
            asof = parse_utc(row["asof_at"])
            if available > asof:
                failures.append(f"line {idx}: available_at after asof_at")
            if float(row["close_raw"]) <= 0 or float(row["close_adjusted"]) <= 0:
                failures.append(f"line {idx}: price must be positive")
            if float(row["cash_dividend"]) < 0 or float(row["split_factor"]) <= 0:
                failures.append(f"line {idx}: dividend/split constraint")
            datetime.fromisoformat(row["session_date"])
            by_symbol.setdefault(row["symbol"], []).append(row)
        except (KeyError, ValueError) as exc:
            failures.append(f"line {idx}: {exc}")

    return_rows = []
    for symbol, symbol_rows in by_symbol.items():
        dates = [row["session_date"] for row in symbol_rows]
        if dates != sorted(set(dates)):
            failures.append(f"{symbol}: session_date must be unique and strictly increasing")
        for previous, current in zip(symbol_rows, symbol_rows[1:]):
            prev_raw = float(previous["close_raw"])
            current_raw = float(current["close_raw"])
            prev_adj = float(previous["close_adjusted"])
            current_adj = float(current["close_adjusted"])
            dividend = float(current["cash_dividend"])
            return_rows.append({
                "symbol": symbol,
                "session_date": current["session_date"],
                "price_return_raw": current_raw / prev_raw - 1.0,
                "total_return_raw": (current_raw + dividend) / prev_raw - 1.0,
                "return_adjusted_close": current_adj / prev_adj - 1.0,
                "split_factor": float(current["split_factor"]),
            })

    checks.extend([
        {"name": "row_count", "status": "PASS" if len(rows) == 7 else "FAIL", "value": len(rows)},
        {"name": "timestamp_and_value_constraints", "status": "PASS" if not failures else "FAIL", "failures": failures},
        {"name": "return_rows", "status": "PASS" if len(return_rows) == 5 else "FAIL", "value": len(return_rows)},
    ])
    return {"verdict": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL", "checks": checks, "returns": return_rows}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "m02_price_panel_fixture.csv")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "m02_price_panel_audit.json")
    args = parser.parse_args()
    result = audit(args.input.resolve())
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
