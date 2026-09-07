#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent

def simplex(v):
    u=np.sort(v)[::-1]; css=np.cumsum(u)-1; rho=np.nonzero(u-css/(np.arange(len(v))+1)>0)[0][-1]
    return np.maximum(v-css[rho]/(rho+1),0)

def target_weights(mu,cov,gamma=8,steps=2500):
    w=np.ones(len(mu))/len(mu)
    for _ in range(steps): w=simplex(w-.05*(gamma*cov@w-mu))
    return w

def apply_turnover_cap(old,target,cap):
    turnover=float(np.abs(target-old).sum())
    return target if turnover<=cap else old+(target-old)*(cap/turnover)

def metrics(r):
    mean=float(np.mean(r)); vol=float(np.std(r,ddof=1)); return {'mean_daily':mean,'vol_daily':vol,'sharpe_annualized':mean/vol*np.sqrt(252) if vol else 0}

def main():
    rng=np.random.default_rng(20260722); n=8; t=720
    b=rng.normal(scale=.5,size=(n,3)); fc=np.diag([.00012,.00008,.00005]); cov=b@fc@b.T+np.eye(n)*.00012
    true_mu=np.linspace(.00018,.00042,n); returns=rng.multivariate_normal(true_mu,cov,size=t)
    lookback,step,cost_bps=120,20,10; wa=wb=np.ones(n)/n; ra=[]; rb=[]; grossa=[]; grossb=[]; ta=tb=0.0
    for start in range(lookback,t,step):
        hist=returns[start-lookback:start]; mu=hist.mean(axis=0); c=np.cov(hist,rowvar=False)+np.eye(n)*1e-8
        newa=target_weights(mu,c); shrink=.25*mu+.75*np.full(n,mu.mean()); rawb=target_weights(shrink,c); newb=apply_turnover_cap(wb,rawb,.35)
        turna=float(np.abs(newa-wa).sum()); turnb=float(np.abs(newb-wb).sum()); ta+=turna; tb+=turnb
        block=returns[start:min(start+step,t)]; ga=block@newa; gb=block@newb
        na=ga.copy(); nb=gb.copy(); na[0]-=cost_bps/10000*turna; nb[0]-=cost_bps/10000*turnb
        grossa.extend(ga); grossb.extend(gb); ra.extend(na); rb.extend(nb); wa,wb=newa,newb
    stress=np.linspace(-.15,-.05,n)
    result={'protocol':{'n_assets':n,'n_days':t,'lookback':lookback,'rebalance_days':step,'cost_bps_per_unit_turnover':cost_bps},
      'sample_mean':{'gross':metrics(np.asarray(grossa)),'net':metrics(np.asarray(ra)),'total_turnover':ta,'stress_loss':float(-(stress@wa))},
      'shrink_turnover_cap':{'gross':metrics(np.asarray(grossb)),'net':metrics(np.asarray(rb)),'total_turnover':tb,'stress_loss':float(-(stress@wb))},
      'final_weights':{'sample_mean':wa.tolist(),'shrink_turnover_cap':wb.tolist()},
      'evidence_boundary':'synthetic walk-forward comparison; no real performance or investment claim'}
    (ROOT/'p4_portfolio_risk_results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
