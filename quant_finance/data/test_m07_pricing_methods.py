#!/usr/bin/env python3
import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class M07Test(unittest.TestCase):
    def test_pricing_cross_checks(self):
        cmd=[sys.executable,str(ROOT/'tools/m07_pricing_methods.py')]
        a=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
        b=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
        self.assertEqual(a,b); p=json.loads((ROOT/'data/m07_pricing_methods_results.json').read_text(encoding='utf-8'))
        self.assertLess(p['option']['tree_abs_error'],.02)
        self.assertLess(p['option']['mc_abs_error'],4*p['option']['mc_standard_error'])
        self.assertGreater(p['bond']['price'],0); self.assertGreater(p['bond']['macaulay_duration'],p['bond']['modified_duration'])
if __name__=='__main__': unittest.main(verbosity=2)
