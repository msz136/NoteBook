#!/usr/bin/env python3
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class M03EstimatorTest(unittest.TestCase):
    def test_comparison_invariants(self):
        subprocess.run([sys.executable, str(ROOT / "tools/m03_core_estimators.py")], check=True, capture_output=True, text=True)
        payload = json.loads((ROOT / "data/m03_estimator_comparison.json").read_text(encoding="utf-8"))
        self.assertLess(payload["max_ols_mle_abs_diff"], 1e-12)
        self.assertLess(payload["max_ols_gmm_abs_diff"], 1e-12)
        self.assertEqual(payload["bootstrap"]["reps"], 400)
        self.assertEqual(len(payload["bootstrap"]["ci_percentile_95"]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
