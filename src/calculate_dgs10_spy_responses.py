"""Phase 3: descriptive SPY response measurements for locked DGS10 events.
Run from project root. No statistical inference or new event definitions.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path.cwd()
ALIGNED = ROOT / 'DATA/CLEAN/daily_market_aligned_PROVISIONAL_2010_2025.csv'
EVENTS = ROOT / 'Research/dgs10_five_day_events_2010_2025.csv'
OUTPUT = ROOT / 'Research/dgs10_spy_event_responses_2010_2025.csv'
SOURCE_RETURN = 'SPY_return_dividend_inclusive_log_PROVISIONAL'

market = pd.read_csv(ALIGNED, parse_dates=['date'])
events = pd.read_csv(EVENTS, parse_dates=['date'])
assert len(market) == 4024 and market.date.is_unique and market.date.is_monotonic_increasing
assert len(events) == 3989 and events.date.is_unique
assert set(events.date).issubset(set(market.date))
r = market[SOURCE_RETURN].to_numpy(dtype=float)
idx = pd.Series(np.arange(len(market)), index=market.date)
records = []
for ev in events.itertuples(index=False):
    i = int(idx[ev.date]); row = {'date':ev.date, 'dgs10_change_5obs_bp':ev.dgs10_change_5obs_bp, 'dgs10_event':ev.dgs10_event,
                                    'eligible_for_response_analysis':bool(ev.eligible_for_response_analysis)}
    during = r[i-4:i+1] if i>=4 else np.array([])
    after = r[i+1:i+6] if i+5<len(r) else np.array([])
    row['during_spy_5d_log_return_pct'] = 100*float(np.sum(during)) if len(during)==5 and np.isfinite(during).all() else np.nan
    row['during_spy_5d_realized_vol_pct'] = 100*float(np.std(during, ddof=1)) if len(during)==5 and np.isfinite(during).all() else np.nan
    row['following_spy_5d_log_return_pct'] = 100*float(np.sum(after)) if len(after)==5 and np.isfinite(after).all() else np.nan
    row['following_spy_5d_realized_vol_pct'] = 100*float(np.std(after, ddof=1)) if len(after)==5 and np.isfinite(after).all() else np.nan
    assert row['eligible_for_response_analysis'] == np.isfinite(row['following_spy_5d_realized_vol_pct'])
    records.append(row)
out = pd.DataFrame.from_records(records)
assert len(out)==3989 and out.eligible_for_response_analysis.sum()==3984
assert out.loc[out.eligible_for_response_analysis, [
    'during_spy_5d_log_return_pct','during_spy_5d_realized_vol_pct',
    'following_spy_5d_log_return_pct','following_spy_5d_realized_vol_pct']].notna().all().all()
OUTPUT.parent.mkdir(exist_ok=True, parents=True)
out.to_csv(OUTPUT,index=False,date_format='%Y-%m-%d',float_format='%.10f')
print('Saved:', OUTPUT)
valid=out[out.eligible_for_response_analysis]
print('Counts:',valid.dgs10_event.value_counts().to_dict())
print(valid.groupby('dgs10_event').agg(n=('date','size'),during_return_mean=('during_spy_5d_log_return_pct','mean'),during_vol_mean=('during_spy_5d_realized_vol_pct','mean'),after_return_mean=('following_spy_5d_log_return_pct','mean'),after_vol_mean=('following_spy_5d_realized_vol_pct','mean'),after_vol_median=('following_spy_5d_realized_vol_pct','median')).round(4).to_string())
