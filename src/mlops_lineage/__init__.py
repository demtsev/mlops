"""
MLOps Lineage Package

Production-quality MLOps toolkit for dataset and model versioning with:
- Git for code and metadata
- DVC for dataset versioning on Azure Blob Storage
- MLflow for experiment tracking and Model Registry on Azure ML
- Strong lineage tracking: model_version -> dataset_version -> exact data

Author: MLOps Team
Date: January 2026
"""

__version__ = "1.0.0"
__all__ = [
    "config",
    "shell",
    "dvc_ops",
    "git_ops",
    "azureml_ops",
    "mlflow_ops",
    "training_demo",
]
