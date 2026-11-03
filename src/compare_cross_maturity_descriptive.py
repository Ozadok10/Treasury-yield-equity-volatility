"""Phase 4, step 1: descriptive cross-maturity comparison of existing approved outputs.
Inputs: Research/dgs{2,10,30}_{spy,iwm}_volatility_inference_2010_2025.csv
        Research/dgs{2,10,30}_five_day_events_2010_2025.csv
Output: Research/cross_maturity_descriptive_2010_2025.csv
No hypothesis testing or reclassification is performed here.
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent
results = []
for maturity in (2, 10, 30):
    events = pd.read_csv(ROOT / f'dgs{maturity}_five_day_events_2010_2025.csv')
    change = events[f'dgs{maturity}_change_5obs_bp']
    assert len(events) == 3989 and change.notna().all()
    shock_sd = float(change.std(ddof=1))
    for direction in ('sharp_decrease', 'sharp_increase'):
        selected = events.loc[events[f'dgs{maturity}_event'].eq(direction)]
        selected_eligible = selected.loc[selected['eligible_for_response_analysis']]
        for symbol in ('spy', 'iwm'):
            tests = pd.read_csv(ROOT / f'dgs{maturity}_{symbol}_volatility_inference_2010_2025.csv')
            row = tests.set_index('contrast').loc[direction + '_minus_normal']
            assert int(row['n_event']) == len(selected)
            results.append({
                'maturity_years': maturity, 'treasury_event': direction, 'etf': symbol.upper(),
                'n_treasury_events':len(selected), 'n_response_eligible_events':len(selected_eligible),
                'mean_treasury_change_bp':round(float(selected[f'dgs{maturity}_change_5obs_bp'].mean()),5),
                'mean_abs_treasury_change_bp':round(float(selected[f'dgs{maturity}_change_5obs_bp'].abs().mean()),5),
                'full_sample_5obs_yield_change_sd_bp': round(shock_sd,5),
                'mean_abs_shock_in_yield_sd_units': round(float(selected[f'dgs{maturity}_change_5obs_bp'].abs().mean())/shock_sd,5),
                'normal_mean_5d_realized_vol_pct':row['normal_mean_vol_pct'],
                'event_mean_5d_realized_vol_pct':row['event_mean_vol_pct'],
                'difference_percentage_points':row['difference_percentage_points'],
                'relative_increase_pct':row['relative_difference_pct'],
                'within_maturity_holm_p':row['p_holm'],
                'within_maturity_significant':row['holm_significant_0_05']
            })
out = pd.DataFrame(results)
assert len(out) == 12
out.to_csv(ROOT / 'cross_maturity_descriptive_2010_2025.csv', index=False)
print(out[['maturity_years','treasury_event','etf','n_response_eligible_events','mean_abs_treasury_change_bp','mean_abs_shock_in_yield_sd_units','relative_increase_pct','within_maturity_holm_p']].to_string(index=False))
print('VALIDATED: 12 summaries, 3 maturities, 2 event directions, 2 ETFs')
