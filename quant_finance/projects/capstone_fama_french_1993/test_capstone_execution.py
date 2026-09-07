#!/usr/bin/env python3
import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
class CapstoneTest(unittest.TestCase):
    def test_frozen_sample_hashes_and_disclosures(self):
        p=subprocess.run([sys.executable,str(ROOT/'execute_capstone.py')],check=True,capture_output=True,text=True)
        r=json.loads((ROOT/'capstone_execution_results.json').read_text(encoding='utf-8'))
        self.assertTrue(r['hash_match']); self.assertEqual(r['n_months'],342); self.assertEqual(r['n_portfolios'],25)
        self.assertEqual(r['status'],'partial_reproduction'); self.assertEqual(r['fama_macbeth']['hAC_status'],'NOT_RUN')
        self.assertEqual(len(r['difference_ledger']),3); self.assertTrue(all(x['status']=='NOT_RUN' for x in r['difference_ledger']))
if __name__=='__main__': unittest.main(verbosity=2)
