-- Original SQLite schema extracted read-only; not a rebuild script

CREATE INDEX idx_cpi_class ON cpi_events(surprise_class);

CREATE UNIQUE INDEX idx_cpi_events_key ON cpi_events (release_date);

CREATE UNIQUE INDEX idx_etf_daily_key ON etf_daily (date,etf);

CREATE UNIQUE INDEX idx_etf_event_responses_key ON etf_event_responses (date,maturity_years,etf);

CREATE UNIQUE INDEX idx_market_days_key ON market_days (date);

CREATE INDEX idx_treasury_class ON treasury_events(maturity_years,event_class);

CREATE UNIQUE INDEX idx_treasury_events_key ON treasury_events (date,maturity_years);

CREATE UNIQUE INDEX idx_treasury_yields_key ON treasury_yields (date,maturity);

CREATE TABLE "cpi_equity_responses" (
"release_date" TEXT,
  "surprise_class" TEXT,
  "surprise_percentage_points" REAL,
  "actual_yoy_pct" REAL,
  "forecast_yoy_pct" REAL,
  "alignment_status" TEXT,
  "primary_eligible" INTEGER,
  "SPY_next5_realized_vol_pct" REAL,
  "IWM_next5_realized_vol_pct" REAL
);

CREATE TABLE "cpi_events" (
"release_date" TEXT,
  "release_datetime_utc" TEXT,
  "reference_period" TEXT,
  "series_id" TEXT,
  "actual_yoy_pct" REAL,
  "forecast_yoy_pct" REAL,
  "surprise_percentage_points" REAL,
  "surprise_class" TEXT,
  "source" TEXT,
  "provider_event_id" INTEGER,
  "provider_occurrence_id" INTEGER,
  "release_date_approximate" INTEGER,
  "forecast_pre_release_verified" TEXT,
  "initial_actual_verified" TEXT,
  "source_url" TEXT,
  "release_on_equity_session" INTEGER,
  "event_session_date" TEXT,
  "all_yields_on_event_date" INTEGER,
  "following_5_equity_returns_complete" INTEGER,
  "following_5_valid_treasury_observations_complete" INTEGER,
  "step1_status" TEXT
);

CREATE TABLE "cpi_inference" (
"family" TEXT,
  "measure" TEXT,
  "comparison" TEXT,
  "n_first" INTEGER,
  "n_second" REAL,
  "effect" REAL,
  "effect_units" TEXT,
  "ci95_low" REAL,
  "ci95_high" REAL,
  "p_unadjusted" REAL,
  "valid_resamples" INTEGER,
  "p_holm" REAL,
  "significant_after_holm_005" INTEGER
);

CREATE TABLE "cpi_non_cpi_inference" (
"outcome" TEXT,
  "cpi_n" INTEGER,
  "non_cpi_n" INTEGER,
  "cpi_mean" REAL,
  "non_cpi_mean" REAL,
  "difference_cpi_minus_non_cpi" REAL,
  "cpi_median" REAL,
  "non_cpi_median" REAL,
  "unit" TEXT,
  "ci95_low" REAL,
  "ci95_high" REAL,
  "p_unadjusted" REAL,
  "family" TEXT,
  "p_holm" REAL,
  "significant_holm_005" INTEGER
);

CREATE TABLE "cpi_non_cpi_windows" (
"date" TEXT,
  "group" TEXT,
  "cpi_primary" INTEGER,
  "control_eligible" INTEGER,
  "cpi_contamination_flag" INTEGER,
  "complete_response_window" INTEGER,
  "DGS2_bp" REAL,
  "DGS10_bp" REAL,
  "DGS30_bp" REAL,
  "SPY_vol_pct" REAL,
  "IWM_vol_pct" REAL
);

CREATE TABLE "cpi_three_way_descriptive" (
"surprise_class" TEXT,
  "maturity" TEXT,
  "etf" TEXT,
  "n_events" INTEGER,
  "mean_next5_yield_change_bp" REAL,
  "median_next5_yield_change_bp" REAL,
  "mean_next5_equity_vol_pct" REAL,
  "median_next5_equity_vol_pct" REAL,
  "within_class_pearson_r_yield_change_vs_vol" REAL
);

CREATE TABLE "cpi_treasury_responses" (
"release_date" TEXT,
  "actual_yoy_pct" REAL,
  "forecast_yoy_pct" REAL,
  "surprise_percentage_points" REAL,
  "surprise_class" TEXT,
  "aligned_primary" INTEGER,
  "alignment_status" TEXT,
  "followup_treasury_date" TEXT,
  "followup_observations" INTEGER,
  "DGS2_change_next_5obs_bp" REAL,
  "DGS10_change_next_5obs_bp" REAL,
  "DGS30_change_next_5obs_bp" REAL
);

CREATE TABLE "cross_maturity_descriptive" (
"maturity_years" INTEGER,
  "treasury_event" TEXT,
  "etf" TEXT,
  "n_treasury_events" INTEGER,
  "n_response_eligible_events" INTEGER,
  "mean_treasury_change_bp" REAL,
  "mean_abs_treasury_change_bp" REAL,
  "full_sample_5obs_yield_change_sd_bp" REAL,
  "mean_abs_shock_in_yield_sd_units" REAL,
  "normal_mean_5d_realized_vol_pct" REAL,
  "event_mean_5d_realized_vol_pct" REAL,
  "difference_percentage_points" REAL,
  "relative_increase_pct" REAL,
  "within_maturity_holm_p" REAL,
  "within_maturity_significant" INTEGER
);

CREATE TABLE "cross_maturity_inference" (
"etf" TEXT,
  "direction" TEXT,
  "contrast" TEXT,
  "maturity_a_years" INTEGER,
  "maturity_b_years" INTEGER,
  "exposure_a_sd" REAL,
  "exposure_b_sd" REAL,
  "standardized_effect_a" REAL,
  "standardized_effect_b" REAL,
  "difference_standardized_effect" REAL,
  "ci_95_low" REAL,
  "ci_95_high" REAL,
  "p_bootstrap_two_sided" REAL,
  "p_holm_12_comparisons" REAL,
  "significant_holm_0_05" INTEGER,
  "bootstrap_resamples" INTEGER,
  "block_length_equity_sessions" INTEGER,
  "seed" INTEGER
);

CREATE TABLE "etf_daily" (
"date" TEXT,
  "etf" TEXT,
  "close_rth" REAL,
  "log_return" REAL,
  "distribution" REAL,
  "late_start" INTEGER,
  "early_end" INTEGER,
  "source_frequency" TEXT
);

CREATE TABLE "etf_event_responses" (
"date" TEXT,
  "maturity_years" INTEGER,
  "etf" TEXT,
  "during_return_pct" REAL,
  "during_vol_pct" REAL,
  "following_return_pct" REAL,
  "following_vol_pct" REAL
);

CREATE TABLE "etf_sensitivity_comparisons" (
"maturity_years" INTEGER,
  "contrast" TEXT,
  "n_event" INTEGER,
  "n_normal" INTEGER,
  "spy_relative_vol_change_pct" REAL,
  "iwm_relative_vol_change_pct" REAL,
  "spy_minus_iwm_percentage_points" REAL,
  "ci_95_low_percentage_points" REAL,
  "ci_95_high_percentage_points" REAL,
  "p_bootstrap_two_sided" REAL,
  "p_holm" REAL,
  "holm_significant_0_05" INTEGER,
  "bootstrap_resamples" INTEGER,
  "block_length_equity_sessions" INTEGER,
  "random_seed" INTEGER
);

CREATE TABLE "joint_curve_inference" (
"contrast" TEXT,
  "ETF" TEXT,
  "n_condition" INTEGER,
  "n_reference" INTEGER,
  "condition_mean_vol_pct" REAL,
  "reference_mean_vol_pct" REAL,
  "difference_pp" REAL,
  "relative_difference_pct" REAL,
  "ci_95_low_pp" REAL,
  "ci_95_high_pp" REAL,
  "p_bootstrap" REAL,
  "p_holm_8_tests" REAL,
  "significant_0_05" INTEGER
);

CREATE TABLE "joint_yield_events" (
"date" TEXT,
  "dgs2_change_5obs_bp" REAL,
  "dgs2_event" TEXT,
  "dgs2_eligible" INTEGER,
  "dgs10_change_5obs_bp" REAL,
  "dgs10_event" TEXT,
  "dgs10_eligible" INTEGER,
  "dgs30_change_5obs_bp" REAL,
  "dgs30_event" TEXT,
  "dgs30_eligible" INTEGER,
  "joint_sharp_event" TEXT,
  "eligible_for_response_analysis" INTEGER,
  "event_sequence_start" INTEGER
);

CREATE TABLE "market_days" (
"date" TEXT,
  "valid_all_yields" INTEGER,
  "valid_equity_returns" INTEGER,
  "research_date_eligible" INTEGER
);

CREATE TABLE "maturity_etf_inference" (
"maturity_years" INTEGER,
  "etf" TEXT,
  "contrast" TEXT,
  "n_event" INTEGER,
  "n_normal" INTEGER,
  "event_mean_vol_pct" REAL,
  "normal_mean_vol_pct" REAL,
  "difference_percentage_points" REAL,
  "relative_difference_pct" REAL,
  "ci_95_low_pp" REAL,
  "ci_95_high_pp" REAL,
  "p_bootstrap_two_sided" REAL,
  "p_holm" REAL,
  "holm_significant_0_05" INTEGER,
  "bootstrap_resamples" INTEGER,
  "block_length_equity_sessions" INTEGER,
  "random_seed" INTEGER
);

CREATE TABLE "treasury_events" (
"date" TEXT,
  "maturity_years" INTEGER,
  "yield_change_bp" REAL,
  "event_class" TEXT,
  "eligible_for_response_analysis" INTEGER
);

CREATE TABLE "treasury_yields" (
"date" TEXT,
  "maturity" TEXT,
  "yield_pct" REAL
);

CREATE TABLE "yield_curve_spreads" (
"date" TEXT,
  "DGS2" REAL,
  "DGS10" REAL,
  "DGS30" REAL,
  "spread_10y_minus_2y_bp" REAL,
  "spread_30y_minus_10y_bp" REAL,
  "spread_10y_minus_2y_change_5obs_bp" REAL,
  "spread_30y_minus_10y_change_5obs_bp" REAL
);
