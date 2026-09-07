#!/usr/bin/env python3
import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class M06Test(unittest.TestCase):
    def test_two_pass_recovers_factor_prices(self):
        cmd=[sys.executable,str(ROOT/'tools/m06_asset_pricing.py')]
        a=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
        b=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
        self.assertEqual(a,b); p=json.loads((ROOT/'data/m06_asset_pricing_results.json').read_text(encoding='utf-8'))
        for est,sample_mean in zip(p['fmb_mean_lambda'],p['sample_factor_mean']): self.assertLess(abs(est-sample_mean),.002)
        self.assertLess(p['beta_rmse'],.08); self.assertLess(p['mean_abs_alpha'],.005)
        self.assertEqual(p['k_factors'],3)
if __name__=='__main__': unittest.main(verbosity=2)
