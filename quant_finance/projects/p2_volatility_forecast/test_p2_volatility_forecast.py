#!/usr/bin/env python3
import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
class VolatilityTest(unittest.TestCase):
    def test_deterministic_positive_and_qlike(self):
        cmd=[sys.executable,str(ROOT/'p2_volatility_forecast.py')]
        a=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
        b=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
        self.assertEqual(a,b)
        p=json.loads((ROOT/'p2_volatility_forecast_results.json').read_text(encoding='utf-8'))
        self.assertEqual(p['train']+p['test'],p['n']); self.assertTrue(p['forecast_positive'])
        self.assertGreaterEqual(p['qlike']['ewma'],0); self.assertGreaterEqual(p['qlike']['garch'],0)
        self.assertLess(p['garch_params']['alpha']+p['garch_params']['beta'],1)
if __name__=='__main__': unittest.main(verbosity=2)
