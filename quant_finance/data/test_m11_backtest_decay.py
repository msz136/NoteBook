#!/usr/bin/env python3
import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class M11Test(unittest.TestCase):
    def test_engine_gap_cost_and_decay(self):
        cmd=[sys.executable,str(ROOT/'tools/m11_backtest_decay.py')]
        a=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout; b=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
        self.assertEqual(a,b); p=json.loads((ROOT/'data/m11_backtest_decay_results.json').read_text(encoding='utf-8'))
        self.assertLessEqual(p['event_net']['mean_daily'],p['event_gross_partial_fill']['mean_daily'])
        self.assertGreater(p['engine_difference_mean_daily'],0)
        self.assertGreater(p['decay']['early_event_net']['sharpe_annualized'],p['decay']['late_event_net']['sharpe_annualized'])
        self.assertGreater(p['event_cost']['total_turnover'],0)
if __name__=='__main__': unittest.main(verbosity=2)
