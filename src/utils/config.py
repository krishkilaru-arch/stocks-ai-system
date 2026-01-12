"""Configuration management for the multi-supervisor AI system."""
import os
from typing import Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from pydantic import Field


class Config(BaseSettings):
    """Application configuration."""
    
    # Databricks
    databricks_host: Optional[str] = Field(None, env="DATABRICKS_HOST")
    databricks_token: Optional[str] = Field(None, env="DATABRICKS_TOKEN")
    catalog_name: str = Field("stocks_ai", env="CATALOG_NAME")
    schema_name: str = Field("fortune100", env="SCHEMA_NAME")
    
    # Databricks Secrets (alternative to env vars)
    use_databricks_secrets: bool = Field(True, env="USE_DATABRICKS_SECRETS")
    secrets_scope: str = Field("stocks_ai_secrets", env="SECRETS_SCOPE")
    
    # LLM Configuration
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    llm_provider: str = Field("openai", env="LLM_PROVIDER")  # openai or anthropic
    llm_model: str = Field("gpt-4-turbo-preview", env="LLM_MODEL")
    
    def get_secret(self, key: str) -> Optional[str]:
        """Get secret from Databricks Secrets if available, else from env."""
        if self.use_databricks_secrets:
            try:
                from pyspark.sql import SparkSession
                spark = SparkSession.builder.getOrCreate()
                return spark.conf.get(f"spark.databricks.secrets.get.{self.secrets_scope}.{key}")
            except:
                # Fallback to environment variable
                return os.getenv(key.upper())
        return os.getenv(key.upper())
    
    # Data Sources
    yahoo_finance_enabled: bool = Field(True, env="YAHOO_FINANCE_ENABLED")
    alpha_vantage_api_key: Optional[str] = Field(None, env="ALPHA_VANTAGE_API_KEY")
    fred_api_key: Optional[str] = Field(None, env="FRED_API_KEY")
    
    # MLflow
    mlflow_experiment_name: str = Field("/Shared/stocks_ai/experiments", env="MLFLOW_EXPERIMENT")
    mlflow_tracking_uri: str = Field("databricks", env="MLFLOW_TRACKING_URI")
    
    # Prediction settings
    default_prediction_horizon_days: int = Field(30, env="PREDICTION_HORIZON_DAYS")
    min_confidence_threshold: float = Field(0.6, env="MIN_CONFIDENCE_THRESHOLD")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global config instance
config = Config()
