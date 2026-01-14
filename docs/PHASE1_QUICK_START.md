# Phase 1: Quick Start Guide

This guide helps you quickly get through Phase 1 setup. Follow these steps in order.

## 🚀 Quick Steps (30-60 minutes)

### Step 1: Access Databricks (5 min)
1. Log into your Databricks workspace
2. Verify you can see:
   - **Compute** in left sidebar
   - **SQL** or **SQL Editor** in left sidebar
   - **Catalog** in left sidebar (Unity Catalog)

### Step 2: Run SQL Setup (10 min)
1. Click **SQL** or **SQL Editor**
2. Open the file `setup/init.sql` from your repository
3. Copy the entire contents
4. Paste into SQL Editor
5. Click **Run** (or press Shift+Enter)
6. Verify success - you should see:
   - Catalog `stocks_ai` created
   - 4 schemas created (fortune100, signals, agents, meta)
   - Multiple tables created

**Quick verification:**
```sql
SHOW SCHEMAS IN stocks_ai;
```

### Step 3: Create Cluster (15 min)
1. Click **Compute** in left sidebar
2. Click **Create Cluster**
3. Configure:
   - **Name**: `stocks-ai-cluster`
   - **Runtime**: **13.3 LTS** (or latest)
   - **Node Type**: `i3.xlarge` or `m5.xlarge` (start small)
   - **Workers**: **2**
   - **Auto Termination**: **30 minutes**
4. Click **Create Cluster**
5. Wait for cluster to start (green status)

### Step 4: Install Libraries (10 min)
1. Click on your cluster name
2. Go to **Libraries** tab
3. Click **Install New**
4. Select **PyPI**
5. Install these libraries (one by one or upload requirements.txt):
   - `yfinance>=0.2.0`
   - `openai>=1.0.0` (optional)
   - `pydantic>=2.0.0`
   - `python-dotenv>=1.0.0`
   - `alpha-vantage>=2.3.0` (optional)
   - `fredapi>=0.5.0` (optional)

**Note**: Cluster will restart after installing libraries.

### Step 5: Upload Code (10 min)

**Option A: Databricks Repos (Recommended)**
1. Click **Repos** in left sidebar
2. Click **Add Repo**
3. Select **Clone remote Git repository**
4. Enter: `https://github.com/krishkilaru-arch/stocks-ai-system.git`
5. Click **Create Repo**
6. Wait for clone to complete

**Option B: Workspace Upload**
1. Click **Workspace** in left sidebar
2. Navigate to your user folder
3. Create folder: `stocks-ai-system`
4. Upload files using **Add** → **File**

### Step 6: Set API Keys (5 min) - Optional

**Option A: Cluster Environment Variables (Easier)**
1. Go to cluster → **Configuration** → **Advanced Options**
2. Scroll to **Environment Variables**
3. Add:
   ```
   OPENAI_API_KEY=your-key-here
   ALPHA_VANTAGE_API_KEY=your-key-here
   FRED_API_KEY=your-key-here
   ```
4. **Restart cluster**

**Option B: Databricks Secrets (More Secure)**
1. Use Databricks CLI:
   ```bash
   databricks secrets create-scope --scope stocks_ai_secrets
   databricks secrets put --scope stocks_ai_secrets --key openai_api_key
   ```

**Note**: You can skip API keys for now - Yahoo Finance works without keys!

### Step 7: Run Setup Notebook (15 min)
1. Open `notebooks/00_initial_setup.ipynb` in Databricks
2. Attach notebook to your cluster
3. Run all cells (or run individually)
4. Check for errors
5. Verify output shows:
   - ✓ Python path configured
   - ✓ Yahoo Finance works
   - ✓ Companies loaded
   - ✓ Delta table accessible

### Step 8: Verify Everything (5 min)

**Test SQL:**
```sql
SELECT * FROM stocks_ai.fortune100.companies LIMIT 10;
```

**Test Python:**
```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()
df = spark.sql("SELECT * FROM stocks_ai.fortune100.companies")
df.show()
```

## ✅ Success Checklist

Before moving to Phase 2, verify:

- [ ] Unity Catalog enabled and accessible
- [ ] Catalog `stocks_ai` exists
- [ ] Schemas created (fortune100, signals, agents, meta)
- [ ] Cluster running with libraries installed
- [ ] Code uploaded to Databricks
- [ ] Setup notebook runs without errors
- [ ] Companies table has data (20+ companies)
- [ ] Can query data via SQL
- [ ] MLflow experiment created

## 🆘 Common Issues

### "Cannot find catalog stocks_ai"
**Solution**: Make sure you ran `setup/init.sql` in SQL Editor first.

### "Cluster not found"
**Solution**: Make sure cluster is running (green status). Click "Start" if stopped.

### "Module not found"
**Solution**: Install libraries on cluster. Go to cluster → Libraries → Install.

### "Permission denied"
**Solution**: Check your permissions. You may need admin to create catalog.

### "API key not found"
**Solution**: That's OK! You can proceed without API keys. Yahoo Finance works without keys.

## 📝 Next Steps

Once Phase 1 is complete:
1. ✅ Celebrate! You've set up the foundation
2. 📖 Review Phase 2: Core Infrastructure
3. 🎯 Start Phase 2 when ready

## 🎯 Expected Time

- **Minimum**: 30 minutes (if everything goes smoothly)
- **Typical**: 45-60 minutes (with some troubleshooting)
- **Maximum**: 2 hours (if encountering issues)

**Good luck!** 🚀
