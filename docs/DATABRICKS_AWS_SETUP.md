# Databricks on AWS - Setup Guide

## Overview

This guide covers everything you need to set up the multi-agent stock prediction system on Databricks (AWS).

---

## 📋 Prerequisites Checklist

### 1. Databricks Workspace Requirements

- [ ] **Databricks workspace on AWS** (Standard or Premium tier recommended)
- [ ] **Unity Catalog enabled** (required for governance features)
- [ ] **Admin access** to workspace (for initial setup)
- [ ] **Cluster access** (ability to create clusters)
- [ ] **S3 bucket** for data storage (or use DBFS)

### 2. AWS Resources

- [ ] **S3 bucket** for Delta Lake tables (optional, can use DBFS)
- [ ] **IAM role** with S3 access (if using S3)
- [ ] **VPC configuration** (if required by your organization)

### 3. API Keys & Credentials

- [ ] **OpenAI API key** OR **Anthropic API key** (for LLM agents)
- [ ] **Alpha Vantage API key** (optional, for additional market data)
- [ ] **FRED API key** (optional, for macroeconomic data)
- [ ] **Databricks personal access token** (for CLI/API access)

---

## 🔧 Step 1: Databricks Workspace Configuration

### A. Enable Unity Catalog

1. **Go to Admin Settings** → **Unity Catalog**
2. **Enable Unity Catalog** (if not already enabled)
3. **Create Metastore** (if first time):
   ```
   - Metastore name: stocks_ai_metastore
   - S3 location: s3://your-bucket/unity-catalog/
   - IAM role: [Your Databricks IAM role]
   ```

### B. Create Catalog and Schemas

Run the SQL script in `setup/init.sql` in your Databricks SQL workspace:

```sql
-- This creates:
-- - Catalog: stocks_ai
-- - Schemas: fortune100, signals, agents, meta
-- - All Delta tables with proper schemas
```

**How to run:**
1. Open **Databricks SQL** (SQL Editor)
2. Copy contents of `setup/init.sql`
3. Execute section by section
4. Verify tables created: `SHOW TABLES IN stocks_ai.fortune100;`

### C. Configure Storage

**Option 1: Use DBFS (Simplest)**
- No additional setup needed
- Data stored in Databricks-managed storage
- Good for demos and development

**Option 2: Use S3 (Production)**
- Create S3 bucket: `s3://your-company-databricks-stocks/`
- Configure IAM role with S3 access
- Mount S3 bucket (optional):

```python
# In notebook
dbutils.fs.mount(
    source="s3://your-bucket/stocks/",
    mount_point="/mnt/stocks",
    extra_configs={"fs.s3a.aws.credentials.provider": "com.amazonaws.auth.InstanceProfileCredentialsProvider"}
)
```

---

## 📊 Step 2: Data Source Configuration

### A. Yahoo Finance (No API Key Needed) ✅

**Status**: Works out of the box with `yfinance` library

**Setup**: None required - just install package:
```python
%pip install yfinance
```

**What it provides**:
- Stock prices (historical and real-time)
- Company fundamentals
- Financial statements
- Company info (sector, industry)

**Limitations**:
- Rate limits (not officially documented)
- Some data may be delayed
- Not suitable for high-frequency trading

### B. Alpha Vantage (Optional but Recommended)

**Why**: More reliable, higher rate limits, additional indicators

**Setup**:
1. **Get API Key**: https://www.alphavantage.co/support/#api-key
2. **Add to environment**:
   ```python
   # In notebook or cluster environment variables
   import os
   os.environ['ALPHA_VANTAGE_API_KEY'] = 'your-key-here'
   ```

**What it provides**:
- Technical indicators (RSI, MACD, etc.)
- Fundamental data
- Earnings data
- News sentiment

**Rate Limits**:
- Free tier: 5 calls/minute, 500 calls/day
- Premium: Higher limits

### C. FRED (Federal Reserve Economic Data) - Optional

**Why**: Authoritative macroeconomic data

**Setup**:
1. **Get API Key**: https://fred.stlouisfed.org/docs/api/api_key.html
2. **Add to environment**:
   ```python
   os.environ['FRED_API_KEY'] = 'your-key-here'
   ```

**What it provides**:
- GDP growth
- Inflation rates
- Interest rates (Fed Funds)
- Unemployment
- Consumer confidence

### D. SEC Filings (Optional - Advanced)

**Why**: Official company financial data

**Options**:
1. **SEC EDGAR API** (free, but complex)
2. **Third-party providers** (FactSet, Bloomberg - paid)

**For demo**: Can skip initially, use Yahoo Finance fundamentals

---

## 🔑 Step 3: API Keys & Secrets Management

### Option A: Databricks Secrets (Recommended)

**Best Practice**: Store API keys in Databricks Secrets

1. **Create Secret Scope**:
   ```bash
   # Using Databricks CLI
   databricks secrets create-scope --scope stocks_ai_secrets
   ```

2. **Add Secrets**:
   ```bash
   databricks secrets put --scope stocks_ai_secrets --key openai_api_key
   databricks secrets put --scope stocks_ai_secrets --key alpha_vantage_api_key
   databricks secrets put --scope stocks_ai_secrets --key fred_api_key
   ```

3. **Access in Code**:
   ```python
   from pyspark.sql import SparkSession
   spark = SparkSession.builder.getOrCreate()
   
   openai_key = dbutils.secrets.get(scope="stocks_ai_secrets", key="openai_api_key")
   ```

### Option B: Cluster Environment Variables

**For Development**:
1. **Cluster Settings** → **Advanced Options** → **Environment Variables**
2. Add:
   ```
   OPENAI_API_KEY=your-key
   ALPHA_VANTAGE_API_KEY=your-key
   FRED_API_KEY=your-key
   ```

**⚠️ Security Note**: Environment variables are visible to all users on cluster. Use Secrets for production.

### Option C: .env File (Local Development Only)

For local development (not Databricks):
```bash
# .env file (never commit to git!)
OPENAI_API_KEY=your-key
ALPHA_VANTAGE_API_KEY=your-key
FRED_API_KEY=your-key
```

---

## 🚀 Step 4: Cluster Configuration

### Recommended Cluster Settings

**Cluster Type**: Standard (for development) or High Concurrency (for production)

**Configuration**:
```json
{
  "cluster_name": "stocks-ai-cluster",
  "spark_version": "13.3.x-scala2.12",
  "node_type_id": "i3.xlarge",  // or m5.xlarge for cost savings
  "driver_node_type_id": "i3.xlarge",
  "num_workers": 2,  // Start with 2, scale up as needed
  "autotermination_minutes": 30,
  "spark_conf": {
    "spark.databricks.delta.optimizeWrite.enabled": "true",
    "spark.databricks.delta.autoCompact.enabled": "true"
  },
  "spark_env_vars": {
    "PYSPARK_PYTHON": "/databricks/python3/bin/python3"
  },
  "libraries": [
    {
      "pypi": {
        "package": "yfinance>=0.2.0"
      }
    },
    {
      "pypi": {
        "package": "alpha-vantage>=2.3.0"
      }
    },
    {
      "pypi": {
        "package": "fredapi>=0.5.0"
      }
    },
    {
      "pypi": {
        "package": "openai>=1.0.0"
      }
    },
    {
      "pypi": {
        "package": "anthropic>=0.18.0"
      }
    }
  ]
}
```

### Cluster Creation Steps

1. **Go to Compute** → **Create Cluster**
2. **Configure**:
   - **Cluster Mode**: Standard or High Concurrency
   - **Databricks Runtime**: 13.3 LTS or later
   - **Python Version**: 3.10+
   - **Node Type**: i3.xlarge or m5.xlarge (start small)
   - **Workers**: 2 (can scale later)
3. **Advanced Options**:
   - **Spark Config**: Add Delta optimizations (see above)
   - **Environment Variables**: Add API keys (or use Secrets)
4. **Libraries**: Install from requirements.txt or add individually

### Install Libraries on Cluster

**Option 1: Cluster Libraries Tab**
- Go to cluster → **Libraries** → **Install New**
- Install from PyPI or upload wheel files

**Option 2: Notebook Installation**
```python
%pip install -r /Workspace/Repos/your-repo/stocks/requirements.txt
```

**Option 3: Init Script** (for persistent installation)
```bash
#!/bin/bash
pip install yfinance alpha-vantage fredapi openai anthropic
```

---

## 📁 Step 5: Project Structure in Databricks

### A. Upload Code to Databricks

**Option 1: Databricks Repos (Recommended)**

1. **Create Repo**:
   - Go to **Repos** → **Add Repo**
   - Connect to your Git repository
   - Or create new repo and push code

2. **Clone Your Repo**:
   ```bash
   # In Databricks Repos
   git clone https://github.com/your-username/stocks-ai.git
   ```

**Option 2: Upload Files**

1. **Create Folder**: `/Workspace/Users/your-email@company.com/stocks/`
2. **Upload Files**: Use Databricks UI or CLI
3. **Update Paths**: Modify `sys.path.append()` in notebooks

### B. Notebook Organization

Create folder structure:
```
/Workspace/Repos/your-repo/stocks/
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_agent_demo.ipynb
│   └── 03_full_pipeline.ipynb
├── src/
│   ├── agents/
│   ├── data/
│   ├── portfolio/
│   └── ...
└── setup/
    └── init.sql
```

### C. Update Notebook Paths

In each notebook, update the path:
```python
import sys
# Update this to your actual repo path
sys.path.append('/Workspace/Repos/your-username/stocks-ai/stocks')
```

---

## 🔐 Step 6: Permissions & Access Control

### A. Unity Catalog Permissions

**Grant Access to Catalog**:
```sql
-- As admin
GRANT USE CATALOG ON CATALOG stocks_ai TO `your-email@company.com`;
GRANT USE SCHEMA ON SCHEMA stocks_ai.fortune100 TO `your-email@company.com`;
GRANT SELECT, INSERT, UPDATE ON TABLE stocks_ai.fortune100.* TO `your-email@company.com`;
```

### B. Cluster Permissions

- **Can Attach To**: Users who can run notebooks on cluster
- **Can Restart**: Users who can restart cluster
- **Can Manage**: Only admins

### C. Secret Scope Permissions

```python
# Grant access to secret scope
databricks secrets put-acl --scope stocks_ai_secrets --principal your-email@company.com --permission READ
```

---

## 📊 Step 7: MLflow Configuration

### A. Create MLflow Experiment

**Option 1: Using UI**
1. Go to **Experiments** → **Create Experiment**
2. Path: `/Shared/stocks_ai/experiments`

**Option 2: Using Code**
```python
import mlflow

mlflow.set_experiment("/Shared/stocks_ai/experiments")
```

### B. MLflow Tracking URI

**Default**: Already configured to use Databricks tracking
```python
# No configuration needed - uses Databricks MLflow by default
mlflow.set_tracking_uri("databricks")
```

---

## 🧪 Step 8: Test Your Setup

### A. Test Data Ingestion

Create test notebook:
```python
# Test notebook
import sys
sys.path.append('/Workspace/Repos/your-repo/stocks')

from src.data.loaders import DataLoader
from datetime import date

# Test data loader
loader = DataLoader()
company = loader.get_company_info("AAPL")
print(f"Company: {company.company_name}")
print(f"Sector: {company.sector}")

# Test fundamentals
fundamentals = loader.get_fundamentals("AAPL", date.today())
print(f"P/E Ratio: {fundamentals.pe_ratio}")
```

### B. Test Agent

```python
from src.agents.fundamentals_agent import FundamentalsAgent

agent = FundamentalsAgent()
prediction = agent.generate_prediction("AAPL")
print(f"Predicted Return: {prediction.predicted_return}%")
print(f"Confidence: {prediction.confidence_score}")
```

### C. Test Delta Lake

```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()

# Test writing to Delta
df = spark.createDataFrame([{"symbol": "AAPL", "test": "data"}])
df.write.format("delta").saveAsTable("stocks_ai.fortune100.test_table")

# Test reading
spark.read.table("stocks_ai.fortune100.test_table").show()
```

---

## 🔄 Step 9: Data Ingestion Workflow

### A. Initial Data Load

**Create notebook**: `notebooks/00_initial_setup.ipynb`

```python
# Load Fortune 100 companies
fortune100_symbols = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", 
    "META", "TSLA", "BRK.B", "V", "JNJ",
    # ... add all Fortune 100
]

from src.data.loaders import DataLoader
from datetime import date
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
loader = DataLoader()

# Load company info
companies = []
for symbol in fortune100_symbols:
    company = loader.get_company_info(symbol)
    if company:
        companies.append(company.dict())

df = spark.createDataFrame(companies)
df.write.format("delta").mode("overwrite").saveAsTable("stocks_ai.fortune100.companies")
```

### B. Scheduled Data Refresh

**Create Databricks Job**:

1. **Jobs** → **Create Job**
2. **Task Type**: Notebook
3. **Notebook**: `notebooks/01_data_ingestion.ipynb`
4. **Schedule**: Daily at 6 AM UTC (after market close)
5. **Cluster**: Use existing cluster or create job cluster

**Job Configuration**:
```json
{
  "name": "daily-stock-data-ingestion",
  "schedule": {
    "quartz_cron_expression": "0 0 6 * * ?",
    "timezone_id": "UTC"
  },
  "tasks": [
    {
      "task_key": "ingest_data",
      "notebook_task": {
        "notebook_path": "/Workspace/Repos/your-repo/stocks/notebooks/01_data_ingestion"
      },
      "existing_cluster_id": "your-cluster-id"
    }
  ]
}
```

---

## 📝 Step 10: Configuration File

### Update `databricks.yml`

```yaml
workspace:
  host: https://your-workspace.cloud.databricks.com
  profile: DEFAULT

catalog:
  name: stocks_ai
  comment: "Multi-supervisor AI system for stock prediction"

schema:
  name: fortune100
  comment: "Fortune 100 companies data and predictions"

# MLflow experiment
mlflow:
  experiment_name: "/Shared/stocks_ai/experiments"
  tracking_uri: "databricks"

# Unity Catalog paths (if using S3)
paths:
  raw_data: "s3://your-bucket/stocks/raw"
  processed_data: "s3://your-bucket/stocks/processed"
  predictions: "s3://your-bucket/stocks/predictions"
```

---

## ✅ Final Checklist

Before running the system:

- [ ] Unity Catalog enabled and schemas created
- [ ] Cluster created with required libraries
- [ ] API keys stored in Databricks Secrets
- [ ] Code uploaded to Databricks Repos
- [ ] MLflow experiment created
- [ ] Test data ingestion successful
- [ ] Test agent prediction successful
- [ ] Delta Lake read/write working
- [ ] Permissions configured correctly

---

## 🆘 Troubleshooting

### Issue: "Cannot find module 'src'"

**Solution**: Update path in notebook:
```python
import sys
sys.path.append('/Workspace/Repos/your-actual-repo-path/stocks')
```

### Issue: "Access denied to catalog"

**Solution**: Grant permissions:
```sql
GRANT USE CATALOG ON CATALOG stocks_ai TO `your-email@company.com`;
```

### Issue: "API key not found"

**Solution**: Check secrets scope:
```python
# Verify secret exists
dbutils.secrets.list(scope="stocks_ai_secrets")
```

### Issue: "Cluster libraries not installed"

**Solution**: Install via notebook:
```python
%pip install yfinance alpha-vantage fredapi openai anthropic
```

---

## 📞 Next Steps

1. **Complete setup checklist above**
2. **Run test notebooks** to verify everything works
3. **Load initial data** (Fortune 100 companies)
4. **Run first prediction** using demo notebook
5. **Set up scheduled jobs** for data refresh

---

## 🎯 What I Need From You

To help you further, please provide:

1. **Databricks Workspace URL**: `https://your-workspace.cloud.databricks.com`
2. **Unity Catalog Status**: Is it enabled?
3. **S3 Bucket Name** (if using): `s3://your-bucket/`
4. **API Keys Status**: Which ones do you have?
5. **Cluster Access**: Can you create clusters?
6. **Any Errors**: Share error messages if you encounter issues

Once you provide this, I can help you with:
- Specific configuration for your workspace
- Troubleshooting any setup issues
- Optimizing cluster configuration
- Setting up data pipelines
