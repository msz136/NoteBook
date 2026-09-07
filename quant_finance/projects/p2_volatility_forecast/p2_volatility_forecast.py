#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent

def simulate(n=520, seed=20260722):
    rng=np.random.default_rng(seed); r=np.zeros(n); v=np.zeros(n); v[0]=0.04
    for t in range(1,n):
        v[t]=0.012+0.10*r[t-1]**2+0.86*v[t-1]
        r[t]=rng.normal()*np.sqrt(v[t])
    return r,v

def ewma_forecast(train, test, lam=0.94):
    var=float(np.var(train)); out=[]
    for x in test:
        out.append(max(var,1e-12)); var=lam*var+(1-lam)*x*x
    return np.asarray(out)

def garch_fit(train):
    # Small deterministic grid search: Gaussian quasi-likelihood, no future data.
    s2=float(np.var(train)); best=(float('inf'),0.012,0.10,0.86)
    for alpha in np.linspace(0.04,0.20,9):
        for beta in np.linspace(0.70,0.94,13):
            if alpha+beta>=0.995: continue
            omega=max(s2*(1-alpha-beta),1e-5); var=s2; nll=0.0
            for x in train:
                var=omega+alpha*x*x+beta*var
                nll += np.log(var)+x*x/var
            if nll<best[0]: best=(nll,omega,alpha,beta)
    return best[1:]

def garch_forecast(train, test, params):
    omega,alpha,beta=params; var=float(np.var(train)); out=[]
    for x in test:
        out.append(max(var,1e-12)); var=omega+alpha*x*x+beta*var
    return np.asarray(out)

def qlike(realized_sq, forecast):
    ratio=realized_sq/np.maximum(forecast,1e-12)
    return float(np.mean(ratio-np.log(ratio)-1.0))

def main():
    r,true_v=simulate(); split=360; train=r[:split]; test=r[split:]
    ew=ewma_forecast(train,test); params=garch_fit(train); ga=garch_forecast(train,test,params)
    realized=test*test
    result={'n':len(r),'train':split,'test':len(test),'ewma_lambda':0.94,
            'garch_params':{'omega':params[0],'alpha':params[1],'beta':params[2]},
            'qlike':{'ewma':qlike(realized,ew),'garch':qlike(realized,ga)},
            'forecast_positive':bool(np.all(ew>0) and np.all(ga>0)),
            'split_rule':'fit parameters using returns strictly before test; evaluate one-step variance forecasts'}
    (ROOT/'p2_volatility_forecast_results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
