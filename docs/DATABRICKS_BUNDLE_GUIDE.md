# Databricks Asset Bundle (DABs) Guide

This guide explains how to use the Databricks Asset Bundle for the stocks-ai-system.

## What is a Databricks Asset Bundle?

A Databricks Asset Bundle (DAB) is a way to deploy and manage Databricks resources as code, including:
- Jobs
- Notebooks
- Clusters
- Libraries
- And more

## Prerequisites

- Databricks CLI installed: `databricks --version`
- Profile configured: `~/.databrickscfg`
- Access to your Databricks workspace

## Bundle Commands

### Validate Bundle

Check if your bundle configuration is valid:

```bash
databricks bundle validate
```

### Deploy Bundle

Deploy all resources defined in the bundle:

```bash
databricks bundle deploy
```

### Run a Job

Run a job defined in the bundle:

```bash
databricks bundle run daily_data_ingestion
```

### Check Status

See what resources are deployed:

```bash
databricks bundle validate
```

### Destroy Resources

Remove all deployed resources (use with caution):

```bash
databricks bundle destroy
```

## Bundle Structure

The bundle is configured in `databricks.yml` and includes:

### Jobs

1. **daily_data_ingestion**
   - Runs: `notebooks/00_initial_setup.ipynb`
   - Schedule: Daily at 6 AM UTC
   - Cluster: Auto-created with 2 workers

2. **phase2_setup**
   - Runs: `notebooks/01_phase2_setup.ipynb`
   - Cluster: Auto-created with 2 workers

### Variables

- `catalog_name`: Unity Catalog name (default: "stocks_ai")
- `experiment_path`: MLflow experiment path (default: "/Shared/stocks_ai/experiments")

## Quick Start

1. **Validate the bundle**:
   ```bash
   databricks bundle validate
   ```

2. **Deploy the bundle** (creates jobs in Databricks):
   ```bash
   databricks bundle deploy
   ```

3. **Run a job manually**:
   ```bash
   databricks bundle run daily_data_ingestion
   ```

## Notes

- Unity Catalog resources (catalogs, schemas, tables) are created via SQL (`setup/init.sql`)
- The bundle uses notebook paths from your Repos
- Clusters are created on-demand for each job run
- Jobs can be scheduled or run manually

## Troubleshooting

### Error: "Top-level folder can only contain repos"
- The bundle automatically uses a workspace path for deployment files
- This is normal and expected

### Error: "Notebook not found"
- Make sure your code is in Databricks Repos
- Check the notebook path in `databricks.yml`

### Error: "Cluster creation failed"
- Check your cluster permissions
- Verify node types are available in your workspace
- Check your workspace quota

## Additional Resources

- [Databricks Asset Bundles Documentation](https://docs.databricks.com/dev-tools/bundles/index.html)
- [Bundle Configuration Reference](https://docs.databricks.com/dev-tools/bundles/spec.html)
