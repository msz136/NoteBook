#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main():
    cash=100000.0; position=0; fee_per_fill=1.0; slippage=0.0002; events=[]
    orders=[{'id':1,'side':'buy','qty':100,'reference':100.0,'fills':[40,60]},
            {'id':2,'side':'sell','qty':100,'reference':102.0,'fills':[100]}]
    total_fees=0.0
    for order in orders:
        events.append({'order_id':order['id'],'status':'submitted','quantity':order['qty']})
        filled=0
        for q in order['fills']:
            direction=1 if order['side']=='buy' else -1
            price=order['reference']*(1+direction*slippage); cash-=direction*q*price; position+=direction*q
            cash-=fee_per_fill; total_fees+=fee_per_fill; filled+=q
            status='filled' if filled==order['qty'] else 'partially_filled'
            events.append({'order_id':order['id'],'status':status,'fill_quantity':direction*q,'fill_price':price,'cash':cash,'position':position})
    result={'lean_runtime':{'cli_found':False,'dotnet_found':False,'official_head':'153d0b7427a918063a018ec18964ddf450edc125'},
      'initial_cash':100000.0,'final_cash':cash,'final_position':position,'total_fees':total_fees,'event_count':len(events),'events':events,
      'realized_pnl_after_fee_and_slippage':cash-100000.0,
      'evidence_boundary':'local deterministic ledger only; LEAN algorithm not executed in this environment'}
    (ROOT/'p6_lean_event_results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
