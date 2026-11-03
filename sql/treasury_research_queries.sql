-- Phase 6: Research validation and Tableau-ready queries.
-- 1. Dataset coverage
SELECT COUNT(*) AS equity_sessions, SUM(valid_all_yields) AS all_yields_present,
       SUM(research_date_eligible) AS research_eligible
FROM market_days;

-- 2. Extreme Treasury event counts
SELECT maturity_years, event_class, COUNT(*) AS n
FROM treasury_events GROUP BY maturity_years,event_class
ORDER BY maturity_years,event_class;

-- 3. Mean next-five-day SPY/IWM volatility by maturity and event category
SELECT e.maturity_years, e.event_class, r.etf, COUNT(r.following_vol_pct) AS n,
       ROUND(AVG(r.following_vol_pct),4) AS subsequent_volatility_pct
FROM treasury_events e
JOIN etf_event_responses r ON r.date=e.date AND r.maturity_years=e.maturity_years
WHERE e.eligible_for_response_analysis=1
GROUP BY e.maturity_years,e.event_class,r.etf
ORDER BY e.maturity_years,e.event_class,r.etf;

-- 4. Inference results: source-of-truth p-values and confidence intervals
SELECT maturity_years,etf,contrast,difference_percentage_points,
       relative_difference_pct,ci_95_low_pp,ci_95_high_pp,p_holm
FROM maturity_etf_inference
ORDER BY maturity_years,etf,contrast;

-- 5. CPI category counts (inclusive of flagged non-session events)
SELECT surprise_class,COUNT(*) AS n FROM cpi_events GROUP BY surprise_class;

-- 6. Approved CPI versus non-CPI inference results
SELECT outcome,cpi_n,non_cpi_n,cpi_mean,non_cpi_mean,
       difference_cpi_minus_non_cpi,ci95_low,ci95_high,p_holm
FROM cpi_non_cpi_inference ORDER BY outcome;
