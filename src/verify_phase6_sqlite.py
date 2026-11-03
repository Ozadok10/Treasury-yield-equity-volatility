"""Final Phase 6 SQLite QA: run documented queries and compare SQL outputs to source CSV summaries.
Run: python Research/Python/verify_phase6_sqlite.py --project-root PATH
"""
import argparse,csv,sqlite3,math
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);a=p.parse_args();root=a.project_root
 def file(name):
  matches=list(root.rglob(name))
  if len(matches)!=1:raise RuntimeError(f'Expected one {name}, got {len(matches)}')
  return matches[0]
 db=file('treasury_equity_research_2010_2025.sqlite')
 con=sqlite3.connect(db)
 checks=[]
 def record(name,ok,description):
  checks.append((name,'PASS' if ok else 'FAIL',description))
  if not ok: print('FAIL:',name,description)
 record('SQLite integrity',con.execute('PRAGMA integrity_check').fetchone()[0]=='ok','PRAGMA integrity_check')
 record('Foreign keys',len(con.execute('PRAGMA foreign_key_check').fetchall())==0,'No invalid references')
 sql=file('treasury_research_queries.sql').read_text(encoding='utf-8')
 for n,q in enumerate((part for part in sql.split(';') if part.strip()),1):
  try:
   rows=con.execute(q).fetchall();record(f'SQL query {n}',True,f'{len(rows)} output rows')
  except Exception as e:record(f'SQL query {n}',False,str(e))
 counts=con.execute('SELECT COUNT(*),SUM(valid_all_yields),SUM(research_date_eligible) FROM market_days').fetchone()
 record('Daily coverage',counts==(4024,3994,3993),str(counts))
 n=0
 for mat in (2,10,30):
  for etf in ('spy','iwm'):
   with file(f'dgs{mat}_{etf}_volatility_inference_2010_2025.csv').open(newline='') as f:
    rows=list(csv.DictReader(f))
   for r in rows:
    dbrow=con.execute('SELECT event_mean_vol_pct,normal_mean_vol_pct,p_holm FROM maturity_etf_inference WHERE maturity_years=? AND etf=? AND contrast=?',(mat,etf.upper(),r['contrast'])).fetchone()
    ok=dbrow is not None and all(math.isclose(x,float(r[y]),rel_tol=0,abs_tol=1e-8) for x,y in zip(dbrow,['event_mean_vol_pct','normal_mean_vol_pct','p_holm']))
    record(f'Inference {mat}Y {etf.upper()} {r["contrast"]}',ok,'CSV-to-SQL numerical agreement');n+=1
 with file('cpi_vs_non_cpi_inference_2012_2025.csv').open(newline='') as f: rows=list(csv.DictReader(f))
 for r in rows:
  dbrow=con.execute('SELECT cpi_mean,non_cpi_mean,p_holm FROM cpi_non_cpi_inference WHERE outcome=?',(r['outcome'],)).fetchone()
  record(f'CPI/non-CPI {r["outcome"]}',dbrow is not None and all(math.isclose(x,float(r[y]),rel_tol=0,abs_tol=1e-9) for x,y in zip(dbrow,['cpi_mean','non_cpi_mean','p_holm'])),'CSV-to-SQL numerical agreement')
 failures=[x for x in checks if x[1]!='PASS']
 print(f'PHASE 6 QA: {len(checks)-len(failures)}/{len(checks)} checks passed')
 for name,status,description in checks:print(f'{status}: {name} — {description}')
 if failures:raise SystemExit(1)
if __name__=='__main__':main()
