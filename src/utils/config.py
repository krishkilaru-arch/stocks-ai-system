"""Configuration management for the multi-supervisor AI system."""
import os
from typing import Optional

# Handle Pydantic v2 BaseSettings import
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    PYDANTIC_V2 = True
except ImportError:
    try:
        from pydantic import BaseSettings
        PYDANTIC_V2 = False
    except ImportError:
        # Fallback: use regular class if pydantic not available
        BaseSettings = object
        PYDANTIC_V2 = False

from pydantic import Field


class Config(BaseSettings):
    """Application configuration."""
    
    # Databricks
    databricks_host: Optional[str] = Field(default=None, json_schema_extra={"env": "DATABRICKS_HOST"})
    databricks_token: Optional[str] = Field(default=None, json_schema_extra={"env": "DATABRICKS_TOKEN"})
    catalog_name: str = Field(default="stocks_ai", json_schema_extra={"env": "CATALOG_NAME"})
    schema_name: str = Field(default="fortune100", json_schema_extra={"env": "SCHEMA_NAME"})
    
    # Databricks Secrets (alternative to env vars)
    use_databricks_secrets: bool = Field(default=True, json_schema_extra={"env": "USE_DATABRICKS_SECRETS"})
    secrets_scope: str = Field(default="stocks_ai_secrets", json_schema_extra={"env": "SECRETS_SCOPE"})
    
    # LLM Configuration
    openai_api_key: Optional[str] = Field(default=None, json_schema_extra={"env": "OPENAI_API_KEY"})
    anthropic_api_key: Optional[str] = Field(default=None, json_schema_extra={"env": "ANTHROPIC_API_KEY"})
    llm_provider: str = Field(default="databricks", json_schema_extra={"env": "LLM_PROVIDER"})  # databricks, openai, or anthropic
    llm_model: str = Field(default="databricks-meta-llama-3-1-70b-instruct", json_schema_extra={"env": "LLM_MODEL"})
    
    # Data Sources
    yahoo_finance_enabled: bool = Field(default=True, json_schema_extra={"env": "YAHOO_FINANCE_ENABLED"})
    alpha_vantage_api_key: Optional[str] = Field(default=None, json_schema_extra={"env": "ALPHA_VANTAGE_API_KEY"})
    fred_api_key: Optional[str] = Field(default=None, json_schema_extra={"env": "FRED_API_KEY"})
    
    # MLflow
    mlflow_experiment_name: str = Field(default="/Shared/stocks_ai/experiments", json_schema_extra={"env": "MLFLOW_EXPERIMENT"})
    mlflow_tracking_uri: str = Field(default="databricks", json_schema_extra={"env": "MLFLOW_TRACKING_URI"})
    
    # Prediction settings
    default_prediction_horizon_days: int = Field(default=30, json_schema_extra={"env": "PREDICTION_HORIZON_DAYS"})
    min_confidence_threshold: float = Field(default=0.6, json_schema_extra={"env": "MIN_CONFIDENCE_THRESHOLD"})
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load secrets from Databricks if available
        if self.use_databricks_secrets:
            try:
                import dbutils
                if not self.openai_api_key:
                    try:
                        self.openai_api_key = dbutils.secrets.get(scope=self.secrets_scope, key="openai_api_key")
                    except:
                        pass
                if not self.anthropic_api_key:
                    try:
                        self.anthropic_api_key = dbutils.secrets.get(scope=self.secrets_scope, key="anthropic_api_key")
                    except:
                        pass
                if not self.alpha_vantage_api_key:
                    try:
                        self.alpha_vantage_api_key = dbutils.secrets.get(scope=self.secrets_scope, key="alpha_vantage_api_key")
                    except:
                        pass
                if not self.fred_api_key:
                    try:
                        self.fred_api_key = dbutils.secrets.get(scope=self.secrets_scope, key="fred_api_key")
                    except:
                        pass
            except:
                # dbutils not available (not in Databricks environment)
                pass
    
    def get_secret(self, key: str) -> Optional[str]:
        """Get secret from Databricks Secrets if available, else from env."""
        if self.use_databricks_secrets:
            try:
                # Try to use dbutils (available in Databricks notebooks)
                try:
                    import dbutils
                    return dbutils.secrets.get(scope=self.secrets_scope, key=key)
                except:
                    # Fallback to environment variable
                    return os.getenv(key.upper())
            except:
                # Fallback to environment variable
                return os.getenv(key.upper())
        return os.getenv(key.upper())


# Set up model config based on Pydantic version
if PYDANTIC_V2:
    # Pydantic v2: use model_config attribute
    Config.model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix=""
    )
else:
    # Pydantic v1: use nested Config class
    class ConfigClass:
        env_file = ".env"
        env_file_encoding = "utf-8"
    Config.Config = ConfigClass


# Global config instance
config = Config()
