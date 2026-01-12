# Data Sources Guide

## Overview

This guide explains all data sources used in the system and how to configure them.

---

## 🎯 Databricks Marketplace Data (Recommended!)

### 0. Databricks Marketplace - BEST OPTION

**Status**: ✅ Check your Databricks workspace Marketplace

**What it provides**:
- Pre-processed Delta tables (no ETL needed!)
- Automatic Unity Catalog integration
- Data lineage built-in
- Production-ready data maintained by providers

**How to Access**:
1. Go to **Marketplace** in Databricks UI
2. Search for "stock market" or "financial data"
3. Look for free/free-tier providers:
   - **Polygon.io** (free tier available)
   - **FRED** (if available as Delta tables)
   - **SEC EDGAR** (if processed version available)
   - **IEX Cloud** (free tier)

**Advantages**:
- ✅ No API keys needed (for some providers)
- ✅ No ETL pipelines required
- ✅ Automatic governance (Unity Catalog)
- ✅ Data already in Delta format
- ✅ **Strong Databricks-specific value for proposal!**

**See**: `DATABRICKS_MARKETPLACE_DATA.md` for detailed guide

---

## ✅ Free Data Sources (No API Key Required)

### 1. Yahoo Finance (yfinance) - PRIMARY SOURCE

**Status**: ✅ Works out of the box

**What it provides**:
- Stock prices (historical and real-time)
- Company fundamentals (P/E, P/B, ROE, etc.)
- Financial statements (income, balance sheet, cash flow)
- Company information (sector, industry, market cap)
- Technical indicators (can calculate from price data)
- Earnings calendar

**Setup**: 
```python
%pip install yfinance
# No API key needed!
```

**Usage**:
```python
import yfinance as yf
ticker = yf.Ticker("AAPL")
info = ticker.info  # Company info
hist = ticker.history(period="1y")  # Price history
```

**Limitations**:
- Rate limits (not officially documented, ~2000 requests/hour recommended)
- Some data may be delayed (15-20 minutes for real-time)
- Not suitable for high-frequency trading
- Some fundamental data may be incomplete

**Best for**: 
- Development and demos
- Historical backtesting
- Company fundamentals
- Price data

---

## 🔑 Optional Data Sources (API Keys Recommended)

### 2. Alpha Vantage - ENHANCED MARKET DATA

**Why use it**: More reliable, higher rate limits, additional indicators

**What it provides**:
- Technical indicators (RSI, MACD, Bollinger Bands)
- Fundamental data (earnings, financials)
- Earnings data and estimates
- News sentiment
- Sector performance

**Setup**:
1. **Get API Key**: https://www.alphavantage.co/support/#api-key (free)
2. **Add to Databricks Secrets**:
   ```bash
   databricks secrets put --scope stocks_ai_secrets --key alpha_vantage_api_key
   ```

**Rate Limits**:
- **Free tier**: 5 calls/minute, 500 calls/day
- **Premium**: Higher limits (paid)

**Usage**:
```python
from alpha_vantage.timeseries import TimeSeries
ts = TimeSeries(key=api_key)
data, meta_data = ts.get_intraday(symbol='AAPL', interval='1min')
```

**Best for**:
- Technical indicators
- Real-time data (with premium)
- Additional market metrics

---

### 3. FRED (Federal Reserve Economic Data) - MACROECONOMIC DATA

**Why use it**: Authoritative source for US macroeconomic data

**What it provides**:
- GDP growth
- Inflation (CPI)
- Interest rates (Fed Funds Rate)
- Unemployment rate
- Consumer confidence
- And 800,000+ other economic series

**Setup**:
1. **Get API Key**: https://fred.stlouisfed.org/docs/api/api_key.html (free)
2. **Add to Databricks Secrets**:
   ```bash
   databricks secrets put --scope stocks_ai_secrets --key fred_api_key
   ```

**Rate Limits**:
- **Free tier**: 120 calls/minute
- Very generous for our use case

**Usage**:
```python
from fredapi import Fred
fred = Fred(api_key=api_key)
gdp = fred.get_series('GDPC1')  # Real GDP
```

**Best for**:
- Macro Agent
- Economic indicators
- Policy analysis

---

## 💰 Premium Data Sources (Optional - Paid)

### 4. SEC EDGAR - OFFICIAL FINANCIAL FILINGS

**Why use it**: Official source for company financial data

**What it provides**:
- 10-K, 10-Q filings
- 8-K filings (events)
- Proxy statements
- Insider trading data

**Setup**:
- **Free**: SEC EDGAR API (complex, rate limited)
- **Paid**: Third-party providers (FactSet, Bloomberg, S&P Capital IQ)

**For demo**: Can skip, use Yahoo Finance fundamentals

---

### 5. News APIs - SENTIMENT DATA

**Options**:
- **NewsAPI**: https://newsapi.org/ (free tier: 100 requests/day)
- **Alpha Vantage News**: Included with Alpha Vantage
- **Polygon.io**: Market news (paid)

**Best for**: Events Agent

---

### 6. ESG Data Providers

**Options**:
- **MSCI ESG**: Premium (paid)
- **Sustainalytics**: Premium (paid)
- **Yahoo Finance**: Basic ESG scores (free, limited)

**For demo**: Use Yahoo Finance basic ESG data

---

## 📊 Data Source Priority

### Best Setup (Databricks-Specific):
1. 🎯 **Databricks Marketplace** - Check first!
   - Provides: Pre-processed Delta tables
   - Advantages: No ETL, Unity Catalog integration
   - **Strong differentiator for proposal!**

### Minimum Setup (Works Immediately):
1. ✅ **Yahoo Finance** - No API key needed
   - Provides: Prices, fundamentals, company info
   - Covers: 80% of use cases

### Recommended Setup:
1. 🎯 **Databricks Marketplace** (if available - best option!)
2. ✅ **Yahoo Finance** (primary fallback)
3. ✅ **Alpha Vantage** (technical indicators)
4. ✅ **FRED** (macroeconomic data)

### Full Production Setup:
1. Yahoo Finance
2. Alpha Vantage (premium)
3. FRED
4. SEC EDGAR or FactSet
5. News API
6. ESG provider (MSCI/Sustainalytics)

---

## 🔧 Configuration in Databricks

### Option 1: Databricks Secrets (Recommended)

```python
# In notebook
openai_key = dbutils.secrets.get(scope="stocks_ai_secrets", key="openai_api_key")
alpha_vantage_key = dbutils.secrets.get(scope="stocks_ai_secrets", key="alpha_vantage_api_key")
fred_key = dbutils.secrets.get(scope="stocks_ai_secrets", key="fred_api_key")

import os
os.environ['ALPHA_VANTAGE_API_KEY'] = alpha_vantage_key
os.environ['FRED_API_KEY'] = fred_key
```

### Option 2: Cluster Environment Variables

1. **Cluster Settings** → **Advanced Options** → **Environment Variables**
2. Add:
   ```
   ALPHA_VANTAGE_API_KEY=your-key
   FRED_API_KEY=your-key
   ```

### Option 3: Init Script

```bash
#!/bin/bash
export ALPHA_VANTAGE_API_KEY="your-key"
export FRED_API_KEY="your-key"
```

---

## 📈 Data Refresh Strategy

### Real-Time Data (Streaming):
- **Prices**: Every 10 seconds (via Structured Streaming)
- **News**: As events occur
- **Macro**: Daily (FRED updates daily)

### Batch Data (Scheduled Jobs):
- **Fundamentals**: Daily (after market close)
- **Technical Indicators**: Daily
- **ESG Scores**: Weekly or monthly
- **Company Info**: Monthly (rarely changes)

### Recommended Schedule:

**Daily Job** (6 AM UTC - after US market close):
- Refresh all price data
- Update fundamentals
- Calculate technical indicators
- Update predictions

**Weekly Job** (Sunday):
- Refresh ESG scores
- Update company master data
- Full portfolio analysis

---

## 🧪 Testing Data Sources

### Test Script:

```python
from src.data.loaders import DataLoader
from datetime import date

loader = DataLoader()

# Test each data source
print("Testing data sources...")

# 1. Company info (Yahoo Finance)
company = loader.get_company_info("AAPL")
print(f"✓ Company: {company.company_name if company else 'Failed'}")

# 2. Fundamentals (Yahoo Finance)
fundamentals = loader.get_fundamentals("AAPL", date.today())
print(f"✓ Fundamentals: P/E = {fundamentals.pe_ratio if fundamentals else 'Failed'}")

# 3. Technical (Yahoo Finance)
technical = loader.get_technical_indicators("AAPL", date.today())
print(f"✓ Technical: Price = ${technical.close_price if technical else 'Failed'}")

# 4. Macro (FRED - requires API key)
macro = loader.get_macro_indicators(date.today())
if macro:
    print(f"✓ Macro: GDP growth = {macro.gdp_growth}%")
else:
    print("⚠ Macro: Requires FRED API key")

# 5. Valuation (Yahoo Finance)
valuation = loader.get_valuation("AAPL", date.today())
print(f"✓ Valuation: Market Cap = ${valuation.market_cap:,}" if valuation else "⚠ Valuation: Failed")
```

---

## 💡 Recommendations

### For DAIS Demo:
- ✅ **Use Yahoo Finance only** - Works immediately, no setup
- ✅ **Add FRED** - Easy setup, adds macro data
- ⚠️ **Skip Alpha Vantage** - Can add later if needed

### For Production:
- ✅ **Yahoo Finance** - Primary source
- ✅ **Alpha Vantage Premium** - Better technical indicators
- ✅ **FRED** - Macro data
- ✅ **News API** - Sentiment data
- ✅ **ESG Provider** - For ESG Agent

### Cost Estimate:
- **Free tier**: $0 (Yahoo Finance + FRED free tier)
- **Basic**: ~$50/month (Alpha Vantage + News API)
- **Production**: $500-2000/month (Premium data providers)

---

## 🆘 Troubleshooting

### Issue: "Rate limit exceeded"

**Solution**: 
- Add delays between requests
- Use caching (Delta Lake)
- Upgrade to premium tier

### Issue: "API key invalid"

**Solution**:
- Verify key in Databricks Secrets
- Check key hasn't expired
- Test key outside Databricks

### Issue: "Data not available"

**Solution**:
- Some symbols may not have all data
- Check if company is listed
- Try alternative data source

---

## ✅ Quick Start Checklist

- [ ] Install yfinance: `%pip install yfinance`
- [ ] Test Yahoo Finance: Load AAPL data
- [ ] (Optional) Get FRED API key
- [ ] (Optional) Get Alpha Vantage API key
- [ ] Add keys to Databricks Secrets
- [ ] Test data loader
- [ ] Verify data writes to Delta Lake

**You can start with just Yahoo Finance - everything else is optional!**
