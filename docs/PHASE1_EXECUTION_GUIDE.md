# Phase 1: Source Data & Environment Setup - Execution Guide

## 🎯 Today's Goal

Set up your Databricks workspace, configure data sources, and load initial company data.

**Expected Time**: 2-4 hours
**End Result**: Working Databricks environment with data access

---

## 📋 Pre-Flight Checklist

Before you start, make sure you have:
- [ ] Access to a Databricks workspace (AWS)
- [ ] Admin or workspace admin permissions
- [ ] (Optional) OpenAI API key (for LLM agents)
- [ ] (Optional) Alpha Vantage API key
- [ ] (Optional) FRED API key

**Note**: You can start with just Databricks + Yahoo Finance (no API keys needed!)

---

## Step 1: Access Databricks Workspace (15 minutes)

### 1.1 Log into Databricks
1. Go to your Databricks workspace URL: `https://your-workspace.cloud.databricks.com`
2. Log in with your credentials

### 1.2 Verify Unity Catalog
1. Click on **Catalog** in the left sidebar
2. Check if you see "Unity Catalog" or catalog options
3. **If Unity Catalog is NOT enabled**:
   - Contact your Databricks admin
   - Or check Admin Settings → Unity Catalog

### 1.3 Check Your Permissions
- Can you see "Compute" in the left sidebar? ✅
- Can you see "SQL" or "SQL Editor"? ✅
- Can you see "Marketplace"? ✅

**✅ Checkpoint**: You're logged in and can see the main navigation

---

## Step 2: Check Databricks Marketplace (10 minutes)

### 2.1 Browse Marketplace
1. Click **Marketplace** in the left sidebar
2. Search for: **"financial"** or **"stock market"** or **"OLAPTrader"**
3. Look for free datasets

### 2.2 Subscribe to Free Data (if available)
1. Find **OLAPTrader Financial Data** (if available)
2. Click **"Get"** or **"Subscribe"**
3. Select catalog: `stocks_ai` (we'll create this)
4. Click **"Get instant access"**

**Note**: If Marketplace data isn't available, that's fine! We'll use Yahoo Finance.

**✅ Checkpoint**: Marketplace checked (data found or not - both are fine)

---

## Step 3: Create Unity Catalog Schemas (20 minutes)

### 3.1 Open SQL Editor
1. Click **SQL** or **SQL Editor** in left sidebar
2. You should see a query editor

### 3.2 Create Catalog
Copy and paste this into SQL Editor:

```sql
-- Create catalog (if it doesn't exist)
CREATE CATALOG IF NOT EXISTS stocks_ai
COMMENT 'Multi-supervisor AI system for stock prediction and investment hypothesis formation';
```

Click **Run** (or press Shift+Enter)

### 3.3 Create Schemas
Run these one by one:

```sql
USE CATALOG stocks_ai;

CREATE SCHEMA IF NOT EXISTS fortune100
COMMENT 'Fortune 100 companies data and predictions';

CREATE SCHEMA IF NOT EXISTS signals
COMMENT 'Raw and processed signals from various sources';

CREATE SCHEMA IF NOT EXISTS agents
COMMENT 'Agent predictions and reasoning logs';

CREATE SCHEMA IF NOT EXISTS meta
COMMENT 'Meta-supervisor synthesized predictions and hypotheses';
```

### 3.4 Verify Creation
Run this to verify:

```sql
SHOW SCHEMAS IN stocks_ai;
```

You should see:
- `fortune100`
- `signals`
- `agents`
- `meta`

**✅ Checkpoint**: Catalog and schemas created successfully

---

## Step 4: Create Company Master Table (15 minutes)

### 4.1 Create Companies Table
Run this SQL:

```sql
USE SCHEMA stocks_ai.fortune100;

CREATE TABLE IF NOT EXISTS companies (
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
```

### 4.2 Verify Table Created
```sql
SHOW TABLES IN stocks_ai.fortune100;
```

You should see `companies` table.

**✅ Checkpoint**: Companies table created

---

## Step 5: Create Cluster (20 minutes)

### 5.1 Create New Cluster
1. Click **Compute** in left sidebar
2. Click **Create Cluster**
3. Configure:

**Basic Settings**:
- **Cluster Name**: `stocks-ai-cluster`
- **Cluster Mode**: **Standard** (or High Concurrency if available)
- **Databricks Runtime**: **13.3 LTS** or latest (with Photon if available)
- **Python Version**: **3.10** or **3.11**

**Node Configuration**:
- **Node Type**: Start with **`i3.xlarge`** or **`m5.xlarge`** (smaller/cheaper)
- **Workers**: **2** (start small, can scale later)
- **Driver Type**: Same as worker (or smaller)

**Advanced Options**:
- **Auto Termination**: **30 minutes** (saves costs)
- **Spark Config** (optional, add these):
  ```
  spark.databricks.delta.optimizeWrite.enabled true
  spark.databricks.delta.autoCompact.enabled true
  ```

### 5.2 Install Libraries
1. After cluster is created, click on cluster name
2. Go to **Libraries** tab
3. Click **Install New**
4. Select **PyPI**
5. Install these one by one (or use requirements.txt if you upload it):
   - `yfinance>=0.2.0`
   - `alpha-vantage>=2.3.0` (optional)
   - `fredapi>=0.5.0` (optional)
   - `openai>=1.0.0` (if using OpenAI)
   - `anthropic>=0.18.0` (if using Anthropic)
   - `pydantic>=2.0.0`
   - `python-dotenv>=1.0.0`

**Note**: Cluster will restart after installing libraries.

**✅ Checkpoint**: Cluster created and libraries installing

---

## Step 6: Set Up API Keys (15 minutes)

### Option A: Databricks Secrets (Recommended)

#### 6.1 Create Secret Scope
1. Click your **username** (top right) → **User Settings**
2. Click **Access Tokens** (or use Databricks CLI)
3. Or use **Workspace** → **Secrets** (if available)

**Using Databricks CLI** (if you have it installed):
```bash
databricks secrets create-scope --scope stocks_ai_secrets
```

**Using UI** (if available):
1. Go to **Workspace** → **Secrets**
2. Create new scope: `stocks_ai_secrets`

#### 6.2 Add Secrets
Using CLI:
```bash
databricks secrets put --scope stocks_ai_secrets --key openai_api_key
# Paste your key when prompted

databricks secrets put --scope stocks_ai_secrets --key alpha_vantage_api_key
# Paste your key when prompted

databricks secrets put --scope stocks_ai_secrets --key fred_api_key
# Paste your key when prompted
```

**Note**: If you don't have CLI, you can skip this and use environment variables.

### Option B: Cluster Environment Variables (Easier for Testing)

1. Go to your cluster → **Configuration** → **Advanced Options**
2. Scroll to **Environment Variables**
3. Add:
   ```
   OPENAI_API_KEY=your-key-here
   ALPHA_VANTAGE_API_KEY=your-key-here
   FRED_API_KEY=your-key-here
   ```
4. **Restart cluster**

**⚠️ Security Note**: Environment variables are visible to all users. Use Secrets for production.

**✅ Checkpoint**: API keys configured (or skipped if not using)

---

## Step 7: Upload Code to Databricks (20 minutes)

### Option A: Databricks Repos (Recommended)

#### 7.1 Create Repo
1. Click **Repos** in left sidebar
2. Click **Add Repo**
3. Choose:
   - **Create repo** (if starting fresh)
   - **Clone remote Git repository** (if you have GitHub/GitLab)

#### 7.2 Upload Files
If creating new repo:
1. Click **Add** → **File** or **Folder**
2. Upload your project files:
   - `src/` folder
   - `notebooks/` folder
   - `setup/` folder
   - `requirements.txt`
   - `README.md`

### Option B: Workspace Files (Alternative)

1. Click **Workspace** in left sidebar
2. Navigate to `/Users/your-email@company.com/`
3. Create folder: `stocks`
4. Upload files using **Add** → **File**

**✅ Checkpoint**: Code uploaded to Databricks

---

## Step 8: Run Initial Setup Notebook (30 minutes)

### 8.1 Create/Open Setup Notebook
1. In your repo or workspace, create new notebook: `00_initial_setup.ipynb`
2. Or open the existing one if you uploaded it

### 8.2 Run Setup Cells
Copy and run these cells one by one:

**Cell 1: Install Libraries**
```python
%pip install yfinance>=0.2.0
%pip install alpha-vantage>=2.3.0
%pip install fredapi>=0.5.0
%pip install openai>=1.0.0
%pip install pydantic>=2.0.0
%pip install python-dotenv>=1.0.0
```

**Cell 2: Configure API Keys**
```python
import os

# Option 1: Use Databricks Secrets
try:
    openai_key = dbutils.secrets.get(scope="stocks_ai_secrets", key="openai_api_key")
    os.environ['OPENAI_API_KEY'] = openai_key
    print("✓ OpenAI API key loaded from secrets")
except Exception as e:
    print(f"⚠ OpenAI key not found: {e}")

try:
    alpha_vantage_key = dbutils.secrets.get(scope="stocks_ai_secrets", key="alpha_vantage_api_key")
    os.environ['ALPHA_VANTAGE_API_KEY'] = alpha_vantage_key
    print("✓ Alpha Vantage API key loaded")
except Exception as e:
    print(f"⚠ Alpha Vantage key not found: {e}")

try:
    fred_key = dbutils.secrets.get(scope="stocks_ai_secrets", key="fred_api_key")
    os.environ['FRED_API_KEY'] = fred_key
    print("✓ FRED API key loaded")
except Exception as e:
    print(f"⚠ FRED key not found: {e}")

# Option 2: Keys should already be in os.environ if set on cluster
```

**Cell 3: Set Python Path**
```python
import sys

# Update this path to your actual location
# Option 1: If using Repos
repo_path = '/Workspace/Repos/your-username/stocks-ai/stocks'

# Option 2: If using Workspace
# repo_path = '/Workspace/Users/your-email@company.com/stocks'

if repo_path not in sys.path:
    sys.path.append(repo_path)
    print(f"✓ Added {repo_path} to Python path")
else:
    print(f"✓ Path already configured")
```

**Cell 4: Test Data Loader**
```python
# Test basic data loading (before full implementation)
import yfinance as yf
from datetime import date

# Test Yahoo Finance
print("Testing Yahoo Finance...")
ticker = yf.Ticker("AAPL")
info = ticker.info
print(f"✓ Company: {info.get('longName', 'N/A')}")
print(f"✓ Sector: {info.get('sector', 'N/A')}")
print(f"✓ Industry: {info.get('industry', 'N/A')}")

# Test price data
hist = ticker.history(period="5d")
if not hist.empty:
    print(f"✓ Latest price: ${hist['Close'].iloc[-1]:.2f}")
    print(f"✓ Data loaded successfully!")
else:
    print("⚠ No price data available")
```

**Cell 5: Load Sample Companies**
```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, LongType, IntegerType, TimestampType
from datetime import datetime

spark = SparkSession.builder.getOrCreate()

# Sample Fortune 100 companies (top 20)
fortune100_symbols = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "META", "TSLA", "BRK.B", "V", "JNJ",
    "WMT", "PG", "MA", "UNH", "HD",
    "DIS", "BAC", "ADBE", "NFLX", "CRM"
]

# Load company data
companies = []
for symbol in fortune100_symbols:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        companies.append({
            "symbol": symbol,
            "company_name": info.get("longName", symbol),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "market_cap": info.get("marketCap"),
            "fortune_rank": None,
            "added_date": datetime.now(),
            "updated_date": datetime.now()
        })
        print(f"✓ Loaded {symbol}: {info.get('longName', symbol)}")
    except Exception as e:
        print(f"✗ Failed to load {symbol}: {e}")

# Save to Delta table
if companies:
    df = spark.createDataFrame(companies)
    df.write.format("delta").mode("overwrite").saveAsTable("stocks_ai.fortune100.companies")
    print(f"\n✓ Saved {len(companies)} companies to Delta table")
    df.show(truncate=False)
else:
    print("✗ No companies loaded")
```

**Cell 6: Verify Setup**
```python
# Verify everything works
print("\n" + "="*80)
print("SETUP VERIFICATION")
print("="*80)

checks = {
    "Python path configured": repo_path in sys.path,
    "OpenAI key available": os.getenv('OPENAI_API_KEY') is not None,
    "Yahoo Finance works": len(companies) > 0,
    "Delta table accessible": True
}

for check, status in checks.items():
    status_icon = "✓" if status else "✗"
    print(f"{status_icon} {check}")

# Verify Delta table
try:
    count = spark.sql("SELECT COUNT(*) as cnt FROM stocks_ai.fortune100.companies").collect()[0]['cnt']
    print(f"✓ Companies in table: {count}")
except Exception as e:
    print(f"✗ Delta table error: {e}")

if all(checks.values()):
    print("\n✅ Phase 1 Setup Complete!")
    print("You can now proceed to Phase 2: Core Infrastructure")
else:
    print("\n⚠️  Some checks failed. Please review the setup steps above.")
```

### 8.3 Run All Cells
1. Attach notebook to your cluster
2. Run all cells (or run individually)
3. Check for errors

**✅ Checkpoint**: Setup notebook runs successfully

---

## Step 9: Verify Everything Works (10 minutes)

### 9.1 Test SQL Queries
Create a new SQL cell or use SQL Editor:

```sql
-- Verify companies table
SELECT * FROM stocks_ai.fortune100.companies LIMIT 10;
```

Should return your loaded companies.

### 9.2 Test Python Access
In a Python notebook:

```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()

# Query companies
df = spark.sql("SELECT * FROM stocks_ai.fortune100.companies")
df.show()
```

Should display companies.

**✅ Checkpoint**: Data accessible via SQL and Python

---

## Step 10: Create MLflow Experiment (5 minutes)

### 10.1 Create Experiment
In a notebook:

```python
import mlflow

# Create MLflow experiment
mlflow.set_experiment("/Shared/stocks_ai/experiments")

# Test logging
with mlflow.start_run():
    mlflow.log_param("test", "phase1_setup")
    mlflow.log_metric("companies_loaded", len(companies))
    print("✓ MLflow experiment created and tested")
```

**✅ Checkpoint**: MLflow working

---

## ✅ Phase 1 Completion Checklist

Before moving to Phase 2, verify:

- [ ] ✅ Databricks workspace accessible
- [ ] ✅ Unity Catalog enabled
- [ ] ✅ Catalog `stocks_ai` created
- [ ] ✅ Schemas created (fortune100, signals, agents, meta)
- [ ] ✅ Cluster created and running
- [ ] ✅ Libraries installed
- [ ] ✅ API keys configured (or skipped)
- [ ] ✅ Code uploaded to Databricks
- [ ] ✅ Setup notebook runs successfully
- [ ] ✅ Companies table populated
- [ ] ✅ Data accessible via SQL
- [ ] ✅ MLflow experiment created
- [ ] ✅ No errors in setup

---

## 🎯 Success Criteria

**Phase 1 is complete when:**
1. ✅ You can query `SELECT * FROM stocks_ai.fortune100.companies;`
2. ✅ Data loader can fetch company info from Yahoo Finance
3. ✅ No errors in setup notebook
4. ✅ Cluster is running and libraries are installed

---

## 🆘 Troubleshooting

### Issue: "Cannot find catalog stocks_ai"
**Solution**: Make sure you ran the CREATE CATALOG command and Unity Catalog is enabled.

### Issue: "Cluster not found"
**Solution**: Make sure cluster is running. Click "Start" if it's stopped.

### Issue: "Module not found"
**Solution**: Install libraries on cluster. Go to cluster → Libraries → Install.

### Issue: "Permission denied"
**Solution**: Check your permissions. You may need admin to create catalog.

### Issue: "API key not found"
**Solution**: That's OK! You can proceed without API keys for now. Yahoo Finance works without keys.

---

## 📝 Notes

_Use this space to track any issues or learnings during Phase 1:_

- Issue: _______________
- Solution: _______________
- Learning: _______________

---

## 🚀 Next Steps

Once Phase 1 is complete:
1. ✅ Celebrate! You've set up the foundation
2. 📖 Review Phase 2: Core Infrastructure
3. 🎯 Start Phase 2 when ready

**Good luck with Phase 1!** 🎉
