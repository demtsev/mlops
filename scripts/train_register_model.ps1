# Train and Register Model
# This script trains a model and registers it with lineage tags

param(
    [Parameter(Mandatory=$true)]
    [string]$ModelName,
    
    [Parameter(Mandatory=$true)]
    [string]$DatasetId,
    
    [Parameter(Mandatory=$false)]
    [string]$Experiment = "default_experiment"
)

Write-Host "=== Training and Registering Model ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Model Name: $ModelName" -ForegroundColor Yellow
Write-Host "Dataset ID: $DatasetId" -ForegroundColor Yellow
Write-Host "Experiment: $Experiment" -ForegroundColor Yellow
Write-Host ""

# Check if conda environment is activated
if (-not $env:CONDA_DEFAULT_ENV) {
    Write-Host "ERROR: Conda environment not activated" -ForegroundColor Red
    Write-Host "Please activate your environment first:" -ForegroundColor Yellow
    Write-Host "  conda activate mlops-lineage" -ForegroundColor Yellow
    exit 1
}

# Check if MLflow tracking URI is set
if (-not $env:MLFLOW_TRACKING_URI) {
    Write-Host "ERROR: MLFLOW_TRACKING_URI not set in .env" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run set_mlflow_tracking_uri.ps1 first:" -ForegroundColor Yellow
    Write-Host "  .\scripts\set_mlflow_tracking_uri.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "MLflow Tracking URI: $env:MLFLOW_TRACKING_URI" -ForegroundColor Green
Write-Host ""

# Build command
$cmd = "python -m mlops_lineage model train --model-name `"$ModelName`" --dataset-id `"$DatasetId`" --experiment `"$Experiment`""

Write-Host "Running command:" -ForegroundColor Cyan
Write-Host "  $cmd" -ForegroundColor Gray
Write-Host ""

# Execute command
Invoke-Expression $cmd

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== SUCCESS ===" -ForegroundColor Green
    Write-Host "Model '$ModelName' trained and registered successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "=== FAILED ===" -ForegroundColor Red
    Write-Host "Failed to train/register model. Check the error messages above." -ForegroundColor Red
    exit 1
}
