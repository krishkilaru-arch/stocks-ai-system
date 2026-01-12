-- Unity Catalog setup for Multi-Supervisor AI Stock Prediction System
-- Run this in your Databricks SQL workspace

-- Create catalog (if it doesn't exist)
CREATE CATALOG IF NOT EXISTS stocks_ai
COMMENT 'Multi-supervisor AI system for stock prediction and investment hypothesis formation';

USE CATALOG stocks_ai;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS fortune100
COMMENT 'Fortune 100 companies data and predictions';

CREATE SCHEMA IF NOT EXISTS signals
COMMENT 'Raw and processed signals from various sources';

CREATE SCHEMA IF NOT EXISTS agents
COMMENT 'Agent predictions and reasoning logs';

CREATE SCHEMA IF NOT EXISTS meta
COMMENT 'Meta-supervisor synthesized predictions and hypotheses';

-- Create tables for company data
CREATE TABLE IF NOT EXISTS fortune100.companies (
  symbol STRING NOT NULL,
  company_name STRING,
  sector STRING,
  industry STRING,
  market_cap BIGINT,
  fortune_rank INT,
  added_date TIMESTAMP,
  updated_date TIMESTAMP
) USING DELTA
COMMENT 'Fortune 100 company master data';

-- Create tables for signals
CREATE TABLE IF NOT EXISTS signals.fundamentals (
  symbol STRING NOT NULL,
  date DATE NOT NULL,
  revenue BIGINT,
  net_income BIGINT,
  eps DOUBLE,
  pe_ratio DOUBLE,
  debt_to_equity DOUBLE,
  roe DOUBLE,
  revenue_growth DOUBLE,
  ingestion_timestamp TIMESTAMP
) USING DELTA
PARTITIONED BY (date)
COMMENT 'Company fundamental metrics';

CREATE TABLE IF NOT EXISTS signals.valuation (
  symbol STRING NOT NULL,
  date DATE NOT NULL,
  market_cap BIGINT,
  enterprise_value BIGINT,
  pe_ratio DOUBLE,
  pb_ratio DOUBLE,
  ev_ebitda DOUBLE,
  dcf_value DOUBLE,
  fair_value_estimate DOUBLE,
  ingestion_timestamp TIMESTAMP
) USING DELTA
PARTITIONED BY (date)
COMMENT 'Valuation metrics and estimates';

CREATE TABLE IF NOT EXISTS signals.macro (
  date DATE NOT NULL,
  gdp_growth DOUBLE,
  inflation_rate DOUBLE,
  interest_rate DOUBLE,
  unemployment_rate DOUBLE,
  consumer_confidence DOUBLE,
  vix_index DOUBLE,
  ingestion_timestamp TIMESTAMP
) USING DELTA
PARTITIONED BY (date)
COMMENT 'Macroeconomic indicators';

CREATE TABLE IF NOT EXISTS signals.events (
  event_id STRING NOT NULL,
  symbol STRING,
  event_type STRING, -- earnings, news, merger, etc.
  event_date DATE,
  title STRING,
  description STRING,
  sentiment_score DOUBLE,
  impact_score DOUBLE,
  ingestion_timestamp TIMESTAMP
) USING DELTA
PARTITIONED BY (event_date)
COMMENT 'Market events and news';

CREATE TABLE IF NOT EXISTS signals.technical (
  symbol STRING NOT NULL,
  date DATE NOT NULL,
  open_price DOUBLE,
  high_price DOUBLE,
  low_price DOUBLE,
  close_price DOUBLE,
  volume BIGINT,
  sma_50 DOUBLE,
  sma_200 DOUBLE,
  rsi DOUBLE,
  macd DOUBLE,
  bollinger_upper DOUBLE,
  bollinger_lower DOUBLE,
  ingestion_timestamp TIMESTAMP
) USING DELTA
PARTITIONED BY (date)
COMMENT 'Technical indicators and price data';

-- Create tables for agent predictions
CREATE TABLE IF NOT EXISTS agents.fundamentals_predictions (
  prediction_id STRING NOT NULL,
  symbol STRING NOT NULL,
  prediction_date DATE NOT NULL,
  target_date DATE NOT NULL,
  predicted_return DOUBLE,
  confidence_score DOUBLE,
  reasoning STRING,
  key_factors ARRAY<STRING>,
  created_timestamp TIMESTAMP
) USING DELTA
PARTITIONED BY (prediction_date)
COMMENT 'Fundamentals agent predictions';

CREATE TABLE IF NOT EXISTS agents.valuation_predictions (
  prediction_id STRING NOT NULL,
  symbol STRING NOT NULL,
  prediction_date DATE NOT NULL,
  target_date DATE NOT NULL,
  predicted_return DOUBLE,
  confidence_score DOUBLE,
  reasoning STRING,
  key_factors ARRAY<STRING>,
  created_timestamp TIMESTAMP
) USING DELTA
PARTITIONED BY (prediction_date)
COMMENT 'Valuation agent predictions';

CREATE TABLE IF NOT EXISTS agents.macro_predictions (
  prediction_id STRING NOT NULL,
  symbol STRING NOT NULL,
  prediction_date DATE NOT NULL,
  target_date DATE NOT NULL,
  predicted_return DOUBLE,
  confidence_score DOUBLE,
  reasoning STRING,
  key_factors ARRAY<STRING>,
  created_timestamp TIMESTAMP
) USING DELTA
PARTITIONED BY (prediction_date)
COMMENT 'Macro agent predictions';

CREATE TABLE IF NOT EXISTS agents.events_predictions (
  prediction_id STRING NOT NULL,
  symbol STRING NOT NULL,
  prediction_date DATE NOT NULL,
  target_date DATE NOT NULL,
  predicted_return DOUBLE,
  confidence_score DOUBLE,
  reasoning STRING,
  key_factors ARRAY<STRING>,
  created_timestamp TIMESTAMP
) USING DELTA
PARTITIONED BY (prediction_date)
COMMENT 'Events agent predictions';

CREATE TABLE IF NOT EXISTS agents.technical_predictions (
  prediction_id STRING NOT NULL,
  symbol STRING NOT NULL,
  prediction_date DATE NOT NULL,
  target_date DATE NOT NULL,
  predicted_return DOUBLE,
  confidence_score DOUBLE,
  reasoning STRING,
  key_factors ARRAY<STRING>,
  created_timestamp TIMESTAMP
) USING DELTA
PARTITIONED BY (prediction_date)
COMMENT 'Technical agent predictions';

CREATE TABLE IF NOT EXISTS agents.sector_predictions (
  prediction_id STRING NOT NULL,
  symbol STRING NOT NULL,
  prediction_date DATE NOT NULL,
  target_date DATE NOT NULL,
  predicted_return DOUBLE,
  confidence_score DOUBLE,
  reasoning STRING,
  key_factors ARRAY<STRING>,
  created_timestamp TIMESTAMP
) USING DELTA
PARTITIONED BY (prediction_date)
COMMENT 'Sector agent predictions';

-- Create table for meta-supervisor synthesized predictions
CREATE TABLE IF NOT EXISTS meta.synthesized_predictions (
  prediction_id STRING NOT NULL,
  symbol STRING NOT NULL,
  prediction_date DATE NOT NULL,
  target_date DATE NOT NULL,
  predicted_return DOUBLE,
  confidence_score DOUBLE,
  investment_hypothesis STRING,
  reasoning_chain STRING,
  agent_contributions MAP<STRING, STRUCT<predicted_return: DOUBLE, confidence: DOUBLE, reasoning: STRING>>,
  risk_factors ARRAY<STRING>,
  key_insights ARRAY<STRING>,
  created_timestamp TIMESTAMP
) USING DELTA
PARTITIONED BY (prediction_date)
COMMENT 'Meta-supervisor synthesized predictions with investment hypotheses';

-- Create view for recent predictions
CREATE OR REPLACE VIEW meta.recent_predictions AS
SELECT 
  symbol,
  prediction_date,
  target_date,
  predicted_return,
  confidence_score,
  investment_hypothesis,
  risk_factors,
  key_insights,
  created_timestamp
FROM meta.synthesized_predictions
WHERE prediction_date >= CURRENT_DATE() - INTERVAL 7 DAYS
ORDER BY prediction_date DESC, confidence_score DESC;
