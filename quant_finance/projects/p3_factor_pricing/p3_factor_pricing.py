#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, io, json, urllib.request, zipfile
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
FACTOR_URL='https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip'
PORT_URL='https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/25_Portfolios_5x5_CSV.zip'

def download_zip(url):
    data=urllib.request.urlopen(url,timeout=30).read(); sha=hashlib.sha256(data).hexdigest()
    z=zipfile.ZipFile(io.BytesIO(data)); text=z.read(z.namelist()[0]).decode('utf-8')
    return text,sha

def parse_monthly(text, header_contains):
    lines=text.splitlines(); start=next(i for i,s in enumerate(lines) if header_contains in s)
    header=next(i for i in range(start,len(lines)) if lines[i].lstrip().startswith(','))
    names=['date']+[x.strip() for x in next(csv.reader([lines[header]]))[1:]]; rows=[]
    for line in lines[header+1:]:
        if not line.strip(): break
        parts=next(csv.reader([line])); key=parts[0].strip()
        if len(key)!=6 or not key.isdigit(): break
        vals=[float(x.strip())/100 for x in parts[1:]]
        if any(v<=-0.999 for v in vals): continue
        rows.append((key,vals))
    return names,rows

def ols(y,x): return np.linalg.lstsq(x,y,rcond=None)[0]

def main():
    factor_text,fsha=download_zip(FACTOR_URL); port_text,psha=download_zip(PORT_URL)
    fn,fr=parse_monthly(factor_text,'Mkt-RF'); pn,pr=parse_monthly(port_text,'Average Value Weighted Returns -- Monthly')
    fdict={d:v for d,v in fr}; pdict={d:v for d,v in pr}; dates=sorted(set(fdict)&set(pdict))
    f=np.asarray([fdict[d] for d in dates]); p=np.asarray([pdict[d] for d in dates]); excess=p-f[:,3,None]
    capm_x=np.column_stack([np.ones(len(dates)),f[:,0]])
    ff3_x=np.column_stack([np.ones(len(dates)),f[:,:3]])
    capm=np.vstack([ols(excess[:,i],capm_x) for i in range(excess.shape[1])])
    ff3=np.vstack([ols(excess[:,i],ff3_x) for i in range(excess.shape[1])])
    result={'factor_url':FACTOR_URL,'portfolio_url':PORT_URL,'factor_sha256':fsha,'portfolio_sha256':psha,
      'factor_source_note':factor_text.splitlines()[0],'portfolio_source_note':port_text.splitlines()[0],
      'sample_start':dates[0],'sample_end':dates[-1],'n_months':len(dates),'n_portfolios':excess.shape[1],
      'units':'source percent converted to decimal; portfolio excess return subtracts RF',
      'capm_mean_abs_monthly_alpha':float(np.mean(np.abs(capm[:,0]))),
      'ff3_mean_abs_monthly_alpha':float(np.mean(np.abs(ff3[:,0]))),
      'ff3_max_abs_monthly_alpha':float(np.max(np.abs(ff3[:,0]))),
      'evidence_boundary':'official public files downloaded and hashed; no raw redistribution, causal, or tradability claim'}
    (ROOT/'p3_factor_pricing_results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False)); return 0
if __name__=='__main__': raise SystemExit(main())
