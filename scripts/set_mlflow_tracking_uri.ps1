# Set MLflow Tracking URI from Azure ML Workspace
# This script fetches the MLflow tracking URI and saves it to .env

Write-Host "=== Setting MLflow Tracking URI ===" -ForegroundColor Cyan
Write-Host ""

# Check if Azure CLI is installed
try {
    $azVersion = az --version 2>&1 | Select-Object -First 1
    Write-Host "Azure CLI: $azVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Azure CLI not found" -ForegroundColor Red
    Write-Host "Please install Azure CLI:" -ForegroundColor Yellow
    Write-Host "  https://aka.ms/installazurecliwindows" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and fill in your values:" -ForegroundColor Yellow
    Write-Host "  copy .env.example .env" -ForegroundColor Yellow
    exit 1
}

Write-Host "Fetching MLflow tracking URI from Azure ML workspace..." -ForegroundColor Cyan
Write-Host ""

# Run the CLI command
python -m mlops_lineage azureml set-tracking-uri

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== SUCCESS ===" -ForegroundColor Green
    Write-Host "MLflow tracking URI saved to .env!" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Please reload your .env file or restart your terminal/IDE" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "=== FAILED ===" -ForegroundColor Red
    Write-Host "Failed to set MLflow tracking URI. Check the error messages above." -ForegroundColor Red
    exit 1
}
