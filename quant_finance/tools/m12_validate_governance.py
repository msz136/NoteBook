#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REQUIRED={'model_id','owner','independent_reviewer','purpose','data_revision','code_revision','environment_hash','status','metrics','limits','approvals','monitoring','rollback','incident_drill'}

def validate(record):
    checks=[]
    missing=sorted(REQUIRED-set(record)); checks.append({'name':'required_fields','pass':not missing,'missing':missing})
    approvals=record.get('approvals',{}); checks.append({'name':'no_production_without_approval','pass':record.get('status')!='deployed' or approvals.get('production') is True})
    drill=record.get('incident_drill',{}); checks.append({'name':'incident_drill_complete','pass':all(drill.get(k) is True for k in ['detected','orders_blocked','owner_notified','recovery_verified'])})
    rb=record.get('rollback',{}); checks.append({'name':'rollback_defined','pass':bool(rb.get('action')) and bool(rb.get('artifact_revision'))})
    checks.append({'name':'independent_roles','pass':bool(record.get('owner')) and record.get('owner')!=record.get('independent_reviewer')})
    return {'verdict':'PASS' if all(x['pass'] for x in checks) else 'FAIL','checks':checks}

def main(path=None):
    src=Path(path) if path else ROOT/'data'/'m12_model_governance_record.json'; record=json.loads(src.read_text(encoding='utf-8')); result=validate(record)
    if path is None: (ROOT/'data'/'m12_model_governance_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2)); return 0 if result['verdict']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main(sys.argv[1] if len(sys.argv)>1 else None))
