#!/usr/bin/env python3
"""Long-only portfolio, Black–Litterman, factor risk, VaR/ES smoke experiment."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

def simplex(v):
    u=np.sort(v)[::-1]; cssv=np.cumsum(u)-1; rho=np.nonzero(u-cssv/(np.arange(len(v))+1)>0)[0][-1]
    theta=cssv[rho]/(rho+1); return np.maximum(v-theta,0)

def optimize(mu,cov,gamma=4.0,steps=8000):
    w=np.ones(len(mu))/len(mu); lr=.03
    for _ in range(steps): w=simplex(w-lr*(gamma*cov@w-mu))
    return w

def black_litterman(pi,cov,p,q,tau=.05,omega=None):
    omega=np.diag(np.diag(p@(tau*cov)@p.T)) if omega is None else omega
    a=np.linalg.inv(tau*cov)+p.T@np.linalg.inv(omega)@p
    b=np.linalg.inv(tau*cov)@pi+p.T@np.linalg.inv(omega)@q
    return np.linalg.solve(a,b)

def main():
    rng=np.random.default_rng(20260722); n=6
    b=np.array([[1,.2],[.8,-.1],[1.1,.3],[.5,-.2],[.9,.4],[.6,.1]]); fcov=np.array([[.00012,.00002],[.00002,.00008]])
    cov=b@fcov@b.T+np.diag([.00007,.00008,.00006,.00009,.00007,.00008]); mu=np.array([.00035,.00025,.00030,.00020,.00028,.00022])
    returns=rng.multivariate_normal(mu,cov,size=1500); w=optimize(mu,cov)
    pi=3.0*cov@(np.ones(n)/n); p=np.array([[1,-1,0,0,0,0],[0,0,1,0,-1,0]],float); q=np.array([.00018,.00010])
    posterior=black_litterman(pi,cov,p,q)
    port=returns@w; losses=-port; var=float(np.quantile(losses,.95)); es=float(losses[losses>=var].mean())
    stress=np.array([-.12,-.08,-.10,-.06,-.09,-.07]); stress_loss=float(-(stress@w))
    factor_var=float(w@b@fcov@b.T@w); total_var=float(w@cov@w)
    result={'weights':w.tolist(),'weight_sum':float(w.sum()),'min_weight':float(w.min()),
      'expected_daily_return':float(mu@w),'daily_volatility':float(np.sqrt(total_var)),
      'black_litterman_prior':pi.tolist(),'black_litterman_posterior':posterior.tolist(),
      'historical_var_95':var,'historical_es_95':es,'stress_loss':stress_loss,
      'factor_variance_example':factor_var,'total_variance':total_var,
      'evidence_boundary':'synthetic returns and illustrative views; no investment recommendation'}
    out=Path(__file__).resolve().parents[1]/'data'/'m08_portfolio_risk_results.json'
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
