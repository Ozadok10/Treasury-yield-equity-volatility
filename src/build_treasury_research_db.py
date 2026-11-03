"""Phase 6 reproducible SQLite build. Run with --input-dir PATH --output PATH.
Uses existing research CSVs only; no data acquisition or recomputation of inference.
"""
import argparse
import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent


def load(folder, name):
    files = list(folder.rglob(name))
    if len(files) != 1:
        raise FileNotFoundError(f'Expected exactly one {name} in {folder}; found {len(files)}')
    return pd.read_csv(files[0], dtype={'date':str, 'release_date':str})


def write(conn, name, frame):
    frame.to_sql(name, conn, if_exists='replace', index=False)
    return len(frame)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', type=Path, default=ROOT, help='Project root containing existing CSVs in Research/ and DATA/CLEAN/')
    parser.add_argument('--output', type=Path, default=ROOT/'treasury_equity_research_2010_2025.sqlite')
    args = parser.parse_args()
    folder=args.input_dir
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists():
        args.output.unlink()
    con=sqlite3.connect(args.output)
    con.execute('PRAGMA foreign_keys=ON')
    market=load(folder,'daily_market_aligned_PROVISIONAL_2010_2025*.csv')
    assert len(market)==4024 and market.date.is_unique and market.date.is_monotonic_increasing
    market_day=market[['date','valid_all_yields','valid_equity_returns','research_date_eligible']].copy()
    write(con,'market_days',market_day)
    yields=market.melt(id_vars='date',value_vars=['DGS2','DGS10','DGS30'],var_name='maturity',value_name='yield_pct')
    write(con,'treasury_yields',yields)
    equities=[]
    for etf in ('SPY','IWM'):
        d=market[['date',f'{etf}_close_rth',f'{etf}_return_dividend_inclusive_log_PROVISIONAL',f'{etf}_distribution',f'{etf}_late_start',f'{etf}_early_end',f'{etf}_frequency']].copy()
        d.columns=['date','close_rth','log_return','distribution','late_start','early_end','source_frequency']
        d.insert(1,'etf',etf)
        equities.append(d)
    write(con,'etf_daily',pd.concat(equities,ignore_index=True))
    events=[];responses=[];inferences=[];comparisons=[]
    for mat in (2,10,30):
        ev=load(folder,f'dgs{mat}_five_day_events_2010_2025.csv')
        ev=ev[['date',f'dgs{mat}_change_5obs_bp',f'dgs{mat}_event','eligible_for_response_analysis']].copy()
        ev.columns=['date','yield_change_bp','event_class','eligible_for_response_analysis']
        ev.insert(1,'maturity_years',mat)
        events.append(ev)
        for etf in ('spy','iwm'):
            r=load(folder,f'dgs{mat}_{etf}_event_responses_2010_2025.csv')
            keep=['date',f'during_{etf}_5d_log_return_pct',f'during_{etf}_5d_realized_vol_pct',f'following_{etf}_5d_log_return_pct',f'following_{etf}_5d_realized_vol_pct']
            r=r[keep].copy()
            r.columns=['date','during_return_pct','during_vol_pct','following_return_pct','following_vol_pct']
            r.insert(1,'maturity_years',mat);r.insert(2,'etf',etf.upper())
            responses.append(r)
            x=load(folder,f'dgs{mat}_{etf}_volatility_inference_2010_2025.csv')
            x.insert(0,'maturity_years',mat);x.insert(1,'etf',etf.upper())
            inferences.append(x)
        comp=load(folder,f'dgs{mat}_spy_iwm_sensitivity_comparison_2010_2025.csv')
        comp.insert(0,'maturity_years',mat)
        comparisons.append(comp)
    write(con,'treasury_events',pd.concat(events,ignore_index=True))
    write(con,'etf_event_responses',pd.concat(responses,ignore_index=True))
    write(con,'maturity_etf_inference',pd.concat(inferences,ignore_index=True))
    write(con,'etf_sensitivity_comparisons',pd.concat(comparisons,ignore_index=True))
    for table,filename in (
        ('cross_maturity_descriptive','cross_maturity_descriptive_2010_2025.csv'),
        ('cross_maturity_inference','cross_maturity_inference_2010_2025.csv'),
        ('yield_curve_spreads','yield_curve_spreads_2010_2025.csv'),
        ('joint_yield_events','phase5_joint_sharp_events_2010_2025.csv'),
        ('cpi_events','cpi_event_alignment_2012_2025.csv'),
        ('cpi_treasury_responses','cpi_treasury_event_responses_2012_2025.csv'),
        ('cpi_equity_responses','cpi_equity_volatility_event_responses_2012_2025.csv'),
        ('cpi_three_way_descriptive','cpi_three_way_descriptive_2012_2025.csv'),
        ('cpi_inference','cpi_step5_inference_2012_2025.csv'),
        ('cpi_non_cpi_windows','cpi_vs_non_cpi_event_windows_2012_2025.csv'),
        ('cpi_non_cpi_inference','cpi_vs_non_cpi_inference_2012_2025.csv'),
    ):
        write(con,table,load(folder,filename))
    # Phase 5 inference is packaged in the existing approved research ZIP.
    import zipfile,io
    z=folder/'phase5_interaction_tests_complete.zip'
    if z.exists():
        with zipfile.ZipFile(z) as arc:
            hits=[n for n in arc.namelist() if n.endswith('phase5_interaction_inference_2010_2025.csv')]
            if len(hits)==1:
                write(con,'joint_curve_inference',pd.read_csv(io.BytesIO(arc.read(hits[0]))))
    for table,cols in [('market_days','date'),('treasury_yields','date,maturity'),('etf_daily','date,etf'),('treasury_events','date,maturity_years'),('etf_event_responses','date,maturity_years,etf'),('cpi_events','release_date')]:
        con.execute(f'CREATE UNIQUE INDEX idx_{table}_key ON {table} ({cols})')
    con.execute('CREATE INDEX idx_treasury_class ON treasury_events(maturity_years,event_class)')
    con.execute('CREATE INDEX idx_cpi_class ON cpi_events(surprise_class)')
    con.commit()
    def count(t):return con.execute(f'SELECT count(*) FROM {t}').fetchone()[0]
    assert count('market_days')==4024
    assert count('treasury_yields')==12072
    assert count('etf_daily')==8048
    assert count('treasury_events')==3*3989
    assert count('etf_event_responses')==6*3989
    assert count('cpi_events')==163
    assert count('cpi_non_cpi_windows')==1790
    assert con.execute('SELECT COUNT(*) FROM treasury_yields WHERE yield_pct IS NULL').fetchone()[0]==90
    assert con.execute('SELECT COUNT(*) FROM market_days WHERE valid_all_yields=1').fetchone()[0]==3994
    assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    print('DB',args.output)
    for tbl in ['market_days','treasury_yields','etf_daily','treasury_events','etf_event_responses','maturity_etf_inference','cpi_events','cpi_non_cpi_windows']:
        print(tbl, count(tbl))
    print('integrity_check ok')
    con.close()

if __name__=='__main__':main()
