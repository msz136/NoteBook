#!/usr/bin/env python3
"""Synthetic limit-order-book execution and square-root capacity checks."""
from __future__ import annotations
import json, math
from pathlib import Path

ASKS=[(100.01,1200),(100.02,1800),(100.04,3000),(100.08,5000)]
BIDS=[(99.99,1200),(99.98,1800),(99.96,3000),(99.92,5000)]

def sweep(levels,qty):
    remain=qty; notional=0.0; filled=0
    for price,size in levels:
        take=min(remain,size); notional+=take*price; filled+=take; remain-=take
        if remain<=0: break
    if remain: raise ValueError('insufficient displayed depth')
    return notional/filled

def impact_bps(q,adv,sigma=.02,y=.7): return 10000*sigma*y*math.sqrt(q/adv)

def main():
    mid=100.0; sizes=[500,1500,4000,9000]; rows=[]
    for q in sizes:
        vwap=sweep(ASKS,q); rows.append({'quantity':q,'buy_vwap':vwap,'shortfall_bps':(vwap/mid-1)*10000,
                                        'sqrt_impact_bps':impact_bps(q,2_000_000)})
    alpha_bps=25; half_spread_bps=1; adv=2_000_000
    max_fraction=((alpha_bps-half_spread_bps)/(10000*.02*.7))**2
    result={'mid':mid,'best_bid':BIDS[0][0],'best_ask':ASKS[0][0],'quoted_spread_bps':(ASKS[0][0]-BIDS[0][0])/mid*10000,
            'sweep_results':rows,'capacity':{'gross_alpha_bps':alpha_bps,'half_spread_bps':half_spread_bps,
              'max_adv_fraction_under_sqrt_model':max_fraction,'max_daily_quantity':max_fraction*adv},
            'evidence_boundary':'synthetic displayed book and illustrative impact model; no live fill or market-capacity claim'}
    out=Path(__file__).resolve().parents[1]/'data'/'m09_execution_costs_results.json'
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
