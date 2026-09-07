#!/usr/bin/env python3
"""Validate P0 machine-readable results against the frozen protocol."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent


def add(checks: list[dict[str, Any]], name: str, ok: bool, evidence: Any) -> None:
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "evidence": evidence})


def validate(summary: dict[str, Any], plot_path: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    protocol = summary["protocol"]
    add(checks, "protocol_version", protocol["protocol_version"] == "p0-v1", protocol["protocol_version"])
    add(checks, "fixed_seed", protocol["seed"] == 20260722, protocol["seed"])

    finite = True
    for family in summary["lln_clt"].values():
        for row in family:
            finite &= all(math.isfinite(v) for k, v in row.items() if k != "n")
    add(checks, "finite_lln_clt_metrics", finite, "all LLN/CLT floating metrics are finite")

    rmse_evidence = {}
    rmse_ok = True
    for name, rows in summary["lln_clt"].items():
        first, last = rows[0]["mean_rmse"], rows[-1]["mean_rmse"]
        rmse_evidence[name] = {"n_first": rows[0]["n"], "rmse_first": first, "n_last": rows[-1]["n"], "rmse_last": last}
        rmse_ok &= last < first
    add(checks, "lln_rmse_contracts", rmse_ok, rmse_evidence)

    clt_evidence = {name: rows[-1]["normal_95_coverage"] for name, rows in summary["lln_clt"].items()}
    add(checks, "large_n_clt_coverage", all(0.90 <= value <= 0.99 for value in clt_evidence.values()), clt_evidence)

    variance_ok = all(abs(row["ddof1_bias"]) < abs(row["ddof0_bias"]) for row in summary["variance_bias"])
    add(checks, "unbiased_variance_improves_bias", variance_ok, summary["variance_bias"])

    t_coverage = {row["n"]: row["t_interval_coverage"] for row in summary["ci_coverage_normal"]}
    add(checks, "normal_t_interval_coverage", all(0.93 <= value <= 0.97 for value in t_coverage.values()), t_coverage)

    bootstrap = {row["n"]: row["percentile_coverage"] for row in summary["bootstrap_median"]}
    add(checks, "bootstrap_coverage_bounded", all(0.80 <= value <= 0.99 for value in bootstrap.values()), bootstrap)
    add(checks, "plot_exists", plot_path.exists() and plot_path.stat().st_size > 1000, {"path": str(plot_path), "bytes": plot_path.stat().st_size if plot_path.exists() else 0})

    failures = [item["name"] for item in checks if item["status"] == "FAIL"]
    return {"verdict": "PASS" if not failures else "FAIL", "checks": checks, "open_items": failures}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, default=ROOT / "results" / "summary.json")
    parser.add_argument("--plot", type=Path, default=ROOT / "results" / "summary.svg")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "validation.json")
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    result = validate(summary, args.plot)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
