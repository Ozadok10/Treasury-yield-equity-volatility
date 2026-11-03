# Methodology and data notes

**Scope:** January 4, 2010 – December 31, 2025. Treasury series DGS2, DGS10, DGS30; ETF instruments SPY and IWM.

**Primary comparisons:** Five-trading-day yield changes versus subsequent five-trading-day ETF realized volatility. Contrasts are segmented by maturity, ETF, and classified yield-shock direction, using normal-event baselines.

**Statistical evidence:** Original study outputs include bootstrap confidence intervals, Holm-adjusted comparisons, and cross-maturity analysis. Check individual values in `data/selected_results/*.csv`.

**CPI extension:** The CPI-vs-non-CPI result is exploratory. The 2Y yield change comparison (161 CPI days; 1,629 other days) has 95% CI [0.7192, 3.4522] basis points and Holm-adjusted p = 0.007199 in the archived export.

**Implementation:** Python source scripts are curated original research files. The `sql/schema.sql` schema is extracted from the original research database, with analytical and Tableau export SQL retained in `sql/`. `docs/database_tables.csv` describes the actual SQLite tables.

**Reproduction requirements:** Raw inputs and some intermediate CSVs are not included in this release. The original database-building script requires a populated input directory, and some scripts reference local project paths. The files here document the actual calculations and published summary outputs, but this repository should not be described as a turnkey end-to-end reproduction package.

**Limitations:** Historical associations, non-causal interpretation, possible dependence from overlapping observation windows, and data-source/provenance restrictions. Review eligibility for redistribution before releasing additional data or workbooks.
