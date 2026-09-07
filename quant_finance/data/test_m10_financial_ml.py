#!/usr/bin/env python3
import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class M10Test(unittest.TestCase):
    def test_purge_embargo_and_ablation(self):
        cmd=[sys.executable,str(ROOT/'tools/m10_financial_ml.py')]
        a=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout; b=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
        self.assertEqual(a,b); p=json.loads((ROOT/'data/m10_financial_ml_results.json').read_text(encoding='utf-8'))
        self.assertLess(p['max_train_label_end'],p['test_start']-p['embargo'])
        self.assertGreaterEqual(p['first_test_feature_time'],p['test_start'])
        self.assertGreater(p['brier_improvement'],0)
        self.assertLess(p['full_model']['brier'],.25)
if __name__=='__main__': unittest.main(verbosity=2)
