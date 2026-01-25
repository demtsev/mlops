# MLOps Lineage: Production-Quality Dataset & Model Versioning

A complete MLOps toolkit for versioning datasets and models with strong lineage tracking:

- **Git** for code and metadata versioning
- **DVC** for dataset versioning on Azure Blob Storage (no data duplication)
- **MLflow** for experiment tracking and Model Registry on Azure ML
- **Strong Lineage**: Every model version knows exactly which dataset version it used

## 🎯 Key Features

✅ **Dataset Versioning**: Version datasets in Azure Blob without duplicating unchanged files  
✅ **Model Lineage**: Each model version stores `dataset_id` + `dataset_version` + `code_commit`  
✅ **Reproducibility**: Pull the exact dataset used by any model version using Git worktrees  
✅ **Azure Integration**: Seamless integration with Azure Blob Storage and Azure ML  
✅ **Windows-Friendly**: Fully tested on Windows with Miniconda on custom drive (E:\)  
✅ **Production-Ready**: Well-structured code, type hints, comprehensive error handling

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Azure Configuration](#azure-configuration)
4. [Environment Setup](#environment-setup)
5. [One-Time Setup](#one-time-setup)
6. [Daily Workflow](#daily-workflow)
7. [CLI Reference](#cli-reference)
8. [PowerShell Scripts](#powershell-scripts)
9. [Project Structure](#project-structure)
10. [Troubleshooting](#troubleshooting)
11. [Advanced Usage](#advanced-usage)

---

## 📌 Prerequisites

### Required Software

1. **Git for Windows**
   - Download: https://git-scm.com/download/win
   - Verify: `git --version`

2. **Azure CLI**
   - Download: https://aka.ms/installazurecliwindows
   - Verify: `az --version`
   - Install ML extension: `az extension add -n ml`

3. **Miniconda** (on E:\ drive)
   - Download: https://docs.conda.io/en/latest/miniconda.html
   - Install to: `E:\Miniconda3`
   - Configure (see [Environment Setup](#environment-setup))

### Azure Resources

You need:
- **Azure Subscription** with appropriate permissions
- **Azure ML Workspace** (for MLflow tracking)
- **Azure Blob Storage Container** (for DVC data storage)

---

## 🔧 Installation

### Step 1: Install Miniconda on E:\ Drive

```powershell
# Download Miniconda installer for Windows
# https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe

# Run installer and choose installation path: E:\Miniconda3

# After installation, create .condarc file
notepad E:\Miniconda3\.condarc
```

Add this content to `.condarc`:

```yaml
envs_dirs:
  - E:\conda_envs
pkgs_dirs:
  - E:\conda_pkgs
```

**Restart your terminal/IDE** after installation.

### Step 2: Clone Repository

```powershell
cd G:\projectsCheck\mlops\pipeline2026
git clone <your-repo-url> mlops_dvc_azure_1
cd mlops_dvc_azure_1
```

### Step 3: Create Conda Environment

```powershell
# Create environment from environment.yml
conda env create -f environment.yml

# Activate environment
conda activate mlops-lineage

# Verify installation
python --version        # Should be 3.11.x
dvc --version          # Should be 3.48.x
mlflow --version       # Should be 2.10.x
az --version           # Should show Azure CLI
```

### Step 4: (Optional) Install as Editable Package

```powershell
# Install in editable mode (recommended for development)
pip install -e .
```

---

## ☁️ Azure Configuration

### Step 1: Login to Azure

```powershell
# Login to Azure
az login

# Set default subscription (if you have multiple)
az account set --subscription <your-subscription-id>

# Verify
az account show
```

### Step 2: Verify Azure Resources

```powershell
# Verify ML workspace exists
az ml workspace show --resource-group <your-rg> --name <your-workspace>

# Verify storage account exists (for DVC)
az storage account show --name <your-storage-account> --resource-group <your-rg>

# Verify blob container exists
az storage container show --name dvc-storage --account-name <your-storage-account>
```

If resources don't exist, create them:

```powershell
# Create storage account (if needed)
az storage account create `
    --name <storage-account-name> `
    --resource-group <your-rg> `
    --location <region> `
    --sku Standard_LRS

# Create blob container (if needed)
az storage container create `
    --name dvc-storage `
    --account-name <storage-account-name>
```

---

## 🌍 Environment Setup

### Step 1: Configure .env File

```powershell
# Copy example .env file
copy .env.example .env

# Edit .env file
notepad .env
```

Fill in your Azure details:

```env
# Azure Subscription and Resource Group
AZURE_SUBSCRIPTION_ID=12345678-1234-1234-1234-123456789abc
AZURE_RESOURCE_GROUP=my-mlops-rg
AZURE_ML_WORKSPACE=my-aml-workspace

# DVC Remote Configuration
DVC_AZURE_CONTAINER=dvc-storage
DVC_AZURE_PATH=datasets

# Optional: Azure Storage Connection String (for DVC auth)
# If not set, will use `az login` credentials
# AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...

# MLflow Tracking URI (auto-populated by CLI command - leave commented)
# MLFLOW_TRACKING_URI=azureml://...
```

### Step 2: Set MLflow Tracking URI

```powershell
# This command fetches the tracking URI from Azure ML and saves it to .env
python -m mlops_lineage azureml set-tracking-uri

# Or use the PowerShell script
.\scripts\set_mlflow_tracking_uri.ps1
```

**Important**: Restart your terminal/IDE or reload .env after this step.

---

## 🚀 One-Time Setup

### Step 1: Initialize Git Repository

```powershell
# Initialize Git (if not already done)
git init

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: MLOps lineage repository"
```

### Step 2: Initialize DVC and Azure Remote

```powershell
# Initialize DVC and configure Azure Blob remote
python -m mlops_lineage dvc init-remote

# Or use the PowerShell script
.\scripts\init_dvc_remote.ps1

# Verify remote configuration
dvc remote list
# Output: azure_storage  azure://dvc-storage/datasets
```

### Step 3: Commit DVC Configuration

```powershell
# Commit DVC configuration files
git add .dvc/config
git commit -m "Configure DVC Azure remote"
```

**✅ Setup Complete!** You're now ready to version datasets and models.

---

## 📊 Daily Workflow

### Workflow 1: Add a New Dataset

```powershell
# 1. Create dataset directory
mkdir datasets\kidney_textures
mkdir datasets\kidney_textures\train
mkdir datasets\kidney_textures\test

# 2. Add your data files
# Copy your images, CSVs, etc. to the dataset directory

# 3. Push dataset to DVC and Azure
python -m mlops_lineage dataset push `
    --dataset-id kidney_textures `
    --message "Add kidney textures dataset v1"

# Or use the PowerShell script
.\scripts\push_new_dataset.ps1 `
    -DatasetId "kidney_textures" `
    -Message "Add kidney textures dataset v1"
```

**What happens:**
1. DVC adds dataset to tracking (creates `.dvc` file)
2. DVC pushes data to Azure Blob Storage
3. Git commits the `.dvc` metadata file
4. Git commit hash becomes the dataset version: `git:<commit>`

### Workflow 2: Append to Existing Dataset

```powershell
# 1. Add more files to existing dataset
# Copy new images to datasets\kidney_textures\train\

# 2. Update dataset
python -m mlops_lineage dataset add `
    --dataset-id kidney_textures `
    --message "Add 100 more training images"

# Or use the PowerShell script
.\scripts\append_to_dataset.ps1 `
    -DatasetId "kidney_textures" `
    -Message "Add 100 more training images"
```

**What happens:**
1. DVC re-scans the dataset directory
2. DVC uploads only NEW/CHANGED files to Azure (efficient!)
3. DVC updates the `.dvc` metadata file
4. Git commits the updated `.dvc` file
5. New git commit hash = new dataset version

### Workflow 3: Train and Register Model

```powershell
# Train a model using a dataset
python -m mlops_lineage model train `
    --model-name kidney_classifier `
    --dataset-id kidney_textures `
    --experiment medical_imaging

# Or use the PowerShell script
.\scripts\train_register_model.ps1 `
    -ModelName "kidney_classifier" `
    -DatasetId "kidney_textures" `
    -Experiment "medical_imaging"
```

**What happens:**
1. Model trains using data from `datasets/kidney_textures/`
2. Model is logged to MLflow
3. Model is registered in MLflow Model Registry
4. Lineage tags are attached:
   - `dataset_id`: kidney_textures
   - `dataset_version`: git:abc1234
   - `code_commit`: abc1234
   - `train_run_id`: <mlflow-run-id>

### Workflow 4: Retrieve Exact Dataset for a Model

```powershell
# Pull the exact dataset used by model version 1
python -m mlops_lineage model pull-data `
    --model-name kidney_classifier `
    --model-version 1

# Or use the PowerShell script
.\scripts\pull_data_for_model.ps1 `
    -ModelName "kidney_classifier" `
    -ModelVersion 1
```

**What happens:**
1. Reads model tags to get `dataset_version` (e.g., `git:abc1234`)
2. Creates a Git worktree at `.worktrees/abc1234/`
3. Runs `dvc pull` in the worktree
4. Prints path to dataset: `.worktrees/abc1234/datasets/kidney_textures/`

**Key Point**: Your current working branch is NOT affected!

---

## 🛠️ CLI Reference

### Azure ML Commands

```powershell
# Fetch and save MLflow tracking URI
python -m mlops_lineage azureml set-tracking-uri
```

### DVC Commands

```powershell
# Initialize DVC Azure Blob remote
python -m mlops_lineage dvc init-remote
```

### Dataset Commands

```powershell
# Push new dataset
python -m mlops_lineage dataset push --dataset-id <id> [--message "<msg>"]

# Update existing dataset
python -m mlops_lineage dataset add --dataset-id <id> [--message "<msg>"]
```

### Model Commands

```powershell
# Train and register model
python -m mlops_lineage model train `
    --model-name <name> `
    --dataset-id <id> `
    [--experiment <exp-name>]

# Show model version info
python -m mlops_lineage model info `
    --model-name <name> `
    --model-version <version>

# List model versions
python -m mlops_lineage model list `
    --model-name <name> `
    [--max-results 10]

# Pull exact dataset for model version
python -m mlops_lineage model pull-data `
    --model-name <name> `
    --model-version <version>
```

---

## 📜 PowerShell Scripts

All scripts are in the `scripts/` directory and provide user-friendly wrappers around CLI commands.

### init_dvc_remote.ps1

```powershell
.\scripts\init_dvc_remote.ps1
```

Initializes DVC and configures Azure Blob remote.

### set_mlflow_tracking_uri.ps1

```powershell
.\scripts\set_mlflow_tracking_uri.ps1
```

Fetches MLflow tracking URI from Azure ML and saves to `.env`.

### push_new_dataset.ps1

```powershell
.\scripts\push_new_dataset.ps1 -DatasetId "my_dataset" [-Message "Commit message"]
```

Adds a new dataset to DVC and pushes to Azure.

### append_to_dataset.ps1

```powershell
.\scripts\append_to_dataset.ps1 -DatasetId "my_dataset" [-Message "Commit message"]
```

Updates an existing dataset and pushes changes.

### train_register_model.ps1

```powershell
.\scripts\train_register_model.ps1 `
    -ModelName "my_model" `
    -DatasetId "my_dataset" `
    [-Experiment "my_experiment"]
```

Trains and registers a model with lineage.

### pull_data_for_model.ps1

```powershell
.\scripts\pull_data_for_model.ps1 `
    -ModelName "my_model" `
    -ModelVersion 1
```

Pulls the exact dataset used by a model version.

---

## 📁 Project Structure

```
mlops_dvc_azure_1/
├── README.md                      # This file
├── .env                           # Environment variables (not committed)
├── .env.example                   # Template for .env
├── .gitignore                     # Git ignore rules
├── environment.yml                # Conda environment specification
├── pyproject.toml                 # Python project metadata
├── dvc.yaml                       # DVC pipeline configuration (optional)
├── dvc.lock                       # DVC lock file (auto-generated)
│
├── .dvc/                          # DVC internal files
│   ├── config                     # DVC configuration (remote settings)
│   └── ...
│
├── datasets/                      # Dataset storage (DVC-tracked)
│   ├── .gitkeep                   # Keeps directory in Git
│   ├── README.md                  # Dataset documentation
│   ├── kidney_textures/           # Example dataset
│   │   ├── train/
│   │   └── test/
│   └── kidney_textures.dvc        # DVC metadata (committed to Git)
│
├── src/
│   └── mlops_lineage/             # Main Python package
│       ├── __init__.py            # Package initialization
│       ├── __main__.py            # Entry point for python -m mlops_lineage
│       ├── cli.py                 # Command-line interface
│       ├── config.py              # Configuration and .env loading
│       ├── shell.py               # Subprocess helpers
│       ├── git_ops.py             # Git operations
│       ├── dvc_ops.py             # DVC operations
│       ├── azureml_ops.py         # Azure ML operations
│       ├── mlflow_ops.py          # MLflow operations
│       └── training_demo.py       # Demo training script
│
├── scripts/                       # PowerShell helper scripts
│   ├── init_dvc_remote.ps1
│   ├── set_mlflow_tracking_uri.ps1
│   ├── push_new_dataset.ps1
│   ├── append_to_dataset.ps1
│   ├── train_register_model.ps1
│   └── pull_data_for_model.ps1
│
└── .worktrees/                    # Git worktrees (not committed)
    └── abc1234/                   # Worktree for commit abc1234
        └── datasets/              # Exact dataset at that commit
```

---

## 🔍 Troubleshooting

### Issue: Azure CLI not found

**Error**: `az: The term 'az' is not recognized...`

**Solution**:
1. Download and install Azure CLI: https://aka.ms/installazurecliwindows
2. **Restart your terminal/IDE**
3. Verify: `az --version`

### Issue: Azure CLI ML extension not installed

**Error**: `az ml: 'ml' is not in the 'az' command group...`

**Solution**:
```powershell
az extension add -n ml
az extension list  # Verify ml extension is installed
```

### Issue: MLflow tracking URI not set

**Error**: `MLFLOW_TRACKING_URI not set in .env file`

**Solution**:
```powershell
# Run the setup command
python -m mlops_lineage azureml set-tracking-uri

# Restart your terminal/IDE or reload .env
```

### Issue: Conda environment not activated

**Error**: Messages about DVC or Python not found

**Solution**:
```powershell
# Activate the environment
conda activate mlops-lineage

# Verify
conda env list  # Should show * next to mlops-lineage
```

### Issue: PATH issues on Windows

**Problem**: Commands not found after installation

**Solution**:
1. Close and reopen your terminal/IDE
2. Verify PATH includes:
   - `E:\Miniconda3\Scripts`
   - `E:\Miniconda3\Library\bin`
   - Azure CLI installation path
   - Git installation path

### Issue: DVC push fails with authentication error

**Error**: `ERROR: failed to push data to the remote`

**Solution**:
1. Verify you're logged in to Azure: `az login`
2. Verify storage account access: `az storage account show --name <account>`
3. Optionally, set connection string in .env:
   ```env
   AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net
   ```
4. Re-run: `python -m mlops_lineage dvc init-remote`

### Issue: Git worktree already exists

**Error**: `fatal: '.worktrees/abc1234' already exists`

**Solution**:
```powershell
# Remove the worktree
git worktree remove .worktrees/abc1234

# Or manually delete
rm -r .worktrees/abc1234
git worktree prune
```

### Issue: Dataset directory is empty

**Error**: `Dataset directory is empty: datasets/my_dataset`

**Solution**:
```powershell
# Add your data files first
mkdir datasets/my_dataset/train
# Copy your files to datasets/my_dataset/train/

# Then push
python -m mlops_lineage dataset push --dataset-id my_dataset
```

---

## 🚀 Advanced Usage

### Custom Training Script

Replace the demo training with your actual training logic:

```python
# my_training.py
from mlops_lineage.config import config
from mlops_lineage.git_ops import get_current_commit
from mlops_lineage.mlflow_ops import configure_mlflow, register_model
import mlflow

def train_my_model(dataset_id: str, model_name: str):
    configure_mlflow()
    
    # Get dataset path
    dataset_path = config.REPO_ROOT / "datasets" / dataset_id
    
    # Train your model
    # ... your training code ...
    
    # Log model to MLflow
    with mlflow.start_run() as run:
        # ... log params, metrics, model ...
        mlflow.log_param("dataset_id", dataset_id)
        
        run_id = run.info.run_id
        model_uri = f"runs:/{run_id}/model"
    
    # Register with lineage
    code_commit = get_current_commit()
    dataset_version = f"git:{code_commit}"
    
    version = register_model(
        model_uri=model_uri,
        model_name=model_name,
        dataset_id=dataset_id,
        dataset_version=dataset_version,
        code_commit=code_commit,
        run_id=run_id,
    )
    
    return version
```

### Using Connection String for DVC Auth

If `az login` authentication doesn't work for DVC, use a connection string:

```powershell
# Get connection string from Azure Portal or CLI
$connStr = az storage account show-connection-string `
    --name <storage-account> `
    --resource-group <rg> `
    --query connectionString -o tsv

# Add to .env
Add-Content .env "AZURE_STORAGE_CONNECTION_STRING=$connStr"

# Re-configure DVC remote
python -m mlops_lineage dvc init-remote
```

### Multiple Datasets

You can track multiple datasets independently:

```powershell
# Dataset 1: Kidney textures
.\scripts\push_new_dataset.ps1 -DatasetId "kidney_textures"

# Dataset 2: Gallbladder textures
.\scripts\push_new_dataset.ps1 -DatasetId "gallbladder_textures"

# Dataset 3: Surgical videos
.\scripts\push_new_dataset.ps1 -DatasetId "surgical_videos"

# Train model on specific dataset
.\scripts\train_register_model.ps1 `
    -ModelName "kidney_classifier" `
    -DatasetId "kidney_textures"
```

### Branching and Dataset Versions

DVC works seamlessly with Git branches:

```powershell
# Create experiment branch
git checkout -b experiment/new-data-augmentation

# Modify and update dataset
# Add augmented images to datasets/kidney_textures/train/
.\scripts\append_to_dataset.ps1 `
    -DatasetId "kidney_textures" `
    -Message "Add augmented images"

# Train model on this branch
.\scripts\train_register_model.ps1 `
    -ModelName "kidney_classifier_v2" `
    -DatasetId "kidney_textures"

# Model will be tagged with the commit from this branch
# Later, you can pull this exact dataset version using the model version
```

---

## 📚 Additional Resources

- **DVC Documentation**: https://dvc.org/doc
- **MLflow Documentation**: https://mlflow.org/docs/latest/index.html
- **Azure ML Documentation**: https://learn.microsoft.com/en-us/azure/machine-learning/
- **Git Worktrees**: https://git-scm.com/docs/git-worktree

---

## 📝 Quick Start Checklist

Follow these steps in order:

- [ ] **1. Install prerequisites**: Git, Azure CLI, Miniconda on E:\
- [ ] **2. Configure Conda**: Set `envs_dirs` and `pkgs_dirs` in `.condarc`
- [ ] **3. Clone repository** and create conda environment
- [ ] **4. Azure login**: `az login`
- [ ] **5. Configure .env**: Copy `.env.example` to `.env` and fill values
- [ ] **6. Set MLflow URI**: `python -m mlops_lineage azureml set-tracking-uri`
- [ ] **7. Init DVC remote**: `python -m mlops_lineage dvc init-remote`
- [ ] **8. Add dataset**: Create `datasets/<id>/` and run `dataset push`
- [ ] **9. Train model**: Run `model train`
- [ ] **10. Test reproducibility**: Run `model pull-data` to retrieve exact dataset

---

## 🎉 Success!

You now have a production-quality MLOps repository with:

✅ Datasets versioned in Azure Blob (efficient, no duplication)  
✅ Models registered with full lineage to datasets and code  
✅ Complete reproducibility via Git worktrees  
✅ Professional CLI and PowerShell scripts  
✅ Beginner-friendly documentation

**Happy MLOps!** 🚀

---

## 📧 Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [CLI Reference](#cli-reference)
3. Check Azure ML workspace logs in Azure Portal
4. Verify DVC remote connection: `dvc remote list`

---

**Version**: 1.0.0  
**Last Updated**: January 2026  
**Author**: MLOps Team
