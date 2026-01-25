# Initialize DVC Azure Remote
# This script configures DVC to use Azure Blob Storage as the default remote

Write-Host "=== Initializing DVC Azure Remote ===" -ForegroundColor Cyan
Write-Host ""

# Check if conda environment is activated
if (-not $env:CONDA_DEFAULT_ENV) {
    Write-Host "ERROR: Conda environment not activated" -ForegroundColor Red
    Write-Host "Please activate your environment first:" -ForegroundColor Yellow
    Write-Host "  conda activate mlops-lineage" -ForegroundColor Yellow
    exit 1
}

Write-Host "Conda environment: $env:CONDA_DEFAULT_ENV" -ForegroundColor Green
Write-Host ""

# Run the CLI command
python -m mlops_lineage dvc init-remote

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== SUCCESS ===" -ForegroundColor Green
    Write-Host "DVC remote configured successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "=== FAILED ===" -ForegroundColor Red
    Write-Host "DVC remote configuration failed. Check the error messages above." -ForegroundColor Red
    exit 1
}
