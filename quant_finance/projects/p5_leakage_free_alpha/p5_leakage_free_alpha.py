#!/usr/bin/env python3
from __future__ import annotations
import json, math
from pathlib import Path
from statistics import NormalDist
import numpy as np
ROOT=Path(__file__).resolve().parent

def metrics(ret):
    m=float(ret.mean()); s=float(ret.std(ddof=1)); sharpe=m/s*math.sqrt(252) if s else 0
    t=m/(s/math.sqrt(len(ret))) if s else 0; p=2*(1-NormalDist().cdf(abs(t)))
    return {'mean_daily':m,'vol_daily':s,'sharpe_annualized':sharpe,'naive_two_sided_p':p}

def net_returns(position,future_return,cost_bps=5):
    turnover=np.abs(np.diff(np.r_[0,position])); return position*future_return-cost_bps/10000*turnover

def main():
    rng=np.random.default_rng(20260722); n=820; sig=np.zeros(n); noise=rng.normal(size=n)
    for t in range(1,n): sig[t]=.72*sig[t-1]+rng.normal(scale=.8)
    ret=.0018*sig+rng.normal(scale=.012,size=n)
    # feature at t maps to return at t+1
    x=sig[:-1]; z=noise[:-1]; y=ret[1:]; times=np.arange(len(y))
    splits={'train':[0,400],'validation':[420,560],'test':[580,len(y)]}; embargo=20
    candidates={'signal':np.tanh(x),'lagged':np.tanh(np.r_[0,x[:-1]]),'blend':np.tanh(.7*x+.3*z),
                'high_threshold':np.where(x>.8,1,np.where(x<-.8,-1,0)),'noise':np.tanh(z),'reversed':-np.tanh(x)}
    ledger=[]; va=slice(*splits['validation']); te=slice(*splits['test'])
    for cid,pos in candidates.items():
        vm=metrics(net_returns(pos[va],y[va])); ledger.append({'candidate_id':cid,'validation':vm,'status':'evaluated_validation'})
    selected=max(ledger,key=lambda r:r['validation']['sharpe_annualized']); selected_id=selected['candidate_id']
    for row in ledger: row['status']='selected' if row['candidate_id']==selected_id else 'failed_validation'
    test_result=metrics(net_returns(candidates[selected_id][te],y[te])); m=len(ledger)
    selected['validation']['bonferroni_p']=min(1.0,selected['validation']['naive_two_sided_p']*m)
    result={'splits':splits,'embargo':embargo,'label_horizon':1,'cost_bps_per_unit_turnover':5,'candidate_count':m,
            'selected_candidate':selected_id,'selection_rule':'maximum validation net annualized Sharpe; test unopened until selection',
            'ledger':ledger,'selected_test_net':test_result,
            'split_invariants':{'train_end_plus_embargo_le_validation_start':splits['train'][1]+embargo<=splits['validation'][0],
              'validation_end_plus_embargo_le_test_start':splits['validation'][1]+embargo<=splits['test'][0]},
            'evidence_boundary':'synthetic candidate ledger; test result is not real alpha or statistical proof'}
    (ROOT/'p5_leakage_free_alpha_results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
