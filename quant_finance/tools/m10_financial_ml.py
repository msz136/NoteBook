#!/usr/bin/env python3
"""Purged/embargoed probability prediction and feature ablation for M10."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

def sigmoid(z):
    z=np.clip(z,-30,30); return 1/(1+np.exp(-z))

def fit_logistic(x,y,lam=.2,steps=5000,lr=.08):
    b=np.zeros(x.shape[1]); n=len(y)
    for _ in range(steps): b-=lr*(x.T@(sigmoid(x@b)-y)/n+lam*np.r_[0,b[1:]])
    return b

def scores(y,p):
    p=np.clip(p,1e-9,1-1e-9)
    return {'brier':float(np.mean((p-y)**2)),'log_loss':float(-np.mean(y*np.log(p)+(1-y)*np.log(1-p))),
            'accuracy':float(np.mean((p>=.5)==y))}

def main():
    rng=np.random.default_rng(20260722); n=720; horizon=5; embargo=10; test_start=500
    signal=np.zeros(n); noise=rng.normal(size=n)
    for t in range(1,n): signal[t]=.75*signal[t-1]+rng.normal(scale=.7)
    daily=.004*signal+rng.normal(scale=.012,size=n)
    idx=np.arange(n-horizon); future=np.array([daily[t+1:t+1+horizon].sum() for t in idx]); y=(future>0).astype(float)
    raw=np.column_stack([signal[idx],noise[idx]]); label_end=idx+horizon
    train_mask=label_end < test_start-embargo; test_mask=idx>=test_start
    mean=raw[train_mask].mean(axis=0); std=raw[train_mask].std(axis=0); x=(raw-mean)/std
    xfull=np.column_stack([np.ones(len(x)),x]); xabl=np.column_stack([np.ones(len(x)),x[:,1]])
    bf=fit_logistic(xfull[train_mask],y[train_mask]); ba=fit_logistic(xabl[train_mask],y[train_mask])
    sf=scores(y[test_mask],sigmoid(xfull[test_mask]@bf)); sa=scores(y[test_mask],sigmoid(xabl[test_mask]@ba))
    result={'n_raw':n,'horizon':horizon,'embargo':embargo,'test_start':test_start,
      'train_count':int(train_mask.sum()),'test_count':int(test_mask.sum()),
      'max_train_label_end':int(label_end[train_mask].max()),'first_test_feature_time':int(idx[test_mask].min()),
      'full_model':sf,'ablation_without_signal':sa,'brier_improvement':sa['brier']-sf['brier'],
      'split_contract':'train label_end < test_start - embargo; test feature_time >= test_start',
      'evidence_boundary':'synthetic overlapping-label classification; no real alpha or model-selection claim'}
    out=Path(__file__).resolve().parents[1]/'data'/'m10_financial_ml_results.json'
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
