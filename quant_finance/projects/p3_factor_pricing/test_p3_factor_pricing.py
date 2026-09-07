#!/usr/bin/env python3
import json, unittest
from pathlib import Path
from p3_factor_pricing import parse_monthly
ROOT=Path(__file__).resolve().parent
class P3Test(unittest.TestCase):
    def test_parser_and_frozen_results(self):
        text='note\n,Mkt-RF,SMB,HML,RF\n202401,1,2,3,0.1\n\nAnnual\n'
        names,rows=parse_monthly(text,'Mkt-RF'); self.assertEqual(names[-1],'RF'); self.assertAlmostEqual(rows[0][1][0],.01)
        p=json.loads((ROOT/'p3_factor_pricing_results.json').read_text(encoding='utf-8'))
        self.assertEqual(p['n_portfolios'],25); self.assertGreater(p['n_months'],1000)
        self.assertEqual(len(p['factor_sha256']),64); self.assertEqual(len(p['portfolio_sha256']),64)
        self.assertLess(p['ff3_mean_abs_monthly_alpha'],p['capm_mean_abs_monthly_alpha'])
if __name__=='__main__': unittest.main(verbosity=2)
