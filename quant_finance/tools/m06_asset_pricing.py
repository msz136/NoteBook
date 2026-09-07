#!/usr/bin/env python3
"""Synthetic factor-model and Fama–MacBeth two-pass experiment."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

def ols(y,x): return np.linalg.lstsq(x,y,rcond=None)[0]

def main():
    rng=np.random.default_rng(20260722); t,n,k=360,45,3
    true_lambda=np.array([0.004,0.0025,0.0015])
    factor_cov=np.array([[.0016,.0002,.0001],[.0002,.0010,.0001],[.0001,.0001,.0008]])
    factors=rng.multivariate_normal(true_lambda,factor_cov,size=t)
    beta=rng.uniform(.3,1.7,size=(n,k)); idio=rng.normal(scale=.025,size=(t,n))
    returns=factors@beta.T+idio
    x=np.column_stack([np.ones(t),factors]); estimates=np.vstack([ols(returns[:,i],x) for i in range(n)])
    alpha_hat=estimates[:,0]; beta_hat=estimates[:,1:]
    z=np.column_stack([np.ones(n),beta_hat]); lambdas=np.vstack([ols(returns[j],z) for j in range(t)])
    result={'t_periods':t,'n_assets':n,'k_factors':k,'true_lambda':true_lambda.tolist(),
            'sample_factor_mean':factors.mean(axis=0).tolist(),
            'fmb_mean_lambda':lambdas[:,1:].mean(axis=0).tolist(),
            'fmb_lambda_se':(lambdas[:,1:].std(axis=0,ddof=1)/np.sqrt(t)).tolist(),
            'mean_abs_alpha':float(np.mean(np.abs(alpha_hat))),
            'beta_rmse':float(np.sqrt(np.mean((beta_hat-beta)**2))),
            'pricing_error_rmse':float(np.sqrt(np.mean(alpha_hat**2))),
            'evidence_boundary':'synthetic factor DGP; no real asset-pricing or investability claim'}
    out=Path(__file__).resolve().parents[1]/'data'/'m06_asset_pricing_results.json'
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
