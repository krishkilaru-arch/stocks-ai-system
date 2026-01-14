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
    databricks_host: Optional[str] = None
    databricks_token: Optional[str] = None
    catalog_name: str = "stocks_ai"
    schema_name: str = "fortune100"
    
    # Databricks Secrets (alternative to env vars)
    use_databricks_secrets: bool = True
    secrets_scope: str = "stocks_ai_secrets"
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    llm_provider: str = "databricks"  # databricks, openai, or anthropic
    llm_model: str = "databricks-meta-llama-3-1-70b-instruct"
    
    # Data Sources
    yahoo_finance_enabled: bool = True
    alpha_vantage_api_key: Optional[str] = None
    fred_api_key: Optional[str] = None
    
    # MLflow
    mlflow_experiment_name: str = "/Shared/stocks_ai/experiments"
    mlflow_tracking_uri: str = "databricks"
    
    # Prediction settings
    default_prediction_horizon_days: int = 30
    min_confidence_threshold: float = 0.6
    
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
