#!/usr/bin/env python3
"""Vectorized versus event-style backtest semantics with strategy decay."""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np

def metrics(x):
    m=float(x.mean()); s=float(x.std(ddof=1)); return {'mean_daily':m,'vol_daily':s,'sharpe_annualized':m/s*math.sqrt(252) if s else 0,
      'max_drawdown':float(np.min(np.cumprod(1+x)/np.maximum.accumulate(np.cumprod(1+x))-1))}

def main():
    rng=np.random.default_rng(20260722); n=900; signal=np.zeros(n)
    for t in range(1,n): signal[t]=.65*signal[t-1]+rng.normal(scale=.9)
    coef=np.where(np.arange(n)<450,.0016,.0002); next_return=coef*signal+rng.normal(scale=.012,size=n)
    target=np.tanh(signal); vector=target*next_return
    fill=.9*target; turnover=np.abs(np.diff(np.r_[0,fill])); event_gross=fill*next_return
    event_net=event_gross-(4+2)/10000*turnover
    result={'n_days':n,'decision':'signal available at close t; synthetic next-period return aligned to t decision',
      'vectorized_gross':metrics(vector),'event_gross_partial_fill':metrics(event_gross),'event_net':metrics(event_net),
      'event_cost':{'commission_bps':4,'slippage_bps':2,'fill_fraction':.9,'total_turnover':float(turnover.sum())},
      'decay':{'early_event_net':metrics(event_net[:450]),'late_event_net':metrics(event_net[450:]),
               'true_signal_coefficient_early':.0016,'true_signal_coefficient_late':.0002},
      'engine_difference_mean_daily':float(vector.mean()-event_net.mean()),
      'evidence_boundary':'synthetic regime change and simplified fill/cost model; no engine benchmark or real strategy claim'}
    out=Path(__file__).resolve().parents[1]/'data'/'m11_backtest_decay_results.json'
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
