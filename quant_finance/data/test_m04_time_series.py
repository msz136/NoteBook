#!/usr/bin/env python3
import json, subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
class M04TimeSeriesTest(unittest.TestCase):
    def test_deterministic_and_shapes(self):
        cmd=[sys.executable, str(ROOT/'tools/m04_time_series.py')]
        a=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
        b=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
        self.assertEqual(a,b)
        p=json.loads((ROOT/'data/m04_time_series_results.json').read_text(encoding='utf-8'))
        self.assertEqual(p['n'],260); self.assertEqual(len(p['var1_coefficients']),3)
        self.assertGreater(p['ar1_rolling_rmse'],0); self.assertGreater(p['ewma_last_variance'],0)
if __name__=='__main__': unittest.main(verbosity=2)
