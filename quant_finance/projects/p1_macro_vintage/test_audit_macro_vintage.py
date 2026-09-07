#!/usr/bin/env python3
import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
class MacroVintageTest(unittest.TestCase):
    def test_point_in_time_differs_from_final(self):
        subprocess.run([sys.executable,str(ROOT/'audit_macro_vintage.py')],check=True,capture_output=True,text=True)
        p=json.loads((ROOT/'p1_macro_vintage_results.json').read_text(encoding='utf-8'))
        self.assertEqual(p['visible_rows'],1); self.assertEqual(p['final_rows'],3)
        self.assertTrue(p['leakage_detected']); self.assertGreater(p['mean_abs_revision_delta'],0)
    def test_future_release_is_not_visible(self):
        from audit_macro_vintage import load_rows, visible_asof
        rows=load_rows(ROOT/'p1_macro_vintage_fixture.csv')
        self.assertTrue(all(r['release_at'] <= '2024-02-28T00:00:00' for r in visible_asof(rows,'2024-02-28T00:00:00')))
if __name__=='__main__': unittest.main(verbosity=2)
