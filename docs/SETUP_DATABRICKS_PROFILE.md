# Databricks Profile Setup Guide

This guide will help you set up your Databricks profile for CLI and SDK access.

## Option 1: Using Databricks CLI Profile (Recommended)

### Step 1: Install Databricks CLI

```bash
pip install databricks-cli
```

Or using Homebrew (macOS):
```bash
brew install databricks/tap/databricks
```

### Step 2: Create Profile Configuration

1. **Create the profile file**:
   ```bash
   mkdir -p ~/.databricks
   cp .databrickscfg.example ~/.databrickscfg
   ```

2. **Edit the profile**:
   ```bash
   nano ~/.databrickscfg
   # or
   vim ~/.databrickscfg
   ```

3. **Update with your credentials**:
   ```ini
   [DEFAULT]
   host = https://dbc-47a3dcaa-ae3e.cloud.databricks.com
   token = your-personal-access-token-here
   ```

### Step 3: Get Your Personal Access Token

1. Log into your Databricks workspace
2. Click on your **username** (top right) → **User Settings**
3. Go to **Access Tokens** tab
4. Click **Generate New Token**
5. Give it a name (e.g., "stocks-ai-cli")
6. Set expiration (or leave as default)
7. Click **Generate**
8. **Copy the token immediately** (you won't see it again!)
9. Paste it into `~/.databrickscfg`

### Step 4: Verify Profile

```bash
databricks workspace ls
```

If successful, you should see your workspace folders.

## Option 2: Using Environment Variables

Instead of a profile file, you can use environment variables:

```bash
export DATABRICKS_HOST=https://dbc-47a3dcaa-ae3e.cloud.databricks.com
export DATABRICKS_TOKEN=your-token-here
```

Or add to your `~/.zshrc` or `~/.bashrc`:
```bash
echo 'export DATABRICKS_HOST=https://dbc-47a3dcaa-ae3e.cloud.databricks.com' >> ~/.zshrc
echo 'export DATABRICKS_TOKEN=your-token-here' >> ~/.zshrc
source ~/.zshrc
```

## Option 3: Using Databricks SDK (Python)

If you're using the Databricks SDK in Python, you can configure it programmatically:

```python
from databricks.sdk import WorkspaceClient

# Option A: Use profile
w = WorkspaceClient(profile='DEFAULT')

# Option B: Use environment variables
w = WorkspaceClient()

# Option C: Explicit configuration
w = WorkspaceClient(
    host='https://dbc-47a3dcaa-ae3e.cloud.databricks.com',
    token='your-token-here'
)
```

## Multiple Profiles

You can create multiple profiles for different workspaces:

```ini
[DEFAULT]
host = https://dbc-47a3dcaa-ae3e.cloud.databricks.com
token = your-dev-token

[PRODUCTION]
host = https://your-prod-workspace.cloud.databricks.com
token = your-prod-token

[STAGING]
host = https://your-staging-workspace.cloud.databricks.com
token = your-staging-token
```

Then use them:
```bash
databricks workspace ls --profile PRODUCTION
```

Or in Python:
```python
w = WorkspaceClient(profile='PRODUCTION')
```

## Using with databricks.yml

The `databricks.yml` file is used for **Databricks Asset Bundles**. It references the profile:

```yaml
workspace:
  host: https://dbc-47a3dcaa-ae3e.cloud.databricks.com
  profile: DEFAULT  # This references [DEFAULT] in ~/.databrickscfg
```

## Security Best Practices

1. **Never commit tokens to git**:
   - `.databrickscfg` is in `.gitignore`
   - Use `.databrickscfg.example` as a template

2. **Use token expiration**:
   - Set reasonable expiration dates
   - Rotate tokens regularly

3. **Use least privilege**:
   - Only grant necessary permissions
   - Use service principals for automation

4. **Store tokens securely**:
   - Use password managers
   - Consider using Databricks Secrets for automation

## Troubleshooting

### Error: "Could not find profile"
- Check that `~/.databrickscfg` exists
- Verify the profile name matches in `databricks.yml`
- Check file permissions: `chmod 600 ~/.databrickscfg`

### Error: "Invalid token"
- Regenerate your access token
- Check token hasn't expired
- Verify you're using the correct workspace URL

### Error: "Permission denied"
- Check your user permissions in Databricks
- Verify you have workspace access
- Contact your Databricks admin

## Next Steps

Once your profile is configured:

1. ✅ Test connection: `databricks workspace ls`
2. ✅ Verify Unity Catalog: `databricks unity-catalog catalogs list`
3. ✅ Test SDK: Run a simple Python script using `WorkspaceClient`
4. ✅ Proceed with Phase 1 setup in Databricks

## Additional Resources

- [Databricks CLI Documentation](https://docs.databricks.com/dev-tools/cli/index.html)
- [Databricks SDK Documentation](https://databricks-sdk-py.readthedocs.io/)
- [Databricks Asset Bundles](https://docs.databricks.com/dev-tools/bundles/index.html)
