#!/usr/bin/env python3
from __future__ import annotations
import csv, json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def parse(s: str) -> datetime:
    return datetime.fromisoformat(s)

def load_rows(path: Path) -> list[dict]:
    with path.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    required={'series_id','observation_date','release_at','vintage_at','value','revision_kind'}
    if not rows or not required.issubset(rows[0]): raise ValueError('schema')
    for r in rows: parse(r['release_at']); parse(r['vintage_at']); float(r['value'])
    return rows

def visible_asof(rows: list[dict], asof: str) -> list[dict]:
    cutoff=parse(asof); visible=[r for r in rows if parse(r['release_at']) <= cutoff]
    latest={}
    for r in sorted(visible, key=lambda x: x['release_at']):
        latest[(r['series_id'], r['observation_date'])]=r
    return list(latest.values())

def main() -> int:
    rows=load_rows(ROOT/'p1_macro_vintage_fixture.csv')
    asof='2024-02-28T00:00:00'
    realtime=visible_asof(rows, asof)
    final=visible_asof(rows, '2025-01-01T00:00:00')
    rt={r['observation_date']:float(r['value']) for r in realtime}
    fin={r['observation_date']:float(r['value']) for r in final}
    common=sorted(set(rt)&set(fin))
    diffs=[fin[d]-rt[d] for d in common]
    result={'asof':asof,'visible_rows':len(realtime),'final_rows':len(final),
            'realtime_values':rt,'final_values':fin,'common_revision_deltas':diffs,
            'mean_abs_revision_delta':sum(abs(x) for x in diffs)/len(diffs),
            'leakage_detected': any(abs(x)>0 for x in diffs),
            'contract':'select latest release_at <= asof for each series_id, observation_date'}
    (ROOT/'p1_macro_vintage_results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2)); return 0

if __name__=='__main__': raise SystemExit(main())
