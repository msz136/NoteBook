#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent; ART=ROOT/'artifacts'

def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ART.mkdir(exist_ok=True); stages=[]; rng=np.random.default_rng(20260722); n=500
    price=100*np.exp(np.cumsum(rng.normal(.0002,.01,size=n))); data={'price':price.tolist(),'n':n,'seed':20260722}
    p=ART/'01_data.json'; write_json(p,data); stages.append(('data',[],p))
    ret=np.diff(np.log(price),prepend=np.log(price[0])); mom=np.convolve(ret,np.ones(5),mode='full')[:n]
    feature={'return_1d':ret.tolist(),'momentum_5d':mom.tolist(),'source_sha256':sha(p)}
    f=ART/'02_features.json'; write_json(f,feature); stages.append(('feature',[p],f))
    x=np.column_stack([np.ones(349),mom[:349]]); y=ret[1:350]; beta=np.linalg.lstsq(x,y,rcond=None)[0]
    model={'beta':beta.tolist(),'train_end_exclusive':350,'feature_sha256':sha(f)}
    m=ART/'03_model.json'; write_json(m,model); stages.append(('train',[f],m))
    pred=beta[0]+beta[1]*mom[350:-1]; pos=np.sign(pred); realized=ret[351:]; turnover=np.abs(np.diff(np.r_[0,pos])); net=pos*realized-.0005*turnover
    bt={'test_start':350,'test_end_exclusive':n-1,'mean_daily':float(net.mean()),'vol_daily':float(net.std(ddof=1)),
        'sharpe_annualized':float(net.mean()/net.std(ddof=1)*math.sqrt(252)),'total_turnover':float(turnover.sum()),
        'model_sha256':sha(m),'cost_bps_per_turnover':5}
    b=ART/'04_backtest.json'; write_json(b,bt); stages.append(('backtest',[m],b))
    summary={'verdict':'PIPELINE_EXECUTED_SYNTHETIC','backtest':bt,'boundary':'Qlib not installed; no real alpha or production deployment'}
    r=ART/'05_report.json'; write_json(r,summary); stages.append(('report',[b],r))
    manifest={'qlib':{'installed':False,'official_head':'d5379c520f66a39953bad76234a7019a72796fd0'},'stages':[]}
    for name,inputs,out in stages:
        manifest['stages'].append({'name':name,'status':'PASS','inputs':[{"path":x.name,'sha256':sha(x)} for x in inputs],
                                   'output':{'path':out.name,'sha256':sha(out)}})
    write_json(ROOT/'pipeline_manifest.json',manifest); print(json.dumps(manifest,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
