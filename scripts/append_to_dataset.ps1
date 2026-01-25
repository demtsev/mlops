# Append to Existing Dataset
# This script updates an existing dataset and pushes changes to Azure Blob Storage

param(
    [Parameter(Mandatory=$true)]
    [string]$DatasetId,
    
    [Parameter(Mandatory=$false)]
    [string]$Message = ""
)

Write-Host "=== Appending to Dataset ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dataset ID: $DatasetId" -ForegroundColor Yellow
Write-Host ""

# Check if conda environment is activated
if (-not $env:CONDA_DEFAULT_ENV) {
    Write-Host "ERROR: Conda environment not activated" -ForegroundColor Red
    Write-Host "Please activate your environment first:" -ForegroundColor Yellow
    Write-Host "  conda activate mlops-lineage" -ForegroundColor Yellow
    exit 1
}

# Check if dataset directory exists
$datasetPath = "datasets\$DatasetId"
if (-not (Test-Path $datasetPath)) {
    Write-Host "ERROR: Dataset directory not found: $datasetPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "This dataset has not been created yet." -ForegroundColor Yellow
    Write-Host "Use push_new_dataset.ps1 instead:" -ForegroundColor Yellow
    Write-Host "  .\scripts\push_new_dataset.ps1 -DatasetId `"$DatasetId`"" -ForegroundColor Yellow
    exit 1
}

# Check if .dvc file exists
$dvcFile = "datasets\$DatasetId.dvc"
if (-not (Test-Path $dvcFile)) {
    Write-Host "WARNING: .dvc file not found: $dvcFile" -ForegroundColor Yellow
    Write-Host "This dataset may not have been pushed before." -ForegroundColor Yellow
    Write-Host ""
}

# Count files
$fileCount = (Get-ChildItem -Path $datasetPath -File -Recurse | Measure-Object).Count
Write-Host "Dataset contains $fileCount file(s)" -ForegroundColor Green
Write-Host ""

# Build command
$cmd = "python -m mlops_lineage dataset add --dataset-id `"$DatasetId`""
if ($Message) {
    $cmd += " --message `"$Message`""
}

Write-Host "Running command:" -ForegroundColor Cyan
Write-Host "  $cmd" -ForegroundColor Gray
Write-Host ""

# Execute command
Invoke-Expression $cmd

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== SUCCESS ===" -ForegroundColor Green
    Write-Host "Dataset '$DatasetId' updated successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "=== FAILED ===" -ForegroundColor Red
    Write-Host "Failed to update dataset. Check the error messages above." -ForegroundColor Red
    exit 1
}
