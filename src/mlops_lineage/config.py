"""
Configuration module for MLOps Lineage

Loads and validates environment variables from .env file.
Provides centralized configuration for Azure, DVC, and MLflow settings.

Author: MLOps Team
Date: January 2026
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """
    Central configuration class that loads settings from .env file.
    
    Attributes:
        AZURE_SUBSCRIPTION_ID: Azure subscription ID
        AZURE_RESOURCE_GROUP: Azure resource group name
        AZURE_ML_WORKSPACE: Azure ML workspace name
        DVC_AZURE_CONTAINER: Azure Blob container for DVC
        DVC_AZURE_PATH: Path prefix in Azure Blob container
        AZURE_STORAGE_CONNECTION_STRING: Optional connection string for DVC auth
        MLFLOW_TRACKING_URI: MLflow tracking URI (auto-populated)
        REPO_ROOT: Repository root directory
    """
    
    def __init__(self):
        """Initialize configuration by loading .env file."""
        # Find and load .env file from repository root
        self.REPO_ROOT = self._find_repo_root()
        env_file = self.REPO_ROOT / ".env"
        
        if env_file.exists():
            load_dotenv(env_file)
        else:
            # Try loading from current directory as fallback
            load_dotenv()
    
    @staticmethod
    def _find_repo_root() -> Path:
        """
        Find repository root by looking for .git directory.
        
        Returns:
            Path to repository root
            
        Raises:
            RuntimeError: If .git directory not found
        """
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        
        # Fallback to current directory if .git not found
        return Path.cwd()
    
    @property
    def AZURE_SUBSCRIPTION_ID(self) -> str:
        """Get Azure subscription ID from environment."""
        value = os.getenv("AZURE_SUBSCRIPTION_ID", "")
        if not value:
            raise RuntimeError(
                "AZURE_SUBSCRIPTION_ID not set in .env file. "
                "Please copy .env.example to .env and fill in your values."
            )
        return value
    
    @property
    def AZURE_RESOURCE_GROUP(self) -> str:
        """Get Azure resource group from environment."""
        value = os.getenv("AZURE_RESOURCE_GROUP", "")
        if not value:
            raise RuntimeError(
                "AZURE_RESOURCE_GROUP not set in .env file. "
                "Please copy .env.example to .env and fill in your values."
            )
        return value
    
    @property
    def AZURE_ML_WORKSPACE(self) -> str:
        """Get Azure ML workspace name from environment."""
        value = os.getenv("AZURE_ML_WORKSPACE", "")
        if not value:
            raise RuntimeError(
                "AZURE_ML_WORKSPACE not set in .env file. "
                "Please copy .env.example to .env and fill in your values."
            )
        return value
    
    @property
    def DVC_AZURE_CONTAINER(self) -> str:
        """Get DVC Azure Blob container name from environment."""
        return os.getenv("DVC_AZURE_CONTAINER", "dvc-storage")
    
    @property
    def DVC_AZURE_PATH(self) -> str:
        """Get DVC Azure Blob path prefix from environment."""
        return os.getenv("DVC_AZURE_PATH", "datasets")
    
    @property
    def AZURE_STORAGE_CONNECTION_STRING(self) -> Optional[str]:
        """Get optional Azure Storage connection string from environment."""
        return os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    
    @property
    def MLFLOW_TRACKING_URI(self) -> Optional[str]:
        """Get MLflow tracking URI from environment."""
        return os.getenv("MLFLOW_TRACKING_URI")
    
    def validate_azure_settings(self) -> None:
        """
        Validate that required Azure settings are present.
        
        Raises:
            RuntimeError: If required settings are missing
        """
        # Access properties to trigger validation
        _ = self.AZURE_SUBSCRIPTION_ID
        _ = self.AZURE_RESOURCE_GROUP
        _ = self.AZURE_ML_WORKSPACE
    
    def validate_mlflow_uri(self) -> None:
        """
        Validate that MLflow tracking URI is set.
        
        Raises:
            RuntimeError: If MLFLOW_TRACKING_URI is not set
        """
        if not self.MLFLOW_TRACKING_URI:
            raise RuntimeError(
                "MLFLOW_TRACKING_URI not set in .env file. "
                "Please run: python -m mlops_lineage azureml set-tracking-uri"
            )


# Global configuration instance
config = Config()
