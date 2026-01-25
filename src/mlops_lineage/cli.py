"""
Command-line interface for MLOps Lineage toolkit

Provides commands for:
- Azure ML: set-tracking-uri
- DVC: init-remote
- Dataset: push, add
- Model: train, info, list, pull-data

Author: MLOps Team
Date: January 2026
"""

import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table

from .config import config
from .shell import print_success, print_info, print_error
from . import azureml_ops, dvc_ops, git_ops, mlflow_ops, training_demo

console = Console()


def cmd_azureml_set_tracking_uri(args) -> int:
    """Command: azureml set-tracking-uri"""
    try:
        azureml_ops.set_mlflow_tracking_uri()
        return 0
    except Exception as e:
        print_error(f"Failed to set MLflow tracking URI: {e}")
        return 1


def cmd_dvc_init_remote(args) -> int:
    """Command: dvc init-remote"""
    try:
        dvc_ops.configure_azure_remote()
        print_info("\nNext steps:")
        print_info("  1. Verify remote: dvc remote list")
        print_info("  2. Test connection: dvc push (after adding a dataset)")
        return 0
    except Exception as e:
        print_error(f"Failed to initialize DVC remote: {e}")
        return 1


def cmd_dataset_push(args) -> int:
    """Command: dataset push"""
    try:
        dataset_id = args.dataset_id
        message = args.message
        
        # Add dataset to DVC
        dvc_file = dvc_ops.add_dataset(dataset_id)
        
        # Push to Azure
        dvc_ops.push_dataset(dataset_id)
        
        # Commit to Git
        print_info("Committing DVC metadata to Git...")
        commit_hash = git_ops.commit_changes(
            message=message or f"Add dataset: {dataset_id}",
            files=[str(dvc_file.relative_to(config.REPO_ROOT))],
        )
        
        dataset_version = f"git:{commit_hash}"
        print_success(
            f"✓ Dataset '{dataset_id}' pushed successfully!\n"
            f"  - Dataset version: {dataset_version}\n"
            f"  - DVC file: {dvc_file.name}\n"
            f"  - Git commit: {commit_hash}"
        )
        return 0
    except Exception as e:
        print_error(f"Failed to push dataset: {e}")
        return 1


def cmd_dataset_add(args) -> int:
    """Command: dataset add (append to existing dataset)"""
    try:
        dataset_id = args.dataset_id
        message = args.message
        
        print_info(f"Updating dataset '{dataset_id}'...")
        
        # Re-add dataset to DVC (updates .dvc file)
        dvc_file = dvc_ops.add_dataset(dataset_id)
        
        # Push updated dataset to Azure
        dvc_ops.push_dataset(dataset_id)
        
        # Commit updated .dvc file to Git
        print_info("Committing updated DVC metadata to Git...")
        commit_hash = git_ops.commit_changes(
            message=message or f"Update dataset: {dataset_id}",
            files=[str(dvc_file.relative_to(config.REPO_ROOT))],
        )
        
        dataset_version = f"git:{commit_hash}"
        print_success(
            f"✓ Dataset '{dataset_id}' updated successfully!\n"
            f"  - New dataset version: {dataset_version}\n"
            f"  - Git commit: {commit_hash}"
        )
        return 0
    except Exception as e:
        print_error(f"Failed to add to dataset: {e}")
        return 1


def cmd_model_train(args) -> int:
    """Command: model train"""
    try:
        model_name = args.model_name
        dataset_id = args.dataset_id
        experiment_name = args.experiment or "default_experiment"
        
        # Train and register model
        version_number = training_demo.train_demo_model(
            model_name=model_name,
            dataset_id=dataset_id,
            experiment_name=experiment_name,
        )
        
        print_success(
            f"\n✓ Training complete! Model '{model_name}' version {version_number} is ready.\n"
            f"\nTo retrieve the exact dataset used:\n"
            f"  python -m mlops_lineage model pull-data --model-name {model_name} --model-version {version_number}"
        )
        return 0
    except Exception as e:
        print_error(f"Failed to train model: {e}")
        return 1


def cmd_model_info(args) -> int:
    """Command: model info"""
    try:
        model_name = args.model_name
        model_version = args.model_version
        
        # Get model version info
        info = mlflow_ops.get_model_version_info(model_name, model_version)
        
        # Display as table
        table = Table(title=f"Model: {model_name} (version {model_version})")
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        for key, value in info.items():
            table.add_row(key, str(value))
        
        console.print(table)
        return 0
    except Exception as e:
        print_error(f"Failed to get model info: {e}")
        return 1


def cmd_model_list(args) -> int:
    """Command: model list"""
    try:
        model_name = args.model_name
        max_results = args.max_results
        
        # List model versions
        versions = mlflow_ops.list_model_versions(model_name, max_results)
        
        if not versions:
            print_info(f"No versions found for model '{model_name}'")
            return 0
        
        # Display as table
        table = Table(title=f"Model Versions: {model_name}")
        table.add_column("Version", style="cyan", justify="right")
        table.add_column("Status", style="green")
        table.add_column("Dataset ID", style="yellow")
        table.add_column("Dataset Version", style="yellow")
        table.add_column("Code Commit", style="magenta")
        
        for version in versions:
            table.add_row(
                version["version"],
                version["status"],
                version.get("dataset_id", "N/A"),
                version.get("dataset_version", "N/A"),
                version.get("code_commit", "N/A"),
            )
        
        console.print(table)
        return 0
    except Exception as e:
        print_error(f"Failed to list model versions: {e}")
        return 1


def cmd_model_pull_data(args) -> int:
    """Command: model pull-data"""
    try:
        model_name = args.model_name
        model_version = args.model_version
        
        print_info(f"Retrieving dataset for model '{model_name}' version {model_version}...")
        
        # Get lineage information
        lineage = mlflow_ops.get_model_lineage(model_name, model_version)
        dataset_id = lineage["dataset_id"]
        dataset_version = lineage["dataset_version"]
        code_commit = lineage["code_commit"]
        
        print_info(f"Model lineage:")
        print_info(f"  - Dataset ID: {dataset_id}")
        print_info(f"  - Dataset version: {dataset_version}")
        print_info(f"  - Code commit: {code_commit}")
        
        # Create worktree for dataset version
        print_info(f"\nCreating Git worktree for {dataset_version}...")
        worktree_path = git_ops.create_worktree(dataset_version)
        
        # Pull dataset in worktree
        print_info(f"Pulling dataset '{dataset_id}' from Azure Blob Storage...")
        dvc_ops.pull_dataset(dataset_id, worktree_path)
        
        # Get dataset path
        dataset_path = dvc_ops.get_dataset_path(dataset_id, worktree_path)
        
        print_success(
            f"\n✓ Dataset retrieved successfully!\n"
            f"\nDataset location:\n"
            f"  {dataset_path}\n"
            f"\nThis is the EXACT dataset used to train model '{model_name}' version {model_version}.\n"
            f"\nWorktree location:\n"
            f"  {worktree_path}\n"
            f"\nNote: This worktree is independent of your current branch."
        )
        return 0
    except Exception as e:
        print_error(f"Failed to pull dataset for model: {e}")
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        prog="mlops_lineage",
        description="MLOps toolkit for dataset and model versioning with Git, DVC, and MLflow",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Azure ML commands
    azureml_parser = subparsers.add_parser("azureml", help="Azure ML operations")
    azureml_subparsers = azureml_parser.add_subparsers(dest="azureml_command")
    
    azureml_subparsers.add_parser(
        "set-tracking-uri",
        help="Fetch and save MLflow tracking URI from Azure ML workspace"
    )
    
    # DVC commands
    dvc_parser = subparsers.add_parser("dvc", help="DVC operations")
    dvc_subparsers = dvc_parser.add_subparsers(dest="dvc_command")
    
    dvc_subparsers.add_parser(
        "init-remote",
        help="Initialize DVC Azure Blob remote"
    )
    
    # Dataset commands
    dataset_parser = subparsers.add_parser("dataset", help="Dataset operations")
    dataset_subparsers = dataset_parser.add_subparsers(dest="dataset_command")
    
    push_parser = dataset_subparsers.add_parser(
        "push",
        help="Add new dataset and push to Azure Blob"
    )
    push_parser.add_argument("--dataset-id", required=True, help="Dataset identifier")
    push_parser.add_argument("--message", help="Commit message")
    
    add_parser = dataset_subparsers.add_parser(
        "add",
        help="Update existing dataset and push to Azure Blob"
    )
    add_parser.add_argument("--dataset-id", required=True, help="Dataset identifier")
    add_parser.add_argument("--message", help="Commit message")
    
    # Model commands
    model_parser = subparsers.add_parser("model", help="Model operations")
    model_subparsers = model_parser.add_subparsers(dest="model_command")
    
    train_parser = model_subparsers.add_parser(
        "train",
        help="Train and register model with lineage"
    )
    train_parser.add_argument("--model-name", required=True, help="Model name")
    train_parser.add_argument("--dataset-id", required=True, help="Dataset identifier")
    train_parser.add_argument("--experiment", help="MLflow experiment name")
    
    info_parser = model_subparsers.add_parser(
        "info",
        help="Show model version information"
    )
    info_parser.add_argument("--model-name", required=True, help="Model name")
    info_parser.add_argument("--model-version", type=int, required=True, help="Model version number")
    
    list_parser = model_subparsers.add_parser(
        "list",
        help="List model versions"
    )
    list_parser.add_argument("--model-name", required=True, help="Model name")
    list_parser.add_argument("--max-results", type=int, default=10, help="Maximum number of versions to show")
    
    pull_data_parser = model_subparsers.add_parser(
        "pull-data",
        help="Pull exact dataset used by a model version"
    )
    pull_data_parser.add_argument("--model-name", required=True, help="Model name")
    pull_data_parser.add_argument("--model-version", type=int, required=True, help="Model version number")
    
    return parser


def main() -> int:
    """Main entry point for CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Route to appropriate command handler
    try:
        if args.command == "azureml":
            if args.azureml_command == "set-tracking-uri":
                return cmd_azureml_set_tracking_uri(args)
        
        elif args.command == "dvc":
            if args.dvc_command == "init-remote":
                return cmd_dvc_init_remote(args)
        
        elif args.command == "dataset":
            if args.dataset_command == "push":
                return cmd_dataset_push(args)
            elif args.dataset_command == "add":
                return cmd_dataset_add(args)
        
        elif args.command == "model":
            if args.model_command == "train":
                return cmd_model_train(args)
            elif args.model_command == "info":
                return cmd_model_info(args)
            elif args.model_command == "list":
                return cmd_model_list(args)
            elif args.model_command == "pull-data":
                return cmd_model_pull_data(args)
        
        # If we get here, no valid command was provided
        parser.print_help()
        return 1
    
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user")
        return 130
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
