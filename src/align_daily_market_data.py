"""Phase 2 / Step 3: reproducibly align daily SPY/IWM and FRED Treasury yields.
Run from the project Research folder; input folders are DATA/CLEAN and DATA/RAW.
No interpolation or forward-filling is performed. Provisional dividend returns stay flagged.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'DATA' / 'RAW'
CLEAN = ROOT / 'DATA' / 'CLEAN'
EQUITY = CLEAN / 'equity_daily_dividend_inclusive_PROVISIONAL_2010_2025.csv'
START, END = '2010-01-04', '2025-12-31'


def create_aligned_dataset():
    e = pd.read_csv(EQUITY, parse_dates=['date'])
    e = e[e['date'].between(START, END)].copy()
    if e.duplicated(['symbol','date']).any():
        raise ValueError('Duplicate equity symbol/date records')
    if e['close_rth'].isna().any():
        raise ValueError('Missing daily closing prices')
    fields = ['close_rth','return_dividend_inclusive_log_PROVISIONAL','distribution','late_start','early_end','frequency']
    parts = []
    for symbol in ('SPY','IWM'):
        d = e.loc[e.symbol.eq(symbol), ['date'] + fields].set_index('date')
        if d.empty:
            raise ValueError(f'No {symbol} records')
        parts.append(d.rename(columns={x: f'{symbol}_{x}' for x in fields}))
    equity = parts[0].join(parts[1], how='inner')
    treasuries = []
    for series in ('DGS2','DGS10','DGS30'):
        df = pd.read_csv(RAW / f'{series}.csv', parse_dates=['observation_date'], na_values=['.'])
        df = df.rename(columns={'observation_date':'date'}).set_index('date')[[series]]
        if df.index.has_duplicates:
            raise ValueError(f'Duplicate {series} dates')
        treasuries.append(df)
    yields = pd.concat(treasuries, axis=1)
    yields = yields.loc[START:END]
    aligned = equity.join(yields, how='left').sort_index()
    aligned['valid_all_yields'] = aligned[['DGS2','DGS10','DGS30']].notna().all(axis=1)
    aligned['valid_equity_returns'] = aligned[['SPY_return_dividend_inclusive_log_PROVISIONAL','IWM_return_dividend_inclusive_log_PROVISIONAL']].notna().all(axis=1)
    aligned['research_date_eligible'] = aligned['valid_all_yields'] & aligned['valid_equity_returns']
    # Preserve the full equity-date timeline; event/window selection occurs after validation.
    out = CLEAN / 'daily_market_aligned_PROVISIONAL_2010_2025.csv'
    aligned.reset_index().to_csv(out, index=False, date_format='%Y-%m-%d')
    print(f'Wrote: {out}')
    print(f'Equity-aligned sessions: {len(aligned)}')
    print(f'Sessions with all 3 yields: {int(aligned.valid_all_yields.sum())}')
    print(f'Sessions with all 3 yields and both returns: {int(aligned.research_date_eligible.sum())}')
    print('Unavailable-yield equity dates:', aligned.index[~aligned.valid_all_yields].strftime('%Y-%m-%d').tolist())
    return aligned

if __name__ == '__main__':
    create_aligned_dataset()
