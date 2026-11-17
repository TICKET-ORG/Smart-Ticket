# SmartTicket local development runner (Windows PowerShell)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (Test-Path ".venv\Scripts\Activate.ps1") {
    . .\.venv\Scripts\Activate.ps1
}

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000