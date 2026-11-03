"""Phase 3 / Step 1: classify five-valid-Treasury-observation DGS2 movements.
Run from the root Treasury_Yield_Curve_Equity_Volatility_Research directory.
Retrospective whole-sample percentile thresholds; classifications are not live signals.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path.cwd()
SOURCE = ROOT / 'DATA' / 'CLEAN' / 'daily_market_aligned_PROVISIONAL_2010_2025.csv'
DEST = ROOT / 'Research' / 'dgs2_five_day_events_2010_2025.csv'
df = pd.read_csv(SOURCE, parse_dates=['date']).sort_values('date').reset_index(drop=True)
assert len(df) == 4024 and df.date.is_unique
assert df.date.is_monotonic_increasing
valid = df[df['valid_all_yields'].astype(bool)].copy()
assert len(valid) == 3994
# Five prior valid Treasury *observations*; do not impute missing publication dates.
valid['dgs2_change_5obs_bp'] = ((valid['DGS2'] - valid['DGS2'].shift(5)) * 100).round(6)
changes = valid['dgs2_change_5obs_bp'].dropna()
low, high = changes.quantile([.10, .90]).tolist()
assert np.isclose(low, -9) and np.isclose(high, 10)
valid['dgs2_event'] = np.select(
    [valid['dgs2_change_5obs_bp'] <= low, valid['dgs2_change_5obs_bp'] >= high],
    ['sharp_decrease', 'sharp_increase'], default='normal')
valid.loc[valid['dgs2_change_5obs_bp'].isna(), 'dgs2_event'] = 'warmup_insufficient_history'
# ETF response is measured on the next five *equity* sessions, not necessarily Treasury dates.
returns_ok = df[[
    'SPY_return_dividend_inclusive_log_PROVISIONAL',
    'IWM_return_dividend_inclusive_log_PROVISIONAL'
]].notna().all(axis=1)
# At index i, all next five equity session returns must be available.
future_ok = pd.Series(False, index=df.index)
for i in range(len(df) - 5):
    future_ok.iloc[i] = bool(returns_ok.iloc[i + 1:i + 6].all())
valid['has_next_5_equity_returns'] = valid.index.map(lambda idx: bool(future_ok.loc[idx]))
valid['eligible_for_response_analysis'] = valid['dgs2_change_5obs_bp'].notna() & valid['has_next_5_equity_returns']
cols = ['date', 'DGS2', 'dgs2_change_5obs_bp', 'dgs2_event',
        'has_next_5_equity_returns', 'eligible_for_response_analysis']
result = valid.loc[valid['dgs2_change_5obs_bp'].notna(), cols]
assert len(result) == 3989
assert result['eligible_for_response_analysis'].sum() == 3984
assert result['dgs2_event'].value_counts().to_dict() == {
    'normal': 3101, 'sharp_decrease': 445, 'sharp_increase': 443}
assert result.loc[result['eligible_for_response_analysis'], 'date'].max() == pd.Timestamp('2025-12-23')
DEST.parent.mkdir(parents=True, exist_ok=True)
result.to_csv(DEST, index=False, date_format='%Y-%m-%d')
print(f'Input: {SOURCE}\nOutput: {DEST}')
print(f'DGS2 percentile cutoffs: 10th={low:.0f} bp, 90th={high:.0f} bp')
print(f'Classified: {len(result):,} | response-eligible: {int(result.eligible_for_response_analysis.sum()):,}')
print(result.dgs2_event.value_counts().to_string())
