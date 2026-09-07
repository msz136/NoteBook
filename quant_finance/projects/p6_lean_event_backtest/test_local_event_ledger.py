#!/usr/bin/env python3
import ast, json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
class P6Test(unittest.TestCase):
    def test_ledger_and_algorithm_syntax(self):
        cmd=[sys.executable,str(ROOT/'local_event_ledger.py')]
        a=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout; b=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
        self.assertEqual(a,b); p=json.loads((ROOT/'p6_lean_event_results.json').read_text(encoding='utf-8'))
        self.assertFalse(p['lean_runtime']['cli_found']); self.assertEqual(p['final_position'],0); self.assertEqual(p['total_fees'],3)
        statuses=[e['status'] for e in p['events']]; self.assertIn('partially_filled',statuses); self.assertEqual(statuses.count('filled'),2)
        source=(ROOT/'lean_momentum_algorithm.py').read_text(encoding='utf-8'); ast.parse(source)
        self.assertIn('QCAlgorithm',source); self.assertIn('on_order_event',source)
if __name__=='__main__': unittest.main(verbosity=2)
