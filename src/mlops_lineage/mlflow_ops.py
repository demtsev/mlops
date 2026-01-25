"""
MLflow operations module

Provides functions for MLflow operations including:
- Configuring MLflow tracking URI
- Registering models with lineage tags
- Retrieving model version information
- Listing model versions

Author: MLOps Team
Date: January 2026
"""

import os
from typing import Dict, Optional, List
import mlflow
from mlflow.tracking import MlflowClient
from .shell import print_success, print_info, print_error
from .config import config


def configure_mlflow() -> None:
    """
    Configure MLflow to use Azure ML tracking URI.
    
    Raises:
        RuntimeError: If MLFLOW_TRACKING_URI not set in .env
    """
    config.validate_mlflow_uri()
    
    tracking_uri = config.MLFLOW_TRACKING_URI
    mlflow.set_tracking_uri(tracking_uri)
    
    print_info(f"MLflow tracking URI: {tracking_uri}")


def register_model(
    model_uri: str,
    model_name: str,
    dataset_id: str,
    dataset_version: str,
    code_commit: str,
    run_id: Optional[str] = None,
    experiment_name: Optional[str] = None,
    additional_tags: Optional[Dict[str, str]] = None,
) -> int:
    """
    Register a model in MLflow Model Registry with lineage tags.
    
    Args:
        model_uri: URI to the model (e.g., "runs:/<run_id>/model")
        model_name: Name of the model to register
        dataset_id: Dataset identifier used for training
        dataset_version: Dataset version (git commit hash with "git:" prefix)
        code_commit: Git commit hash of training code
        run_id: Optional MLflow run ID
        experiment_name: Optional experiment name
        additional_tags: Optional additional tags to attach
        
    Returns:
        Model version number
        
    Raises:
        RuntimeError: If model registration fails
    """
    configure_mlflow()
    client = MlflowClient()
    
    print_info(f"Registering model '{model_name}'...")
    
    # Register model
    model_version = client.create_model_version(
        name=model_name,
        source=model_uri,
        run_id=run_id,
    )
    
    version_number = int(model_version.version)
    print_success(f"Model '{model_name}' registered as version {version_number}")
    
    # Set lineage tags
    tags = {
        "dataset_id": dataset_id,
        "dataset_version": dataset_version,
        "code_commit": code_commit,
    }
    
    if run_id:
        tags["train_run_id"] = run_id
    
    if experiment_name:
        tags["mlflow_experiment"] = experiment_name
    
    if additional_tags:
        tags.update(additional_tags)
    
    print_info(f"Setting lineage tags on model version {version_number}...")
    for key, value in tags.items():
        client.set_model_version_tag(model_name, str(version_number), key, value)
        print_info(f"  {key}: {value}")
    
    print_success(f"Lineage tags set for model '{model_name}' version {version_number}")
    
    return version_number


def get_model_version_info(model_name: str, model_version: int) -> Dict[str, str]:
    """
    Get information about a model version, including lineage tags.
    
    Args:
        model_name: Name of the model
        model_version: Version number
        
    Returns:
        Dictionary with model version information and tags
        
    Raises:
        RuntimeError: If model version not found
    """
    configure_mlflow()
    client = MlflowClient()
    
    try:
        model_version_obj = client.get_model_version(model_name, str(model_version))
    except Exception as e:
        raise RuntimeError(
            f"Model version not found: {model_name} version {model_version}\n"
            f"Error: {e}"
        )
    
    info = {
        "model_name": model_name,
        "model_version": str(model_version),
        "source": model_version_obj.source,
        "run_id": model_version_obj.run_id or "N/A",
        "status": model_version_obj.status,
        "creation_timestamp": str(model_version_obj.creation_timestamp),
    }
    
    # Add tags
    if model_version_obj.tags:
        info.update(model_version_obj.tags)
    
    return info


def get_model_lineage(model_name: str, model_version: int) -> Dict[str, str]:
    """
    Get lineage information for a model version.
    
    Args:
        model_name: Name of the model
        model_version: Version number
        
    Returns:
        Dictionary with dataset_id, dataset_version, and code_commit
        
    Raises:
        RuntimeError: If lineage tags are missing
    """
    info = get_model_version_info(model_name, model_version)
    
    # Extract lineage tags
    dataset_id = info.get("dataset_id")
    dataset_version = info.get("dataset_version")
    code_commit = info.get("code_commit")
    
    if not dataset_id or not dataset_version or not code_commit:
        raise RuntimeError(
            f"Lineage tags missing for model '{model_name}' version {model_version}.\n"
            f"Found tags: dataset_id={dataset_id}, "
            f"dataset_version={dataset_version}, code_commit={code_commit}\n"
            f"Please ensure model was registered with lineage tags."
        )
    
    return {
        "dataset_id": dataset_id,
        "dataset_version": dataset_version,
        "code_commit": code_commit,
    }


def list_model_versions(model_name: str, max_results: int = 10) -> List[Dict[str, str]]:
    """
    List versions of a registered model.
    
    Args:
        model_name: Name of the model
        max_results: Maximum number of versions to return
        
    Returns:
        List of dictionaries with model version information
        
    Raises:
        RuntimeError: If model not found
    """
    configure_mlflow()
    client = MlflowClient()
    
    try:
        versions = client.search_model_versions(f"name='{model_name}'", max_results=max_results)
    except Exception as e:
        raise RuntimeError(f"Failed to list model versions: {e}")
    
    if not versions:
        print_info(f"No versions found for model '{model_name}'")
        return []
    
    result = []
    for version in versions:
        version_info = {
            "version": version.version,
            "status": version.status,
            "creation_timestamp": str(version.creation_timestamp),
        }
        
        # Add lineage tags if available
        if version.tags:
            version_info["dataset_id"] = version.tags.get("dataset_id", "N/A")
            version_info["dataset_version"] = version.tags.get("dataset_version", "N/A")
            version_info["code_commit"] = version.tags.get("code_commit", "N/A")
        
        result.append(version_info)
    
    return result


def set_experiment(experiment_name: str) -> None:
    """
    Set the active MLflow experiment.
    
    Args:
        experiment_name: Name of the experiment
    """
    configure_mlflow()
    mlflow.set_experiment(experiment_name)
    print_info(f"Active experiment: {experiment_name}")
