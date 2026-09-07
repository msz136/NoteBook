#!/usr/bin/env python3
import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class M08Test(unittest.TestCase):
    def test_constraints_and_tail_order(self):
        cmd=[sys.executable,str(ROOT/'tools/m08_portfolio_risk.py')]
        a=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
        b=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
        self.assertEqual(a,b); p=json.loads((ROOT/'data/m08_portfolio_risk_results.json').read_text(encoding='utf-8'))
        self.assertAlmostEqual(p['weight_sum'],1,places=10); self.assertGreaterEqual(p['min_weight'],-1e-12)
        self.assertGreaterEqual(p['historical_es_95'],p['historical_var_95'])
        self.assertGreater(p['stress_loss'],0); self.assertGreater(p['total_variance'],0)
        self.assertLessEqual(p['factor_variance_example'],p['total_variance'])
        self.assertNotEqual(p['black_litterman_prior'],p['black_litterman_posterior'])
if __name__=='__main__': unittest.main(verbosity=2)
