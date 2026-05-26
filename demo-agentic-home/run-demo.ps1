[CmdletBinding()]
param(
    [ValidateSet("cli", "ui")]
    [string]$Mode = "cli",
    [switch]$SkipInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$DefaultVenvRoot = Join-Path $env:USERPROFILE ".venvs"
$DefaultVenvPath = Join-Path $DefaultVenvRoot "demo-agentic-home"
$VenvPath = if ($env:DEMO_AGENTIC_HOME_VENV_PATH) { $env:DEMO_AGENTIC_HOME_VENV_PATH } else { $DefaultVenvPath }
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"
$StreamlitExe = Join-Path $VenvPath "Scripts\streamlit.exe"

function Test-RequiredModules {
    param(
        [string]$PythonPath,
        [ValidateSet("cli", "ui")]
        [string]$RunMode
    )

    $modules = @("yaml", "pydantic")
    if ($RunMode -eq "ui") {
        $modules += "streamlit"
    }

    foreach ($module in $modules) {
        & $PythonPath -c "import $module" 2>$null
        if ($LASTEXITCODE -ne 0) {
            return $false
        }
    }

    return $true
}

function Get-RequirementsFile {
    param(
        [ValidateSet("cli", "ui")]
        [string]$RunMode
    )

    if ($RunMode -eq "ui") {
        return "requirements-ui.txt"
    }

    return "requirements-cli.txt"
}

Push-Location $ProjectRoot
try {
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        throw "Python is not installed or not available on PATH."
    }

    if (-not (Test-Path (Split-Path -Parent $VenvPath))) {
        New-Item -Path (Split-Path -Parent $VenvPath) -ItemType Directory | Out-Null
    }

    if (-not (Test-Path $VenvPath)) {
        Write-Host "[demo] Creating virtual environment at: $VenvPath"
        python -m venv "$VenvPath"
    }

    $requirementsFile = Get-RequirementsFile -RunMode $Mode
    $dependenciesReady = Test-RequiredModules -PythonPath $PythonExe -RunMode $Mode
    if (-not $SkipInstall -or -not $dependenciesReady) {
        if ($SkipInstall -and -not $dependenciesReady) {
            Write-Host "[demo] Dependencies missing in current venv; installing once before run..."
        }
        Write-Host "[demo] Installing dependencies from $requirementsFile..."
        & $PythonExe -m pip install -r $requirementsFile
    }

    if ($Mode -eq "cli") {
        Write-Host "[demo] Running CLI demo..."
        & $PythonExe -m src.main
    }
    else {
        Write-Host "[demo] Starting Streamlit UI..."
        & $StreamlitExe run src/ui/app.py
    }
}
finally {
    Pop-Location
}
