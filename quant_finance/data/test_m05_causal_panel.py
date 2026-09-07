#!/usr/bin/env python3
import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class M05Test(unittest.TestCase):
    def test_estimators_follow_synthetic_truth(self):
        cmd=[sys.executable,str(ROOT/'tools/m05_causal_panel.py')]
        a=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
        b=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
        self.assertEqual(a,b); p=json.loads((ROOT/'data/m05_causal_panel_results.json').read_text(encoding='utf-8'))
        self.assertLess(abs(p['fe']['within_fe_beta']-1.6),.08)
        self.assertLess(abs(p['iv']['tsls_beta']-2.0),.08)
        self.assertLess(abs(p['did']['did_estimate']-1.5),.12)
        self.assertGreater(abs(p['iv']['ols_beta']-2.0),abs(p['iv']['tsls_beta']-2.0))
if __name__=='__main__': unittest.main(verbosity=2)
