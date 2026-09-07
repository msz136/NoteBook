#!/usr/bin/env python3
import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
class P5Test(unittest.TestCase):
    def test_selection_ledger_and_frozen_test(self):
        cmd=[sys.executable,str(ROOT/'p5_leakage_free_alpha.py')]
        a=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout; b=subprocess.run(cmd,check=True,capture_output=True,text=True).stdout
        self.assertEqual(a,b); p=json.loads((ROOT/'p5_leakage_free_alpha_results.json').read_text(encoding='utf-8'))
        self.assertTrue(all(p['split_invariants'].values())); self.assertEqual(len(p['ledger']),p['candidate_count'])
        best=max(p['ledger'],key=lambda x:x['validation']['sharpe_annualized'])['candidate_id']; self.assertEqual(best,p['selected_candidate'])
        self.assertEqual(sum(x['status']=='selected' for x in p['ledger']),1); self.assertGreater(sum(x['status']=='failed_validation' for x in p['ledger']),0)
        selected=next(x for x in p['ledger'] if x['status']=='selected'); self.assertGreaterEqual(selected['validation']['bonferroni_p'],selected['validation']['naive_two_sided_p'])
if __name__=='__main__': unittest.main(verbosity=2)
