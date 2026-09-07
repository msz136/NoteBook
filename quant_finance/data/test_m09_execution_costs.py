#!/usr/bin/env python3
import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class M09Test(unittest.TestCase):
    def test_cost_monotonicity_and_capacity(self):
        cmd=[sys.executable,str(ROOT/'tools/m09_execution_costs.py')]
        a=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout; b=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
        self.assertEqual(a,b); p=json.loads((ROOT/'data/m09_execution_costs_results.json').read_text(encoding='utf-8'))
        costs=[x['shortfall_bps'] for x in p['sweep_results']]; impacts=[x['sqrt_impact_bps'] for x in p['sweep_results']]
        self.assertEqual(costs,sorted(costs)); self.assertEqual(impacts,sorted(impacts))
        self.assertGreater(p['quoted_spread_bps'],0); self.assertGreater(p['capacity']['max_daily_quantity'],0)
if __name__=='__main__': unittest.main(verbosity=2)
