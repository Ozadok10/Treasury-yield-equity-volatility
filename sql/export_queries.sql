-- treasury_yields.csv
SELECT date,maturity,yield_pct FROM treasury_yields ORDER BY date,maturity;

-- etf_daily.csv
SELECT date,etf,close_rth,log_return,distribution,late_start,early_end,source_frequency FROM etf_daily ORDER BY date,etf;

-- treasury_event_responses.csv
SELECT e.date,e.maturity_years,e.yield_change_bp,e.event_class,e.eligible_for_response_analysis,r.etf,r.during_return_pct,r.during_vol_pct,r.following_return_pct,r.following_vol_pct FROM treasury_events e INNER JOIN etf_event_responses r ON e.date=r.date AND e.maturity_years=r.maturity_years ORDER BY e.date,e.maturity_years,r.etf;

-- maturity_etf_inference.csv
SELECT * FROM maturity_etf_inference ORDER BY maturity_years,etf,contrast;

-- etf_sensitivity_comparisons.csv
SELECT * FROM etf_sensitivity_comparisons ORDER BY maturity_years,contrast;

-- cross_maturity_descriptive.csv
SELECT * FROM cross_maturity_descriptive ORDER BY maturity_years,treasury_event,etf;

-- cross_maturity_inference.csv
SELECT * FROM cross_maturity_inference ORDER BY etf,direction,contrast;

-- cpi_non_cpi_inference.csv
SELECT * FROM cpi_non_cpi_inference ORDER BY outcome;

