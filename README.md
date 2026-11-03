# Treasury Yield Curve & Equity Volatility

*A historical analysis of Treasury yield shocks and subsequent equity-market volatility (2010–2025).*

## Research question

How are changes in 2-year, 10-year, and 30-year U.S. Treasury yields associated with subsequent realized volatility in SPY and IWM? Does the relationship differ across shock directions, maturities, and ETFs?

## Approach

- Calculate five-trading-day Treasury yield changes and classify yield-shock conditions.
- Measure subsequent five-trading-day realized equity volatility.
- Compare SPY and IWM across Treasury maturities and shock categories.
- Estimate sampling uncertainty using bootstrap confidence intervals and Holm-adjusted hypothesis tests.
- Explore CPI-announcement-day versus non-CPI-day differences separately.

## Findings

- Sharp yield decreases were generally associated with higher subsequent realized equity volatility than sharp increases in the conditions studied.
- IWM had a higher baseline volatility; SPY showed larger *relative* responses in some comparisons.
- Effects and statistical significance varied by Treasury maturity and ETF.
- In an exploratory CPI-day analysis, the mean 2-year Treasury yield change was **2.08 bp** on CPI days versus **−0.01 bp** on other days (difference **2.09 bp**, 95% CI **0.72 to 3.45 bp**, Holm-adjusted *p* = **0.0072**; 161 CPI and 1,629 non-CPI observations).

These are historical associations, not proof of causation or a tradable forecasting edge.

## Technical implementation

| Area | Evidence in this repository |
|---|---|
| Python | Time-series alignment, event classification, response calculations, bootstrap analysis and validation (`src/`) |
| SQL / SQLite | Archived database schema, research queries and Tableau export queries (`sql/`) |
| Research data | Selected aggregate outputs and inference summaries (`data/selected_results/`) |
| Data engineering | Database-building script and database table inventory (`src/`, `docs/`) |
| Visualization | Tableau Public link will be added when published |

## Explore the results

See [`data/selected_results/`](data/selected_results/) for summary tables and [`sql/`](sql/) for analytical queries. The source code in [`src/`](src/) documents the core workflow.

**Interactive Tableau dashboard:** publication link pending.

## Reproducibility and limitations

The repository includes selected original research code and output summaries, not raw market datasets or the populated research database. Full end-to-end reproduction requires original inputs, including some intermediate event CSVs that are not included here. Certain scripts retain original project file-path assumptions; consult [`docs/methodology.md`](docs/methodology.md) before execution. Data provenance and redistribution rights should be confirmed prior to making the repository public.

The study is observational, uses overlapping time windows, and should not be interpreted as causal evidence. The CPI comparison is exploratory.
