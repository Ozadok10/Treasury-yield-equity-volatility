"""Phase 3: predefined IWM subsequent-volatility contrasts for DGS10 events.

Run from the project root. Uses a moving-block bootstrap of the chronological
response-eligible event table, retaining overlapping windows. Two-sided
bootstrap p values are centered at the observed statistic (null = zero).
The two sharp-vs-normal contrasts form one Holm-adjusted family.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path.cwd()
SOURCE=ROOT/'Research'/'dgs10_iwm_event_responses_2010_2025.csv'
ALIGNED=ROOT/'DATA'/'CLEAN'/'daily_market_aligned_PROVISIONAL_2010_2025.csv'
OUTPUT=ROOT/'Research'/'dgs10_iwm_volatility_inference_2010_2025.csv'
R=5000; BLOCK=20; SEED=20261029
raw=pd.read_csv(SOURCE,parse_dates=['date'])
eligible=raw.loc[raw['eligible_for_response_analysis'].astype(bool)].copy()
assert len(eligible)==3984 and eligible.date.is_unique
calendar=pd.read_csv(ALIGNED,usecols=['date'],parse_dates=['date']).sort_values('date')
assert len(calendar)==4024 and calendar.date.is_unique
df=calendar.merge(eligible[['date','dgs10_event','following_iwm_5d_realized_vol_pct']],on='date',how='left',validate='one_to_one')
labels=df['dgs10_event'].fillna('ineligible').to_numpy()
vol=df['following_iwm_5d_realized_vol_pct'].to_numpy(float)
assert set(labels)=={'sharp_decrease','sharp_increase','normal','ineligible'}
conditions=['sharp_decrease','sharp_increase','normal']
counts={k:int((labels==k).sum()) for k in conditions}
means={k:float(np.mean(vol[labels==k])) for k in conditions}
assert sum(counts.values())==3984
print('Samples:',counts)
print('Mean subsequent realized vol (%):',means)
N=len(df); rng=np.random.default_rng(SEED)
# Index each resample as stitched consecutive blocks of original rows.
boot=np.empty((R,2),dtype=float)
for k in range(R):
    starts=rng.integers(0,N-BLOCK+1,size=(N+BLOCK-1)//BLOCK)
    ind=(starts[:,None]+np.arange(BLOCK)).ravel()[:N]
    lb=labels[ind]; v=vol[ind]
    norm=v[lb=='normal'].mean()
    boot[k,0]=v[lb=='sharp_decrease'].mean()-norm
    boot[k,1]=v[lb=='sharp_increase'].mean()-norm
observed=np.array([means['sharp_decrease']-means['normal'],means['sharp_increase']-means['normal']])
# centered bootstrap tail probability for H0: difference = 0; finite-sample correction
p=np.array([(1+np.sum(np.abs(boot[:,i]-observed[i])>=abs(observed[i])))/(R+1) for i in range(2)])
order=np.argsort(p)
adj=np.empty(2)
max_so_far=0.
for rank, j in enumerate(order):
    max_so_far=max(max_so_far,min(1.,p[j]*(2-rank)))
    adj[j]=max_so_far
rows=[]
for i,c in enumerate(conditions[:2]):
    lo,hi=np.percentile(boot[:,i],[2.5,97.5])
    rows.append({'contrast':f'{c}_minus_normal','n_event':counts[c],'n_normal':counts['normal'],
      'event_mean_vol_pct':means[c],'normal_mean_vol_pct':means['normal'],
      'difference_percentage_points':observed[i],
      'relative_difference_pct':100*observed[i]/means['normal'],
      'ci_95_low_pp':lo,'ci_95_high_pp':hi,
      'p_bootstrap_two_sided':p[i],'p_holm':adj[i],
      'holm_significant_0_05':bool(adj[i]<0.05),
      'bootstrap_resamples':R,'block_length_equity_sessions':BLOCK,'random_seed':SEED})
out=pd.DataFrame(rows)
OUTPUT.parent.mkdir(parents=True,exist_ok=True)
out.to_csv(OUTPUT,index=False,float_format='%.8f')
print(out.to_string(index=False))
print('Saved:',OUTPUT)
