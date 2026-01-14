# Folder & Repository Naming Guide

## 🎯 Recommended Folder Structure

### Option 1: Professional & Clear (Recommended) ⭐

```
/Workspace/Repos/your-username/
└── stocks-ai-system/
    └── stocks/
        ├── src/
        ├── notebooks/
        ├── setup/
        └── ...
```

**Repo Name**: `stocks-ai-system`  
**Main Folder**: `stocks`

**Pros**:
- ✅ Professional and clear
- ✅ Easy to reference
- ✅ Good for DAIS proposal
- ✅ Descriptive

**Path in code**:
```python
repo_path = '/Workspace/Repos/your-username/stocks-ai-system/stocks'
```

---

### Option 2: Short & Simple

```
/Workspace/Repos/your-username/
└── stocks-ai/
    └── stocks/
        ├── src/
        ├── notebooks/
        └── ...
```

**Repo Name**: `stocks-ai`  
**Main Folder**: `stocks`

**Pros**:
- ✅ Short and easy to type
- ✅ Clear purpose
- ✅ Good for quick reference

**Path in code**:
```python
repo_path = '/Workspace/Repos/your-username/stocks-ai/stocks'
```

---

### Option 3: DAIS Proposal Specific

```
/Workspace/Repos/your-username/
└── dais2026-stocks-ai/
    └── stocks/
        ├── src/
        ├── notebooks/
        └── ...
```

**Repo Name**: `dais2026-stocks-ai`  
**Main Folder**: `stocks`

**Pros**:
- ✅ Clearly identifies as DAIS project
- ✅ Easy to find later
- ✅ Professional

**Path in code**:
```python
repo_path = '/Workspace/Repos/your-username/dais2026-stocks-ai/stocks'
```

---

### Option 4: Multi-Agent Focused

```
/Workspace/Repos/your-username/
└── multi-agent-stocks/
    └── stocks/
        ├── src/
        ├── notebooks/
        └── ...
```

**Repo Name**: `multi-agent-stocks`  
**Main Folder**: `stocks`

**Pros**:
- ✅ Highlights multi-agent architecture
- ✅ Descriptive of approach
- ✅ Good for proposal

**Path in code**:
```python
repo_path = '/Workspace/Repos/your-username/multi-agent-stocks/stocks'
```

---

## 🏆 My Top Recommendation

### **`stocks-ai-system`** (Option 1)

**Why**:
- Professional and clear
- Easy to understand
- Good for sharing/demo
- Not too long, not too short
- Works well for DAIS proposal

**Full Structure**:
```
/Workspace/Repos/your-username/stocks-ai-system/
└── stocks/
    ├── src/
    │   ├── agents/
    │   ├── data/
    │   ├── portfolio/
    │   ├── backtesting/
    │   ├── governance/
    │   ├── streaming/
    │   ├── scenarios/
    │   └── utils/
    ├── notebooks/
    │   ├── 00_initial_setup.ipynb
    │   ├── 01_data_ingestion.ipynb
    │   ├── 02_agent_demo.ipynb
    │   └── 03_full_pipeline.ipynb
    ├── setup/
    │   └── init.sql
    ├── README.md
    ├── requirements.txt
    └── databricks.yml
```

---

## 📝 Alternative: Workspace Folder (Not Repos)

If you're NOT using Databricks Repos and uploading directly to workspace:

```
/Workspace/Users/your-email@company.com/
└── stocks_ai/
    ├── src/
    ├── notebooks/
    └── ...
```

**Folder Name**: `stocks_ai` (with underscore for workspace folders)

**Path in code**:
```python
repo_path = '/Workspace/Users/your-email@company.com/stocks_ai'
```

---

## ✅ Quick Decision Guide

**Choose Option 1 (`stocks-ai-system`)** if:
- ✅ You want professional naming
- ✅ You're using Databricks Repos
- ✅ You want it to look good in demos
- ✅ You want clear, descriptive name

**Choose Option 2 (`stocks-ai`)** if:
- ✅ You want something shorter
- ✅ You prefer simplicity
- ✅ You're using Repos

**Choose Option 3 (`dais2026-stocks-ai`)** if:
- ✅ You want to clearly mark it as DAIS project
- ✅ You have multiple projects
- ✅ You want easy identification

**Choose Option 4 (`multi-agent-stocks`)** if:
- ✅ You want to emphasize multi-agent architecture
- ✅ That's the key differentiator you want to highlight

---

## 🔧 How to Update Your Code

Once you choose a name, update these files:

### 1. Update `notebooks/00_initial_setup.ipynb`

Change this line:
```python
# Option 1: If using Databricks Repos
repo_path = '/Workspace/Repos/your-username/stocks-ai-system/stocks'  # ← Update this

# Option 2: If uploaded to workspace
# repo_path = '/Workspace/Users/your-email@company.com/stocks_ai'  # ← Or this
```

### 2. Update `databricks.yml` (if using)

```yaml
workspace:
  host: https://your-workspace.cloud.databricks.com
  profile: DEFAULT
  # Add repo path if needed
```

### 3. Update any other notebooks

Check `notebooks/01_data_ingestion.ipynb`, `02_agent_demo.ipynb`, etc. for path references.

---

## 💡 Naming Best Practices

### Do ✅:
- Use lowercase with hyphens: `stocks-ai-system`
- Be descriptive: `multi-agent-stocks`
- Keep it professional: `stocks-ai-system`
- Use consistent naming: same pattern throughout

### Don't ❌:
- Use spaces: `stocks ai system` (bad)
- Use special characters: `stocks@ai#system` (bad)
- Make it too long: `multi-supervisor-ai-system-for-stock-prediction` (too long)
- Use camelCase in folder names: `stocksAiSystem` (inconsistent)

---

## 🎯 Final Recommendation

**Use**: `stocks-ai-system`

**Path**: `/Workspace/Repos/your-username/stocks-ai-system/stocks`

**Why**: Professional, clear, perfect length, great for DAIS proposal!

---

## 📋 Quick Checklist

- [ ] Choose folder/repo name
- [ ] Create folder/repo in Databricks
- [ ] Update `00_initial_setup.ipynb` with correct path
- [ ] Update any other notebooks with path references
- [ ] Test path works in notebook

**Ready to proceed!** 🚀
