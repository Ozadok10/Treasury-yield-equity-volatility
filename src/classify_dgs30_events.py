"""Classify 30-year Treasury five-valid-observation yield changes.
Run from Treasury_Yield_Curve_Equity_Volatility_Research root.
Whole-sample decile thresholds are retrospective research groupings, not live signals.
"""
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path.cwd()
SRC=ROOT/'DATA'/'CLEAN'/'daily_market_aligned_PROVISIONAL_2010_2025.csv'
DEST=ROOT/'Research'/'dgs30_five_day_events_2010_2025.csv'
df=pd.read_csv(SRC,parse_dates=['date']).sort_values('date').reset_index(drop=True)
assert len(df)==4024 and df.date.is_unique and df.date.is_monotonic_increasing
v=df.loc[df.valid_all_yields.astype(bool)].copy()
assert len(v)==3994
v['dgs30_change_5obs_bp']=((v.DGS30-v.DGS30.shift(5))*100).round(6)
c=v.dgs30_change_5obs_bp.dropna()
low,high=c.quantile([.1,.9]).tolist()
v['dgs30_event']=np.select([v.dgs30_change_5obs_bp<=low,v.dgs30_change_5obs_bp>=high],['sharp_decrease','sharp_increase'],default='normal')
v.loc[v.dgs30_change_5obs_bp.isna(),'dgs30_event']='warmup_insufficient_history'
returns_ok=df[['SPY_return_dividend_inclusive_log_PROVISIONAL','IWM_return_dividend_inclusive_log_PROVISIONAL']].notna().all(axis=1)
future_ok=pd.Series(False,index=df.index)
for j in range(len(df)-5): future_ok.iloc[j]=bool(returns_ok.iloc[j+1:j+6].all())
v['has_next_5_equity_returns']=future_ok.loc[v.index].to_numpy()
v['eligible_for_response_analysis']=v.dgs30_change_5obs_bp.notna() & v.has_next_5_equity_returns
out=v.loc[v.dgs30_change_5obs_bp.notna(),['date','DGS30','dgs30_change_5obs_bp','dgs30_event','has_next_5_equity_returns','eligible_for_response_analysis']]
assert len(out)==3989 and out.eligible_for_response_analysis.sum()==3984
assert out.date.is_unique and (out.date.diff().dropna()>pd.Timedelta(0)).all()
assert (out.dgs30_event=='sharp_decrease').sum()>=399 and (out.dgs30_event=='sharp_increase').sum()>=399
DEST.parent.mkdir(exist_ok=True,parents=True)
out.to_csv(DEST,index=False,date_format='%Y-%m-%d')
print('10th,90th percentile bp:',low,high)
print('Full classified:',out.dgs30_event.value_counts().to_dict())
print('Response eligible:',out.loc[out.eligible_for_response_analysis,'dgs30_event'].value_counts().to_dict())
print('Saved:',DEST)
