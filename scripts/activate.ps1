# Activate the EUREKA 2026 environment in the current PowerShell session:
#
#     . D:\EUREKA-2026\repo\scripts\activate.ps1
#
# Loads repo\project.env (cache and runtime paths on D:) into this process only,
# then activates D:\EUREKA-2026\.venv. Nothing is written to the user or machine
# environment; closing the terminal undoes everything.

. (Join-Path $PSScriptRoot '_common.ps1')
$null = Import-ProjectEnv

# tempfile silently falls back to other locations if TEMP does not exist.
if (-not (Test-Path -LiteralPath $env:TEMP)) { New-Item -ItemType Directory -Path $env:TEMP | Out-Null }

$venvActivate = Join-Path $env:UV_PROJECT_ENVIRONMENT 'Scripts\Activate.ps1'
if (-not (Test-Path -LiteralPath $venvActivate)) {
    Write-Warning "No virtual environment at $env:UV_PROJECT_ENVIRONMENT. Run: powershell -File $EurekaRepoDir\scripts\setup.ps1"
    return
}
. $venvActivate
Write-Host "EUREKA-2026 active: $(Join-Path $env:UV_PROJECT_ENVIRONMENT 'Scripts\python.exe')  (caches under $env:EUREKA_ROOT\cache)" -ForegroundColor Green
