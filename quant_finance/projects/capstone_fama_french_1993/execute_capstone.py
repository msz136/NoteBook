#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'p3_factor_pricing'))
from p3_factor_pricing import download_zip, parse_monthly, FACTOR_URL, PORT_URL
ROOT=Path(__file__).resolve().parent
EXPECTED_F='80b88699a18ac408e2456d25b1004e340f3f7f8d41d5b476a0285bc53c6f0436'; EXPECTED_P='afc2f6c40237d07b99ab84ab9375a08bc301e3801e3ad8d91aa90d5aa9ec6295'

def ols(y,x): return np.linalg.lstsq(x,y,rcond=None)[0]

def main():
    ft,fh=download_zip(FACTOR_URL); pt,ph=download_zip(PORT_URL)
    fn,fr=parse_monthly(ft,'Mkt-RF'); pn,pr=parse_monthly(pt,'Average Value Weighted Returns -- Monthly')
    fd={d:v for d,v in fr}; pd={d:v for d,v in pr}; dates=sorted(set(fd)&set(pd)); dates=[d for d in dates if '196307'<=d<='199112']
    f=np.asarray([fd[d] for d in dates]); p=np.asarray([pd[d] for d in dates]); excess=p-f[:,3,None]; X=np.column_stack([np.ones(len(dates)),f[:,:3]])
    ts=np.vstack([ols(excess[:,i],X) for i in range(25)]); lambdas=np.vstack([ols(excess[t],np.column_stack([np.ones(25),ts[:,1:]])) for t in range(len(dates))])
    result={'status':'partial_reproduction','protocol_status':'protocol_frozen_not_executed','factor_sha256':fh,'portfolio_sha256':ph,
      'hash_match':fh==EXPECTED_F and ph==EXPECTED_P,'sample_start':dates[0],'sample_end':dates[-1],'n_months':len(dates),'n_portfolios':25,
      'time_series':{'mean_abs_alpha':float(np.mean(np.abs(ts[:,0]))),'max_abs_alpha':float(np.max(np.abs(ts[:,0]))),'mean_beta':ts[:,1:].mean(axis=0).tolist()},
      'fama_macbeth':{'mean_lambda':lambdas[:,1:].mean(axis=0).tolist(),'lambda_std':lambdas[:,1:].std(axis=0,ddof=1).tolist(),'hAC_status':'NOT_RUN'},
      'difference_ledger':[{'item':'raw paper tables digitized','status':'NOT_RUN','reason':'paper tables not machine-extracted in this slice'},
        {'item':'GRS joint pricing-error test','status':'NOT_RUN','reason':'test implementation not frozen in protocol execution environment'},
        {'item':'HAC standard errors','status':'NOT_RUN','reason':'statsmodels unavailable; lambda standard deviations only'}],
      'evidence_boundary':'official files re-downloaded and hashed; outputs are partial reproduction, not proof of paper equivalence or investment alpha'}
    (ROOT/'capstone_execution_results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2)); return 0 if result['hash_match'] and result['n_months']==342 else 1
if __name__=='__main__': raise SystemExit(main())
