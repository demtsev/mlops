# Pull Data for Model Version
# This script retrieves the exact dataset used to train a specific model version

param(
    [Parameter(Mandatory=$true)]
    [string]$ModelName,
    
    [Parameter(Mandatory=$true)]
    [int]$ModelVersion
)

Write-Host "=== Pulling Dataset for Model Version ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Model Name: $ModelName" -ForegroundColor Yellow
Write-Host "Model Version: $ModelVersion" -ForegroundColor Yellow
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
$cmd = "python -m mlops_lineage model pull-data --model-name `"$ModelName`" --model-version $ModelVersion"

Write-Host "Running command:" -ForegroundColor Cyan
Write-Host "  $cmd" -ForegroundColor Gray
Write-Host ""

# Execute command
Invoke-Expression $cmd

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== SUCCESS ===" -ForegroundColor Green
    Write-Host "Dataset retrieved successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "The dataset is now available in the .worktrees directory." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "=== FAILED ===" -ForegroundColor Red
    Write-Host "Failed to pull dataset. Check the error messages above." -ForegroundColor Red
    exit 1
}
