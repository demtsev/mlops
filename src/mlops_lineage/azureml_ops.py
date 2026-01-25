"""
Azure ML operations module

Provides functions for Azure ML operations including:
- Fetching MLflow tracking URI from Azure ML workspace
- Storing tracking URI in .env file

Author: MLOps Team
Date: January 2026
"""

from pathlib import Path
from .shell import run_command, print_success, print_info
from .config import config


def get_mlflow_tracking_uri() -> str:
    """
    Fetch MLflow tracking URI from Azure ML workspace using Azure CLI.
    
    Returns:
        MLflow tracking URI (e.g., azureml://...)
        
    Raises:
        RuntimeError: If Azure CLI command fails or workspace not found
    """
    print_info("Fetching MLflow tracking URI from Azure ML workspace...")
    
    # Validate Azure settings
    config.validate_azure_settings()
    
    # Run Azure CLI command to get tracking URI
    cmd = [
        "az", "ml", "workspace", "show",
        "--resource-group", config.AZURE_RESOURCE_GROUP,
        "--name", config.AZURE_ML_WORKSPACE,
        "--query", "mlflow_tracking_uri",
        "-o", "tsv",
    ]
    
    _, stdout, _ = run_command(cmd, capture_output=True)
    tracking_uri = stdout.strip()
    
    if not tracking_uri:
        raise RuntimeError(
            f"Failed to get MLflow tracking URI from workspace '{config.AZURE_ML_WORKSPACE}'. "
            f"Please verify the workspace exists and you have access."
        )
    
    print_success(f"MLflow tracking URI: {tracking_uri}")
    return tracking_uri


def save_tracking_uri_to_env(tracking_uri: str) -> None:
    """
    Save MLflow tracking URI to .env file.
    
    Args:
        tracking_uri: MLflow tracking URI to save
        
    Raises:
        RuntimeError: If .env file operations fail
    """
    env_file = config.REPO_ROOT / ".env"
    
    if not env_file.exists():
        raise RuntimeError(
            f".env file not found at {env_file}. "
            f"Please copy .env.example to .env first."
        )
    
    # Read current .env content
    with open(env_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Update or add MLFLOW_TRACKING_URI
    updated = False
    new_lines = []
    
    for line in lines:
        if line.startswith("MLFLOW_TRACKING_URI=") or line.startswith("# MLFLOW_TRACKING_URI="):
            new_lines.append(f"MLFLOW_TRACKING_URI={tracking_uri}\n")
            updated = True
        else:
            new_lines.append(line)
    
    if not updated:
        # Add to end of file
        new_lines.append(f"\nMLFLOW_TRACKING_URI={tracking_uri}\n")
    
    # Write updated content
    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    
    print_success(f"Saved MLflow tracking URI to {env_file}")


def set_mlflow_tracking_uri() -> str:
    """
    Fetch MLflow tracking URI from Azure ML and save to .env file.
    
    Returns:
        MLflow tracking URI
        
    Raises:
        RuntimeError: If operation fails
    """
    tracking_uri = get_mlflow_tracking_uri()
    save_tracking_uri_to_env(tracking_uri)
    
    print_info("Please reload your .env file or restart your application to use the new tracking URI.")
    return tracking_uri


def check_azure_cli_ml_extension() -> bool:
    """
    Check if Azure CLI ML extension is installed.
    
    Returns:
        True if extension is installed, False otherwise
    """
    try:
        _, stdout, _ = run_command(
            ["az", "extension", "list", "-o", "json"],
            capture_output=True,
        )
        return "ml" in stdout.lower()
    except Exception:
        return False


def install_azure_cli_ml_extension() -> None:
    """
    Install Azure CLI ML extension.
    
    Raises:
        RuntimeError: If installation fails
    """
    print_info("Installing Azure CLI ML extension...")
    run_command(["az", "extension", "add", "-n", "ml"])
    print_success("Azure CLI ML extension installed")
