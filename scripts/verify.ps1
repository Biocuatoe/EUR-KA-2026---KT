<#
.SYNOPSIS
    Verifies the EUREKA 2026 environment and records every check.

.DESCRIPTION
    Every check runs a real command; PASS is recorded only from its exit code and
    output. Writes:
      D:\EUREKA-2026\logs\verify-<stamp>.log                                 full output
      D:\EUREKA-2026\artifacts\reports\environment-verification-<stamp>.json  per-check results
      D:\EUREKA-2026\artifacts\reports\pytest-<stamp>.xml                     JUnit test report
    Exits 0 only if every check passes. Read-only apart from those outputs, the test
    figure and the project caches.

.EXAMPLE
    powershell -NoProfile -ExecutionPolicy RemoteSigned -File D:\EUREKA-2026\repo\scripts\verify.ps1
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '_common.ps1')
$null = Import-ProjectEnv
$env:UV_NO_PROGRESS = '1'
if (-not (Test-Path -LiteralPath $env:TEMP)) { New-Item -ItemType Directory -Path $env:TEMP | Out-Null }

$root = $env:EUREKA_ROOT
$repo = $EurekaRepoDir
$venv = $env:UV_PROJECT_ENVIRONMENT
$py = Join-Path $venv 'Scripts\python.exe'
$ruff = Join-Path $venv 'Scripts\ruff.exe'
$jupyter = Join-Path $venv 'Scripts\jupyter.exe'
$cacheRoot = Join-Path $root 'cache'
$expectedPython = (Get-Content -LiteralPath (Join-Path $repo '.python-version') -TotalCount 1).Trim()
$uv = (Get-Command uv -ErrorAction Stop).Source

$start = Get-Date
$stamp = $start.ToString('yyyyMMdd-HHmmss')
$log = Join-Path $root "logs\verify-$stamp.log"
$reports = Join-Path $root 'artifacts\reports'
$jsonOut = Join-Path $reports "environment-verification-$stamp.json"
$junit = Join-Path $reports "pytest-$stamp.xml"
$checks = New-Object System.Collections.Generic.List[object]

function Add-Check {
    param([string]$Name, $Result, [bool]$Pass, [string]$Note = '')
    $status = $(if ($Pass) { 'PASS' } else { 'FAIL' })
    $out = $(if ($Result) { [string]$Result.Output } else { '' })
    if ($out.Length -gt 6000) { $out = $out.Substring(0, 6000) + ' ...[truncated; see log]' }
    $checks.Add([pscustomobject][ordered]@{
            name      = $Name
            status    = $status
            command   = $(if ($Result) { $Result.Command } else { '' })
            exit_code = $(if ($Result) { $Result.ExitCode } else { $null })
            note      = $Note
            output    = $out
        })
    Write-Log $log ("[{0}] {1}  {2}" -f $status, $Name, $Note)
}

function ConvertFrom-JsonText {
    # Parses the JSON object in a command's output, ignoring any stray stderr lines around it.
    param([string]$Text)
    $i = $Text.IndexOf('{'); $j = $Text.LastIndexOf('}')
    if ($i -lt 0 -or $j -lt $i) { return $null }
    return $Text.Substring($i, $j - $i + 1) | ConvertFrom-Json
}

function Test-Under {
    param([string]$Path, [string]$Parent)
    return [bool]$Path -and $Path.Trim().StartsWith($Parent, [StringComparison]::OrdinalIgnoreCase)
}

Write-Log $log "EUREKA-2026 verification started $($start.ToString('o')) on $env:COMPUTERNAME"

# 1-3. Interpreter ---------------------------------------------------------------
$r = Invoke-Native $py @('--version') -LogFile $log
Add-Check 'python version' $r ($r.ExitCode -eq 0 -and $r.Output.Trim() -eq "Python $expectedPython") "expected Python $expectedPython"

$r = Invoke-Native $py @('-m', 'pip', '--version') -LogFile $log
Add-Check 'pip version (from .venv)' $r ($r.ExitCode -eq 0 -and $r.Output -like "*$venv*")

$r = Invoke-Native $py @('-c', 'import json,sys; print(json.dumps(dict(executable=sys.executable, prefix=sys.prefix, base_prefix=sys.base_prefix)))') -LogFile $log
$p = $(if ($r.ExitCode -eq 0) { ConvertFrom-JsonText $r.Output } else { $null })
$okPaths = $p -and ($p.prefix -ieq $venv) -and (Test-Under $p.executable $venv) -and (Test-Under $p.base_prefix $env:UV_PYTHON_INSTALL_DIR)
Add-Check 'interpreter and venv paths' $r $okPaths "prefix == $venv; base_prefix under $env:UV_PYTHON_INSTALL_DIR"

Push-Location $repo
try {
    # 4. Lock and dependency consistency ----------------------------------------
    $r = Invoke-Native $uv @('lock', '--check') -LogFile $log
    Add-Check 'uv.lock matches pyproject.toml' $r ($r.ExitCode -eq 0)
    $r = Invoke-Native $uv @('sync', '--check') -LogFile $log
    Add-Check '.venv matches uv.lock exactly' $r ($r.ExitCode -eq 0)
    $r = Invoke-Native $uv @('pip', 'check', '--python', $py) -LogFile $log
    Add-Check 'uv pip check' $r ($r.ExitCode -eq 0)
    $r = Invoke-Native $py @('-m', 'pip', 'check') -LogFile $log
    Add-Check 'pip check' $r ($r.ExitCode -eq 0)

    # 5. Imports and resolved versions -------------------------------------------
    $r = Invoke-Native $py @((Join-Path $repo 'scripts\check_imports.py')) -LogFile $log
    $imports = ConvertFrom-JsonText $r.Output
    Add-Check 'imports and versions match uv.lock' $r ($r.ExitCode -eq 0) $(if ($imports) { "$($imports.installed_count) distributions installed" })

    # 6. Test suite: numerics, LQR, Pint, YAML/Pydantic, statsmodels, plot, cache paths
    $r = Invoke-Native $py @('-m', 'pytest', '--junitxml', $junit, '--cov=tests', '--cov-report=term') -LogFile $log
    $summary = ($r.Output -split "`r?`n" | Where-Object { $_ -match '^=+ .*(passed|failed|error).* =+$' } | Select-Object -Last 1)
    Add-Check 'pytest' $r ($r.ExitCode -eq 0) "$summary"

    $figure = Join-Path $root 'artifacts\figures\environment-check\lqr_double_integrator.png'
    $fig = Get-Item -LiteralPath $figure -ErrorAction SilentlyContinue
    Add-Check 'plot written on D:' $null ($fig -and $fig.Length -gt 0 -and $fig.LastWriteTime -ge $start) "$figure"

    # 7. Lint and format -----------------------------------------------------------
    $r = Invoke-Native $ruff @('check', '.') -LogFile $log
    Add-Check 'ruff check' $r ($r.ExitCode -eq 0)
    $r = Invoke-Native $ruff @('format', '--check', '.') -LogFile $log
    Add-Check 'ruff format --check' $r ($r.ExitCode -eq 0)

    # 8. Jupyter kernel --------------------------------------------------------------
    $r = Invoke-Native $jupyter @('kernelspec', 'list', '--json') -LogFile $log
    $ks = $(if ($r.ExitCode -eq 0) { (ConvertFrom-JsonText $r.Output).kernelspecs.'eureka-2026' } else { $null })
    Add-Check 'kernelspec eureka-2026 registered in .venv' $r ($ks -and (Test-Under $ks.resource_dir $venv) -and (Test-Under $ks.spec.argv[0] $venv))
    $r = Invoke-Native $py @((Join-Path $repo 'scripts\check_kernel.py')) -LogFile $log
    Add-Check 'kernel starts and executes in .venv' $r ($r.ExitCode -eq 0)

    # 9. Cache locations ---------------------------------------------------------------
    $r = Invoke-Native $uv @('cache', 'dir') -LogFile $log
    Add-Check 'uv cache dir' $r ($r.ExitCode -eq 0 -and (Test-Under $r.Output $cacheRoot))
    $r = Invoke-Native $py @('-m', 'pip', 'cache', 'dir') -LogFile $log
    Add-Check 'pip cache dir' $r ($r.ExitCode -eq 0 -and (Test-Under $r.Output $cacheRoot))
    $r = Invoke-Native $ruff @('check', '--show-settings', 'tests\conftest.py') -Quiet
    $line = ($r.Output -split "`r?`n" | Where-Object { $_ -match '^\s*cache_dir\s*=' } | Select-Object -First 1)
    $r.Output = "$line"
    Add-Content -LiteralPath $log -Encoding UTF8 -Value @("> $($r.Command)", $line, "[exit $($r.ExitCode)]", '')
    Add-Check 'ruff cache dir' $r ($r.ExitCode -eq 0 -and $line -like "*$cacheRoot*")

    $stray = @('.pytest_cache', '.ruff_cache', '.hypothesis', '.coverage', '.mypy_cache', '.venv') |
        ForEach-Object { Join-Path $repo $_ } | Where-Object { Test-Path -LiteralPath $_ }
    Add-Check 'no tool caches or venv inside repo\' $null (@($stray).Count -eq 0) (@($stray) -join '; ')
} finally {
    Pop-Location
}

# 10. Anything written to the usual C: locations during this run? ------------------
$userTemp = [Environment]::ExpandEnvironmentVariables([Environment]::GetEnvironmentVariable('TEMP', 'User'))
$watch = @(
    "$env:LOCALAPPDATA\uv", "$env:APPDATA\uv", "$env:LOCALAPPDATA\pip",
    "$env:USERPROFILE\.matplotlib", "$env:USERPROFILE\.jupyter", "$env:APPDATA\jupyter",
    "$env:LOCALAPPDATA\jupyter", "$env:USERPROFILE\.ipython", "$env:USERPROFILE\.local\bin",
    "$env:USERPROFILE\.cache", (Join-Path $userTemp "pytest-of-$env:USERNAME")
)
$written = @(foreach ($w in $watch) {
        if (Test-Path -LiteralPath $w) {
            Get-ChildItem -LiteralPath $w -Recurse -Force -ErrorAction SilentlyContinue |
                Where-Object { $_.LastWriteTime -ge $start } | ForEach-Object { $_.FullName }
        }
    })
$watchResult = [pscustomobject]@{ Command = 'scan: ' + ($watch -join '; '); ExitCode = 0; Output = ($written -join [Environment]::NewLine) }
Add-Check 'no writes to watched C: locations during verification' $watchResult ($written.Count -eq 0) "$($written.Count) file(s) written"

# Report ---------------------------------------------------------------------------------
$failed = @($checks | Where-Object { $_.status -eq 'FAIL' }).Count
$disk = @{}
foreach ($d in 'C', 'D') { $disk[$d] = [math]::Round((Get-PSDrive $d).Free / 1GB, 2) }
$report = [ordered]@{
    started        = $start.ToString('o')
    finished       = (Get-Date).ToString('o')
    machine        = $env:COMPUTERNAME
    root           = $root
    interpreter    = $py
    uv             = $uv
    passed         = $checks.Count - $failed
    failed         = $failed
    disk_free_gb   = $disk
    direct_imports = $(if ($imports) { $imports.direct_imports } else { $null })
    checks         = $checks
    junit_report   = $junit
    log            = $log
}
$report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $jsonOut -Encoding UTF8

Write-Log $log ''
Write-Log $log ("{0} checks: {1} passed, {2} failed" -f $checks.Count, ($checks.Count - $failed), $failed)
Write-Log $log "report: $jsonOut"
Write-Log $log "log:    $log"
exit $(if ($failed -eq 0) { 0 } else { 1 })
