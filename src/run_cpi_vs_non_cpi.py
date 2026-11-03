"""CPI vs non-CPI five-session comparison. Permanent: Research/CPI/.
Inputs: DATA/RAW/cpi_consensus_PROVISIONAL_2010_2025.csv and
DATA/CLEAN/daily_market_aligned_PROVISIONAL_2010_2025.csv.
Outputs: Research/CPI/cpi_vs_non_cpi_event_windows_2012_2025.csv,
Research/CPI/cpi_vs_non_cpi_inference_2012_2025.csv.
Uses 5,000 moving-block bootstrap replications, block size 20 equity sessions.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2] if Path(__file__).resolve().parent.name=='CPI' else Path('/mnt/data')
market_path=ROOT/'DATA/CLEAN/daily_market_aligned_PROVISIONAL_2010_2025.csv'
cpi_path=ROOT/'DATA/RAW/cpi_consensus_PROVISIONAL_2010_2025.csv'
if not market_path.exists(): market_path=Path('/mnt/data/daily_market_aligned_PROVISIONAL_2010_2025(1).csv')
if not cpi_path.exists(): cpi_path=Path('/mnt/data/cpi_consensus_PROVISIONAL_2010_2025(3).csv')
outdir=Path(__file__).resolve().parent if Path(__file__).resolve().parent.name=='CPI' else Path('/mnt/data')
m=pd.read_csv(market_path,parse_dates=['date']).sort_values('date').reset_index(drop=True)
c=pd.read_csv(cpi_path)
c['release_date']=pd.to_datetime(c['release_date'])
assert m['date'].is_unique and m['date'].is_monotonic_increasing and c['release_date'].is_unique
n=len(m); idx={d:i for i,d in enumerate(m.date)}
# Scope control: comparison uses the CPI-overlap period, not pre-2012 historical controls.
first,last=c.release_date.min(),c.release_date.max()
cols=['DGS2','DGS10','DGS30']
for col in cols: m[col]=pd.to_numeric(m[col],errors='coerce')
# Five subsequent *valid Treasury* observations for yields; five next equity sessions for volatility.
valid=np.where(m[cols].notna().all(axis=1))[0]
rank=np.searchsorted(valid,np.arange(n),side='right')
end=np.full(n,-1,dtype=int)
for i in range(n):
    if m.loc[i,cols].notna().all() and rank[i]+4<len(valid):end[i]=valid[rank[i]+4]
returns={ticker:pd.to_numeric(m[f'{ticker}_return_dividend_inclusive_log_PROVISIONAL'],errors='coerce').to_numpy() for ticker in ['SPY','IWM']}
features={k:np.full(n,np.nan) for k in ['DGS2_bp','DGS10_bp','DGS30_bp','SPY_vol_pct','IWM_vol_pct']}
for i in range(n-5):
    if end[i]<0 or not all(np.isfinite(v[i+1:i+6]).all() for v in returns.values()): continue
    for col in cols:features[col+'_bp'][i]=100*(m.at[end[i],col]-m.at[i,col])
    for ticker in ['SPY','IWM']:features[ticker+'_vol_pct'][i]=100*np.std(returns[ticker][i+1:i+6],ddof=1)
valid_window=np.isfinite(np.column_stack(list(features.values()))).all(axis=1)
# The approved primary CPI sample: release date must be an actual equity session.
primary_idx=np.array([idx[d] for d in c.release_date if d in idx],dtype=int)
assert len(primary_idx)==161
# For off-calendar CPI dates, conservatively anchor to the first subsequent equity session
# for contamination exclusion ONLY; retain their exclusion from the CPI treatment sample.
all_anchor=np.array([idx[d] if d in idx else np.searchsorted(m.date.to_numpy(),np.datetime64(d),'left') for d in c.release_date],dtype=int)
assert len(all_anchor)==163
# A control observation window [t,t+5] cannot intersect any CPI influence window [a,a+5].
contaminated=np.zeros(n,dtype=bool)
for a in all_anchor:
    contaminated[max(0,a-5):min(n,a+6)]=True
primary=np.zeros(n,dtype=bool);primary[primary_idx]=True
scope=(m.date>=first)&(m.date<=last)
controls=scope.to_numpy()&valid_window&~contaminated
assert (controls&primary).sum()==0
assert valid_window[primary_idx].all()
frame=pd.DataFrame({'date':m.date.dt.strftime('%Y-%m-%d'),'group':np.where(primary,'CPI',np.where(controls,'NON_CPI','EXCLUDED')),'cpi_primary':primary,'control_eligible':controls,'cpi_contamination_flag':contaminated,'complete_response_window':valid_window})
for k,v in features.items():frame[k]=v
frame=frame.loc[primary|controls].reset_index(drop=True)
assert (frame.group=='CPI').sum()==161
frame.to_csv(outdir/'cpi_vs_non_cpi_event_windows_2012_2025.csv',index=False)
# Bootstrap paired calendar series (event grouping + responses) via 20-day blocks,
# retaining calendar-time dependence; fixed observed sample length and eligible group labels.
labels=np.zeros(n,dtype=np.int8);labels[primary]=1;labels[controls]=2
feature_names=list(features)
mat=np.column_stack([features[k] for k in feature_names]); mat=np.where(np.isfinite(mat),mat,0)
B=5000;block=20;rng=np.random.default_rng(20261029)
# Restrict bootstrap to CPI-era trading-session calendar (including excluded rows).
start=int(np.where(m.date>=first)[0][0]);stop=int(np.where(m.date<=last)[0][-1])+1
L=stop-start
obs=[];boots=np.full((B,len(feature_names)),np.nan)
for j,name in enumerate(feature_names):
    x=features[name];a=x[primary];b=x[controls]
    obs.append({'outcome':name,'cpi_n':len(a),'non_cpi_n':len(b),'cpi_mean':a.mean(),'non_cpi_mean':b.mean(),'difference_cpi_minus_non_cpi':a.mean()-b.mean(),'cpi_median':np.median(a),'non_cpi_median':np.median(b),'unit':'bp' if name.endswith('_bp') else 'volatility percentage points'})
for z in range(B):
    chunks=(L+block-1)//block
    starts=rng.integers(start,stop-block+1,size=chunks)
    sample=(starts[:,None]+np.arange(block)).reshape(-1)[:L]
    lab=labels[sample];aa=lab==1;bb=lab==2
    if aa.sum()<5 or bb.sum()<20:continue
    v=mat[sample]
    boots[z]=v[aa].mean(axis=0)-v[bb].mean(axis=0)
res=pd.DataFrame(obs)
# Two-sided centered bootstrap test: estimate null distribution by subtracting observed effect.
pvals=[]
for j in range(len(feature_names)):
    v=boots[:,j];v=v[np.isfinite(v)];d=res.loc[j,'difference_cpi_minus_non_cpi']
    lo,hi=np.percentile(v,[2.5,97.5]);p=(1+np.count_nonzero(np.abs(v-d)>=abs(d)))/(len(v)+1)
    res.loc[j,'ci95_low']=lo;res.loc[j,'ci95_high']=hi;res.loc[j,'p_unadjusted']=p
# Locked hypothesis families prior to inferential inspection: yield changes (3), ETF volatility (2).
res['family']=['treasury_yields']*3+['equity_volatility']*2
res['p_holm']=np.nan
for family,ids in res.groupby('family').groups.items():
    order=sorted(ids,key=lambda i:res.loc[i,'p_unadjusted']);running=0
    for k,i in enumerate(order):
        running=max(running,(len(order)-k)*res.loc[i,'p_unadjusted']);res.loc[i,'p_holm']=min(1,running)
res['significant_holm_005']=res.p_holm<0.05
res.to_csv(outdir/'cpi_vs_non_cpi_inference_2012_2025.csv',index=False)
print('CPI',int(primary.sum()),'non-CPI',int(controls.sum()),'holiday exceptions',len(all_anchor)-len(primary_idx),'bootstrap valid',int(np.isfinite(boots[:,0]).sum()))
print(res[['outcome','cpi_mean','non_cpi_mean','difference_cpi_minus_non_cpi','ci95_low','ci95_high','p_unadjusted','p_holm','significant_holm_005']].to_string(index=False))
