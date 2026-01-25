"""
DVC operations module

Provides functions for DVC operations including:
- Initializing DVC and Azure remote
- Adding and pushing datasets
- Pulling datasets from Azure Blob Storage

Author: MLOps Team
Date: January 2026
"""

from pathlib import Path
from typing import Optional
from .shell import run_command, print_success, print_info, print_warning
from .config import config


def init_dvc() -> None:
    """
    Initialize DVC in the repository if not already initialized.
    
    Raises:
        RuntimeError: If DVC initialization fails
    """
    dvc_dir = config.REPO_ROOT / ".dvc"
    
    if dvc_dir.exists():
        print_info("DVC already initialized")
        return
    
    print_info("Initializing DVC...")
    run_command(["dvc", "init"], cwd=str(config.REPO_ROOT))
    print_success("DVC initialized")


def configure_azure_remote() -> None:
    """
    Configure Azure Blob Storage as DVC remote.
    
    This sets up the default DVC remote to use Azure Blob Storage.
    If AZURE_STORAGE_CONNECTION_STRING is set in .env, it will be
    configured as a local secret (not committed to git).
    
    Raises:
        RuntimeError: If remote configuration fails
    """
    init_dvc()
    
    # Build Azure Blob URL
    container = config.DVC_AZURE_CONTAINER
    path = config.DVC_AZURE_PATH
    remote_url = f"azure://{container}/{path}"
    
    print_info(f"Configuring DVC remote: {remote_url}")
    
    # Check if remote already exists
    _, stdout, _ = run_command(
        ["dvc", "remote", "list"],
        cwd=str(config.REPO_ROOT),
        capture_output=True,
    )
    
    if "azure_storage" in stdout:
        print_warning("Remote 'azure_storage' already exists, updating URL...")
        run_command(
            ["dvc", "remote", "modify", "azure_storage", "url", remote_url],
            cwd=str(config.REPO_ROOT),
        )
    else:
        # Add remote
        run_command(
            ["dvc", "remote", "add", "-d", "azure_storage", remote_url],
            cwd=str(config.REPO_ROOT),
        )
    
    # Configure connection string if provided (stored locally, not committed)
    conn_str = config.AZURE_STORAGE_CONNECTION_STRING
    if conn_str:
        print_info("Configuring connection string (local, not committed)...")
        run_command(
            ["dvc", "remote", "modify", "--local", "azure_storage", "connection_string", conn_str],
            cwd=str(config.REPO_ROOT),
        )
        print_success("DVC remote configured with connection string")
    else:
        print_info("No connection string provided, will use 'az login' credentials")
        print_success("DVC remote configured")
    
    print_info("To verify remote: dvc remote list")


def add_dataset(dataset_id: str) -> Path:
    """
    Add a dataset to DVC tracking.
    
    This creates/updates the .dvc file for the dataset directory.
    
    Args:
        dataset_id: Dataset identifier (e.g., "kidney_textures")
        
    Returns:
        Path to the .dvc file
        
    Raises:
        RuntimeError: If dataset directory doesn't exist or DVC add fails
    """
    dataset_path = config.REPO_ROOT / "datasets" / dataset_id
    
    if not dataset_path.exists():
        raise RuntimeError(
            f"Dataset directory not found: {dataset_path}\n"
            f"Please create it and add your data files first."
        )
    
    if not any(dataset_path.iterdir()):
        raise RuntimeError(
            f"Dataset directory is empty: {dataset_path}\n"
            f"Please add your data files first."
        )
    
    print_info(f"Adding dataset '{dataset_id}' to DVC tracking...")
    run_command(
        ["dvc", "add", str(dataset_path)],
        cwd=str(config.REPO_ROOT),
    )
    
    dvc_file = config.REPO_ROOT / "datasets" / f"{dataset_id}.dvc"
    print_success(f"Dataset tracked by DVC: {dvc_file}")
    
    return dvc_file


def push_dataset(dataset_id: Optional[str] = None) -> None:
    """
    Push dataset(s) to Azure Blob Storage.
    
    Args:
        dataset_id: Optional dataset identifier. If None, pushes all datasets.
        
    Raises:
        RuntimeError: If DVC push fails
    """
    if dataset_id:
        dvc_file = config.REPO_ROOT / "datasets" / f"{dataset_id}.dvc"
        if not dvc_file.exists():
            raise RuntimeError(
                f"Dataset '{dataset_id}' not tracked by DVC. "
                f"Run 'dataset push' first to add it."
            )
        print_info(f"Pushing dataset '{dataset_id}' to Azure Blob Storage...")
        run_command(
            ["dvc", "push", str(dvc_file)],
            cwd=str(config.REPO_ROOT),
        )
    else:
        print_info("Pushing all datasets to Azure Blob Storage...")
        run_command(
            ["dvc", "push"],
            cwd=str(config.REPO_ROOT),
        )
    
    print_success("Dataset(s) pushed to Azure Blob Storage")


def pull_dataset(dataset_id: Optional[str] = None, worktree_path: Optional[Path] = None) -> None:
    """
    Pull dataset(s) from Azure Blob Storage.
    
    Args:
        dataset_id: Optional dataset identifier. If None, pulls all datasets.
        worktree_path: Optional path to worktree (for reproducible pulls)
        
    Raises:
        RuntimeError: If DVC pull fails
    """
    # Determine working directory
    work_dir = str(worktree_path) if worktree_path else str(config.REPO_ROOT)
    
    if dataset_id:
        dvc_file = f"datasets/{dataset_id}.dvc"
        print_info(f"Pulling dataset '{dataset_id}' from Azure Blob Storage...")
        run_command(
            ["dvc", "pull", dvc_file],
            cwd=work_dir,
        )
    else:
        print_info("Pulling all datasets from Azure Blob Storage...")
        run_command(
            ["dvc", "pull"],
            cwd=work_dir,
        )
    
    print_success("Dataset(s) pulled from Azure Blob Storage")


def get_dataset_path(dataset_id: str, worktree_path: Optional[Path] = None) -> Path:
    """
    Get the path to a dataset directory.
    
    Args:
        dataset_id: Dataset identifier
        worktree_path: Optional path to worktree
        
    Returns:
        Path to dataset directory
    """
    base_path = worktree_path if worktree_path else config.REPO_ROOT
    return base_path / "datasets" / dataset_id
