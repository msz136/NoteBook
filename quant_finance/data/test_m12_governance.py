#!/usr/bin/env python3
import copy, json, unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'tools'))
from m12_validate_governance import validate
class M12Test(unittest.TestCase):
    def setUp(self): self.record=json.loads((ROOT/'data/m12_model_governance_record.json').read_text(encoding='utf-8'))
    def test_valid_record_passes(self): self.assertEqual(validate(self.record)['verdict'],'PASS')
    def test_missing_owner_fails(self):
        bad=copy.deepcopy(self.record); bad.pop('owner'); self.assertEqual(validate(bad)['verdict'],'FAIL')
    def test_deployment_without_approval_fails(self):
        bad=copy.deepcopy(self.record); bad['status']='deployed'; self.assertEqual(validate(bad)['verdict'],'FAIL')
if __name__=='__main__': unittest.main(verbosity=2)
