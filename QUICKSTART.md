# 🚀 Quick Start Guide

Get up and running with MLOps Lineage in 10 steps!

## Prerequisites

- ✅ Windows PC
- ✅ Git installed
- ✅ Azure CLI installed (`az --version`)
- ✅ Miniconda installed on E:\Miniconda3
- ✅ Azure subscription with ML workspace and Blob storage

---

## Step-by-Step Setup

### 1️⃣ Configure Conda for E:\ Drive

Create/edit `E:\Miniconda3\.condarc`:

```yaml
envs_dirs:
  - E:\conda_envs
pkgs_dirs:
  - E:\conda_pkgs
```

**Restart your terminal** after this change.

### 2️⃣ Create Conda Environment

```powershell
cd g:\projectsCheck\mlops\pipeline2026\mlops_dvc_azure_1
conda env create -f environment.yml
conda activate mlops-lineage
```

### 3️⃣ Login to Azure

```powershell
az login
az account set --subscription <your-subscription-id>
```

### 4️⃣ Configure Environment

```powershell
# Copy template
copy .env.example .env

# Edit .env and fill in:
# - AZURE_SUBSCRIPTION_ID
# - AZURE_RESOURCE_GROUP
# - AZURE_ML_WORKSPACE
# - DVC_AZURE_CONTAINER
# - DVC_AZURE_PATH
notepad .env
```

### 5️⃣ Set MLflow Tracking URI

```powershell
python -m mlops_lineage azureml set-tracking-uri
# Or
.\scripts\set_mlflow_tracking_uri.ps1
```

**Restart your terminal/IDE** to load the new MLFLOW_TRACKING_URI.

### 6️⃣ Initialize Git and DVC

```powershell
# Initialize Git
git init
git add .
git commit -m "Initial commit"

# Initialize DVC remote
python -m mlops_lineage dvc init-remote
# Or
.\scripts\init_dvc_remote.ps1

# Commit DVC config
git add .dvc/config
git commit -m "Configure DVC Azure remote"
```

### 7️⃣ Add Your First Dataset

```powershell
# Create dataset directory
mkdir datasets\kidney_textures\train
mkdir datasets\kidney_textures\test

# Add your data files (copy images, CSVs, etc.)
# Example: copy your files to datasets\kidney_textures\train\

# Push dataset
python -m mlops_lineage dataset push --dataset-id kidney_textures --message "Add kidney textures v1"
# Or
.\scripts\push_new_dataset.ps1 -DatasetId "kidney_textures" -Message "Add kidney textures v1"
```

### 8️⃣ Train and Register Your First Model

```powershell
python -m mlops_lineage model train --model-name kidney_classifier --dataset-id kidney_textures
# Or
.\scripts\train_register_model.ps1 -ModelName "kidney_classifier" -DatasetId "kidney_textures"
```

### 9️⃣ View Model Information

```powershell
# List model versions
python -m mlops_lineage model list --model-name kidney_classifier

# View specific version details
python -m mlops_lineage model info --model-name kidney_classifier --model-version 1
```

### 🔟 Test Reproducibility

```powershell
# Pull the exact dataset used by model version 1
python -m mlops_lineage model pull-data --model-name kidney_classifier --model-version 1
# Or
.\scripts\pull_data_for_model.ps1 -ModelName "kidney_classifier" -ModelVersion 1

# Dataset will be available at: .worktrees\<commit>\datasets\kidney_textures\
```

---

## 🎯 Daily Workflow

### Add/Update Dataset

```powershell
# For NEW dataset
.\scripts\push_new_dataset.ps1 -DatasetId "my_dataset"

# For EXISTING dataset (append data)
.\scripts\append_to_dataset.ps1 -DatasetId "my_dataset"
```

### Train Model

```powershell
.\scripts\train_register_model.ps1 `
    -ModelName "my_model" `
    -DatasetId "my_dataset" `
    -Experiment "my_experiment"
```

### Retrieve Dataset for Model

```powershell
.\scripts\pull_data_for_model.ps1 `
    -ModelName "my_model" `
    -ModelVersion 1
```

---

## 🔧 Common Commands

```powershell
# Activate environment
conda activate mlops-lineage

# Check status
git status
dvc status

# View DVC remote
dvc remote list

# View model versions
python -m mlops_lineage model list --model-name <name>

# View model details
python -m mlops_lineage model info --model-name <name> --model-version <ver>
```

---

## ⚠️ Troubleshooting

**"az not found"**
→ Install Azure CLI and restart terminal

**"MLFLOW_TRACKING_URI not set"**
→ Run `python -m mlops_lineage azureml set-tracking-uri` and restart

**"Conda environment not activated"**
→ Run `conda activate mlops-lineage`

**"DVC push failed"**
→ Run `az login` and verify storage container exists

---

## ✅ Success Checklist

- [ ] Conda environment created and activated
- [ ] Azure login successful
- [ ] .env file configured
- [ ] MLflow tracking URI set
- [ ] DVC remote configured
- [ ] First dataset pushed
- [ ] First model trained and registered
- [ ] Dataset retrieved using model pull-data

---

**You're all set! Happy MLOps! 🎉**

For detailed documentation, see [README.md](README.md)
