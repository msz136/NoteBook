#!/usr/bin/env python3
import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
class P7Test(unittest.TestCase):
    def test_determinism_hash_chain_and_recovery(self):
        cmd=[sys.executable,str(ROOT/'run_pipeline.py')]
        subprocess.run(cmd,check=True,capture_output=True,text=True)
        before={p.name:p.read_bytes() for p in (ROOT/'artifacts').glob('*.json')}; manifest1=(ROOT/'pipeline_manifest.json').read_bytes()
        (ROOT/'artifacts'/'04_backtest.json').unlink(); subprocess.run(cmd,check=True,capture_output=True,text=True)
        after={p.name:p.read_bytes() for p in (ROOT/'artifacts').glob('*.json')}; manifest2=(ROOT/'pipeline_manifest.json').read_bytes()
        self.assertEqual(before,after); self.assertEqual(manifest1,manifest2)
        p=json.loads(manifest2); self.assertFalse(p['qlib']['installed']); self.assertEqual([x['status'] for x in p['stages']],['PASS']*5)
        self.assertEqual([x['name'] for x in p['stages']],['data','feature','train','backtest','report'])
if __name__=='__main__': unittest.main(verbosity=2)
