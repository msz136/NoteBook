#!/usr/bin/env python3
"""Negative and positive tests for the M02 data-contract audit."""

from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audit_price_panel import audit


ROOT = Path(__file__).resolve().parent


class PricePanelAuditTest(unittest.TestCase):
    def test_fixture_passes(self) -> None:
        result = audit(ROOT / "m02_price_panel_fixture.csv")
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(len(result["returns"]), 5)

    def test_future_available_at_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.csv"
            with (ROOT / "m02_price_panel_fixture.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            rows[0]["available_at"] = "2024-01-07T21:05:00Z"
            with bad.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
            result = audit(bad)
            self.assertEqual(result["verdict"], "FAIL")
            self.assertTrue(any("available_at" in failure for failure in result["checks"][2]["failures"]))


if __name__ == "__main__":
    unittest.main()
