"""
Training demo module

Provides a minimal training example that demonstrates:
- Loading a dataset
- Training a simple model
- Logging to MLflow
- Registering model with lineage tags

Author: MLOps Team
Date: January 2026
"""

from pathlib import Path
from typing import Dict, Any
import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import pandas as pd

from .config import config
from .git_ops import get_current_commit
from .mlflow_ops import configure_mlflow, register_model, set_experiment
from .shell import print_success, print_info, print_warning


def get_dataset_manifest(dataset_id: str, max_files: int = 100) -> Dict[str, Any]:
    """
    Create a manifest of files in a dataset.
    
    Args:
        dataset_id: Dataset identifier
        max_files: Maximum number of files to list
        
    Returns:
        Dictionary with dataset manifest information
    """
    dataset_path = config.REPO_ROOT / "datasets" / dataset_id
    
    if not dataset_path.exists():
        print_warning(f"Dataset directory not found: {dataset_path}")
        return {
            "dataset_id": dataset_id,
            "exists": False,
            "files": [],
            "total_files": 0,
        }
    
    # Collect all files (not directories)
    all_files = []
    for item in dataset_path.rglob("*"):
        if item.is_file():
            # Store relative path from dataset directory
            rel_path = item.relative_to(dataset_path)
            all_files.append(str(rel_path))
    
    # Limit to max_files to avoid huge logs
    files = sorted(all_files)[:max_files]
    
    manifest = {
        "dataset_id": dataset_id,
        "exists": True,
        "files": files,
        "total_files": len(all_files),
        "truncated": len(all_files) > max_files,
    }
    
    return manifest


def train_demo_model(
    model_name: str,
    dataset_id: str,
    experiment_name: str = "demo_experiments",
    hyperparams: Dict[str, Any] = None,
) -> int:
    """
    Train a demo model and register it with MLflow.
    
    This is a minimal example using the Iris dataset.
    Replace this with your actual training logic.
    
    Args:
        model_name: Name to register the model as
        dataset_id: Dataset identifier (for lineage tracking)
        experiment_name: MLflow experiment name
        hyperparams: Optional hyperparameters for the model
        
    Returns:
        Model version number
        
    Raises:
        RuntimeError: If training or registration fails
    """
    configure_mlflow()
    set_experiment(experiment_name)
    
    # Get current git commit for code lineage
    code_commit = get_current_commit()
    dataset_version = f"git:{code_commit}"
    
    print_info(f"Training demo model '{model_name}'...")
    print_info(f"  Dataset ID: {dataset_id}")
    print_info(f"  Dataset version: {dataset_version}")
    print_info(f"  Code commit: {code_commit}")
    print_info(f"  Experiment: {experiment_name}")
    
    # Default hyperparameters
    if hyperparams is None:
        hyperparams = {
            "max_iter": 1000,
            "random_state": 42,
        }
    
    # Start MLflow run
    with mlflow.start_run() as run:
        # Load demo data (replace with your actual dataset loading)
        print_info("Loading Iris dataset (demo)...")
        X, y = load_iris(return_X_y=True, as_frame=True)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Log hyperparameters
        mlflow.log_params(hyperparams)
        mlflow.log_param("dataset_id", dataset_id)
        mlflow.log_param("dataset_version", dataset_version)
        
        # Train model
        print_info("Training LogisticRegression model...")
        model = LogisticRegression(**hyperparams)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted")
        
        print_success(f"Training complete. Accuracy: {accuracy:.4f}, F1: {f1:.4f}")
        
        # Log metrics
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1_score", f1)
        
        # Log dataset manifest
        manifest = get_dataset_manifest(dataset_id)
        mlflow.log_dict(manifest, "dataset_manifest.json")
        
        # Log model to MLflow
        print_info("Logging model to MLflow...")
        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name=None,  # We'll register separately for better control
        )
        
        run_id = run.info.run_id
        model_uri = f"runs:/{run_id}/model"
        
        print_success(f"Model logged. Run ID: {run_id}")
    
    # Register model with lineage tags
    print_info("Registering model in MLflow Model Registry...")
    version_number = register_model(
        model_uri=model_uri,
        model_name=model_name,
        dataset_id=dataset_id,
        dataset_version=dataset_version,
        code_commit=code_commit,
        run_id=run_id,
        experiment_name=experiment_name,
        additional_tags={
            "framework": "sklearn",
            "model_type": "LogisticRegression",
        },
    )
    
    print_success(
        f"✓ Model '{model_name}' version {version_number} registered with lineage:\n"
        f"  - dataset_id: {dataset_id}\n"
        f"  - dataset_version: {dataset_version}\n"
        f"  - code_commit: {code_commit}\n"
        f"  - run_id: {run_id}"
    )
    
    return version_number
