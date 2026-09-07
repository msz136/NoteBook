#!/usr/bin/env python3
"""Deterministic synthetic FE, IV/2SLS, and DiD comparisons for M05."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

def ols(y,x): return np.linalg.lstsq(x,y,rcond=None)[0]

def fe_experiment(rng):
    n,t=120,8; alpha=rng.normal(size=n); x=[]; y=[]; ids=[]
    for i in range(n):
        for j in range(t):
            xv=0.8*alpha[i]+rng.normal(); yv=1.6*xv+alpha[i]+0.15*j+rng.normal(scale=.5)
            x.append(xv); y.append(yv); ids.append(i)
    x=np.asarray(x); y=np.asarray(y); ids=np.asarray(ids)
    pooled=float(ols(y,np.column_stack([np.ones(len(y)),x]))[1])
    xd=x.copy(); yd=y.copy()
    for i in range(n):
        m=ids==i; xd[m]-=x[m].mean(); yd[m]-=y[m].mean()
    within=float(ols(yd[:,None] if False else yd,xd[:,None])[0])
    return {'true_beta':1.6,'pooled_beta':pooled,'within_fe_beta':within,'n_entities':n,'t_periods':t}

def iv_experiment(rng):
    n=5000; z=rng.normal(size=n); u=rng.normal(size=n); x=.9*z+.8*u+rng.normal(scale=.5,size=n); y=2*x+u
    pooled=float(ols(y,np.column_stack([np.ones(n),x]))[1])
    xhat=np.column_stack([np.ones(n),z])@ols(x,np.column_stack([np.ones(n),z]))
    tsls=float(ols(y,np.column_stack([np.ones(n),xhat]))[1])
    return {'true_beta':2.0,'ols_beta':pooled,'tsls_beta':tsls,'first_stage_corr':float(np.corrcoef(z,x)[0,1])}

def did_experiment(rng):
    n=800; treated=np.repeat([0,1],n//2); pre=1+0.4*treated+rng.normal(scale=.5,size=n); effect=1.5
    post=1.3+0.4*treated+effect*treated+rng.normal(scale=.5,size=n)
    did=(post[treated==1].mean()-pre[treated==1].mean())-(post[treated==0].mean()-pre[treated==0].mean())
    return {'true_effect':effect,'did_estimate':float(did),'pre_gap':float(pre[treated==1].mean()-pre[treated==0].mean())}

def main():
    rng=np.random.default_rng(20260722); result={'fe':fe_experiment(rng),'iv':iv_experiment(rng),'did':did_experiment(rng),
      'evidence_boundary':'synthetic identification checks only; no real causal or market claim'}
    out=Path(__file__).resolve().parents[1]/'data'/'m05_causal_panel_results.json'
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
