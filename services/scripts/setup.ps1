# This script installs the Python packages used by the server.
# It is safe to run again if everything is already installed.

$servicesRoot = Split-Path -Parent $PSScriptRoot
Set-Location $servicesRoot

# Prefer the project's virtual environment if it exists.
$venvPython = Join-Path $servicesRoot "..\.venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    $pythonExe = $venvPython
} else {
    $pythonExe = "python"
}

Write-Host "Installing server Python packages..."
& $pythonExe -m pip install -r .\requirements.txt

