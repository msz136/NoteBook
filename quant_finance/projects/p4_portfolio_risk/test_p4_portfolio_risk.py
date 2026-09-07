#!/usr/bin/env python3
import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
class P4Test(unittest.TestCase):
    def test_cost_turnover_and_constraints(self):
        cmd=[sys.executable,str(ROOT/'p4_portfolio_risk.py')]
        a=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout; b=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
        self.assertEqual(a,b); p=json.loads((ROOT/'p4_portfolio_risk_results.json').read_text(encoding='utf-8'))
        x=p['sample_mean']; y=p['shrink_turnover_cap']
        self.assertLess(y['total_turnover'],x['total_turnover'])
        self.assertLessEqual(x['net']['mean_daily'],x['gross']['mean_daily']); self.assertLessEqual(y['net']['mean_daily'],y['gross']['mean_daily'])
        for w in p['final_weights'].values(): self.assertAlmostEqual(sum(w),1,places=10); self.assertGreaterEqual(min(w),-1e-12)
        self.assertGreater(x['stress_loss'],0); self.assertGreater(y['stress_loss'],0)
if __name__=='__main__': unittest.main(verbosity=2)
