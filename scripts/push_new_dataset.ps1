# Push a New Dataset
# This script adds a new dataset to DVC and pushes it to Azure Blob Storage

param(
    [Parameter(Mandatory=$true)]
    [string]$DatasetId,
    
    [Parameter(Mandatory=$false)]
    [string]$Message = ""
)

Write-Host "=== Pushing New Dataset ===" -ForegroundColor Cyan
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
    Write-Host "Please create the directory and add your data files:" -ForegroundColor Yellow
    Write-Host "  mkdir $datasetPath" -ForegroundColor Yellow
    Write-Host "  # Add your data files to $datasetPath" -ForegroundColor Yellow
    exit 1
}

# Check if directory is empty
$fileCount = (Get-ChildItem -Path $datasetPath -File -Recurse | Measure-Object).Count
if ($fileCount -eq 0) {
    Write-Host "ERROR: Dataset directory is empty: $datasetPath" -ForegroundColor Red
    Write-Host "Please add your data files first." -ForegroundColor Yellow
    exit 1
}

Write-Host "Found $fileCount file(s) in dataset directory" -ForegroundColor Green
Write-Host ""

# Build command
$cmd = "python -m mlops_lineage dataset push --dataset-id `"$DatasetId`""
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
    Write-Host "Dataset '$DatasetId' pushed successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "=== FAILED ===" -ForegroundColor Red
    Write-Host "Failed to push dataset. Check the error messages above." -ForegroundColor Red
    exit 1
}
