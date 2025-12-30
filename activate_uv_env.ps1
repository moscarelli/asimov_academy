# Activate UV-managed Python environment
# Usage: .\activate_uv_env.ps1

# Add UV to PATH
$env:Path += ";C:\Users\Avell\.local\bin"

# Activate the virtual environment
& .\.venv\Scripts\Activate.ps1

Write-Host "UV environment activated!" -ForegroundColor Green
Write-Host "Python version: $(python --version)" -ForegroundColor Cyan
Write-Host "UV version: $(uv --version)" -ForegroundColor Cyan
Write-Host ""
Write-Host "To sync dependencies: uv sync" -ForegroundColor Yellow
Write-Host "To add packages: uv add <package-name>" -ForegroundColor Yellow
Write-Host "To run Python: python or uv run python" -ForegroundColor Yellow
