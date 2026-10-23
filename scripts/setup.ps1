<#
.SYNOPSIS
    Reproducible, rerunnable setup of the EUREKA 2026 research environment on D:.

.DESCRIPTION
    1. Creates any missing project folders (never deletes or overwrites data).
    2. Installs the CPython version pinned in .python-version into
       <project root>\tools\python (no PATH shims, no Windows registry entries).
    3. Checks uv.lock against pyproject.toml, then syncs <project root>\.venv
       exactly to uv.lock. If the sync would uninstall packages that are not in
       the lock, it stops and lists them unless -AllowPrune is given.
    4. Refuses to touch an existing .venv that was built from another interpreter.
    5. Registers the .venv as a Jupyter kernel inside the venv (--sys-prefix).
    6. Exports requirements-lock.txt (pip-compatible, hashed) from uv.lock.
    All caches are redirected to <project root>\cache via project.env.
    A full log is written to <project root>\logs\setup-<timestamp>.log.

.PARAMETER Relock
    Re-resolve uv.lock from pyproject.toml (use after editing dependencies).

.PARAMETER AllowPrune
    Allow the sync to uninstall packages present in .venv but absent from uv.lock.

.EXAMPLE
    powershell -NoProfile -ExecutionPolicy RemoteSigned -File <project root>\scripts\setup.ps1
#>
[CmdletBinding()]
param(
    [switch]$Relock,
    [switch]$AllowPrune
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '_common.ps1')
$null = Import-ProjectEnv
$env:UV_NO_PROGRESS = '1'

$root = $env:EUREKA_ROOT
$repo = $EurekaRepoDir
$venv = $env:UV_PROJECT_ENVIRONMENT
$venvPython = Join-Path $venv 'Scripts\python.exe'
$pythonVersion = (Get-Content -LiteralPath (Join-Path $repo '.python-version') -TotalCount 1).Trim()
$kernelName = 'eureka-2026'

$logDir = Join-Path $root 'logs'
if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$log = Join-Path $logDir ("setup-{0}.log" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
Write-Log $log "EUREKA-2026 setup started $(Get-Date -Format o) on $env:COMPUTERNAME"
Write-Log $log "Relock=$Relock AllowPrune=$AllowPrune PythonVersion=$pythonVersion"

# 1. Folder layout -----------------------------------------------------------
$dirs = @(
    'tools', 'tools\python', 'tools\jupyter\config', 'tools\jupyter\data',
    'cache', 'cache\uv', 'cache\pip', 'cache\matplotlib', 'cache\jupyter\runtime',
    'cache\ipython', 'cache\ruff', 'cache\coverage', 'cache\pytest', 'cache\hypothesis', 'cache\tmp',
    'data\raw', 'data\processed',
    'artifacts\raw', 'artifacts\figures', 'artifacts\tables', 'artifacts\reports',
    'logs', 'docs'
)
foreach ($d in $dirs) {
    $p = Join-Path $root $d
    if (-not (Test-Path -LiteralPath $p)) {
        New-Item -ItemType Directory -Path $p | Out-Null
        Write-Log $log "created  $p"
    }
}

# 2. uv ----------------------------------------------------------------------
$uv = (Get-Command uv -ErrorAction SilentlyContinue).Source
if (-not $uv) { throw 'uv not found on PATH. Install it with: winget install --id astral-sh.uv -e' }
Assert-Success (Invoke-Native $uv @('--version') -LogFile $log) 'uv --version'

# 3. Managed CPython on D: ---------------------------------------------------
Assert-Success (Invoke-Native $uv @('python', 'install', $pythonVersion,
        '--install-dir', $env:UV_PYTHON_INSTALL_DIR, '--no-bin', '--no-registry') -LogFile $log) 'uv python install'
# --system: ignore .venv, which `uv python find` would otherwise report when run inside repo\
$found = Invoke-Native $uv @('python', 'find', $pythonVersion, '--system') -LogFile $log
Assert-Success $found 'uv python find'
if (-not $found.Output.Trim().StartsWith($env:UV_PYTHON_INSTALL_DIR, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Resolved interpreter is not under $env:UV_PYTHON_INSTALL_DIR : $($found.Output)"
}

# 4. Never replace a venv built from a different interpreter ------------------
$cfg = Join-Path $venv 'pyvenv.cfg'
if (Test-Path -LiteralPath $cfg) {
    $homeLine = (Get-Content -LiteralPath $cfg | Where-Object { $_ -match '^\s*home\s*=' } | Select-Object -First 1)
    $venvHome = ($homeLine -split '=', 2)[1].Trim()
    if (-not $venvHome.StartsWith($env:UV_PYTHON_INSTALL_DIR, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Existing $venv was created from '$venvHome', not from $env:UV_PYTHON_INSTALL_DIR. Move or rename it yourself, then rerun."
    }
}

# 5. Lockfile ------------------------------------------------------------------
Push-Location $repo
try {
    if ($Relock -or -not (Test-Path -LiteralPath (Join-Path $repo 'uv.lock'))) {
        Assert-Success (Invoke-Native $uv @('lock') -LogFile $log) 'uv lock'
    } else {
        $check = Invoke-Native $uv @('lock', '--check') -LogFile $log
        if ($check.ExitCode -ne 0) { throw 'uv.lock does not match pyproject.toml. Rerun with -Relock if the dependency change is intended.' }
    }

    # 6. Sync .venv exactly to the lock, but never prune silently ---------------
    $dry = Invoke-Native $uv @('sync', '--locked', '--dry-run') -LogFile $log
    Assert-Success $dry 'uv sync --dry-run'
    $removals = @($dry.Output -split "`r?`n" | Where-Object { $_ -match '^\s*-\s+\S+==' })
    if ($removals.Count -gt 0 -and -not $AllowPrune) {
        throw ("uv sync would uninstall packages that are not in uv.lock:`n" + ($removals -join "`n") +
            "`nAdd them to pyproject.toml (then -Relock), or rerun with -AllowPrune to remove them.")
    }
    Assert-Success (Invoke-Native $uv @('sync', '--locked') -LogFile $log) 'uv sync'

    # 7. Pip-compatible pinned export (deterministic; rewritten only from uv.lock)
    Assert-Success (Invoke-Native $uv @('export', '--quiet', '--frozen', '--all-groups', '--format', 'requirements-txt',
            '--output-file', (Join-Path $repo 'requirements-lock.txt')) -LogFile $log) 'uv export'
} finally {
    Pop-Location
}

# 8. Jupyter kernel inside the venv (VS Code and Jupyter both discover it) -----
$kernelEnv = @()
foreach ($k in 'EUREKA_ROOT', 'MPLCONFIGDIR', 'IPYTHONDIR', 'JUPYTER_PLATFORM_DIRS', 'TEMP', 'TMP') {
    $kernelEnv += @('--env', $k, (Get-Item "Env:$k").Value)
}
Assert-Success (Invoke-Native $venvPython (@('-m', 'ipykernel', 'install', '--sys-prefix', '--name', $kernelName,
            '--display-name', "Python $pythonVersion (EUREKA-2026)") + $kernelEnv) -LogFile $log) 'ipykernel install'

Write-Log $log ''
Write-Log $log "Setup finished $(Get-Date -Format o)"
Write-Log $log "  interpreter : $venvPython"
Write-Log $log "  kernel      : $kernelName  ($venv\share\jupyter\kernels\$kernelName)"
Write-Log $log "  log         : $log"
Write-Log $log "Next: . $repo\scripts\activate.ps1 ; powershell -File $repo\scripts\verify.ps1"
