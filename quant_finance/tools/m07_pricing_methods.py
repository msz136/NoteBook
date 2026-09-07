#!/usr/bin/env python3
"""Bond analytics and European option pricing cross-checks for M07."""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np

def norm_cdf(x): return .5*(1+math.erf(x/math.sqrt(2)))

def black_scholes_call(s,k,r,sigma,t):
    d1=(math.log(s/k)+(r+.5*sigma*sigma)*t)/(sigma*math.sqrt(t)); d2=d1-sigma*math.sqrt(t)
    return s*norm_cdf(d1)-k*math.exp(-r*t)*norm_cdf(d2)

def binomial_call(s,k,r,sigma,t,steps=600):
    dt=t/steps; u=math.exp(sigma*math.sqrt(dt)); d=1/u; q=(math.exp(r*dt)-d)/(u-d); disc=math.exp(-r*dt)
    vals=np.maximum(s*(u**np.arange(steps,-1,-1))*(d**np.arange(0,steps+1))-k,0.0)
    for _ in range(steps): vals=disc*(q*vals[:-1]+(1-q)*vals[1:])
    return float(vals[0])

def mc_call(s,k,r,sigma,t,n=200000,seed=20260722):
    rng=np.random.default_rng(seed); z=rng.normal(size=n//2); z=np.concatenate([z,-z])
    st=s*np.exp((r-.5*sigma*sigma)*t+sigma*math.sqrt(t)*z); payoff=np.maximum(st-k,0)
    pv=math.exp(-r*t)*payoff; return float(pv.mean()),float(pv.std(ddof=1)/math.sqrt(n))

def bond_price_duration(face,coupon,y,maturity,freq=2):
    periods=maturity*freq; c=face*coupon/freq; rate=y/freq
    times=np.arange(1,periods+1)/freq; cash=np.full(periods,c); cash[-1]+=face
    pv=cash/(1+rate)**np.arange(1,periods+1); price=float(pv.sum())
    macaulay=float(np.sum(times*pv)/price); modified=macaulay/(1+rate)
    return price,macaulay,modified

def main():
    bond=bond_price_duration(100,0.04,0.045,5); bs=black_scholes_call(100,100,.03,.2,1)
    tree=binomial_call(100,100,.03,.2,1); mc,se=mc_call(100,100,.03,.2,1)
    result={'bond':{'price':bond[0],'macaulay_duration':bond[1],'modified_duration':bond[2]},
      'option':{'black_scholes':bs,'binomial_600':tree,'monte_carlo_antithetic':mc,'mc_standard_error':se,
                'tree_abs_error':abs(tree-bs),'mc_abs_error':abs(mc-bs)},
      'assumptions':'European call, no dividends, constant r and sigma; bond uses flat yield and semiannual coupons',
      'evidence_boundary':'numerical identity and convergence checks only; no market calibration or hedge-PnL claim'}
    out=Path(__file__).resolve().parents[1]/'data'/'m07_pricing_methods_results.json'
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
