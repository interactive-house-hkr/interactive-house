param(
    [int]$Port = 8000,
    [switch]$DisableBridge,
    [switch]$MockDispatch
)

# This script starts the FastAPI server for local development.
# It also sets simple auth defaults if they are missing.

$servicesRoot = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent $servicesRoot
Set-Location $repoRoot

# Prefer the project's virtual environment if it exists.
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    $pythonExe = $venvPython
} else {
    $pythonExe = "python"
}

# These values are only fallback defaults for local development.
# Real values from services/.env or your shell will still work.
if (-not $env:SECRET_KEY) {
    $env:SECRET_KEY = "dev-secret-key"
}

if (-not $env:ACCESS_TOKEN_EXPIRE_MINUTES) {
    $env:ACCESS_TOKEN_EXPIRE_MINUTES = "60"
}

if (-not $env:REFRESH_TOKEN_EXPIRE_DAYS) {
    $env:REFRESH_TOKEN_EXPIRE_DAYS = "7"
}

# Optional flags for easier local testing.
if ($DisableBridge) {
    $env:ENABLE_BRIDGE = "false"
}

if ($MockDispatch) {
    $env:MOCK_DISPATCH = "true"
}

Write-Host "Starting server on port $Port..."
& $pythonExe -m uvicorn services.src.main:app --reload --host 0.0.0.0 --port $Port

