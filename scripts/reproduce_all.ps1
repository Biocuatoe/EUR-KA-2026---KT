<#
.SYNOPSIS
    Regenerate every result of the evaluation (docs/lineage.md).

.DESCRIPTION
    Default: recompute analyses, tables, figures and evidence exports from the existing
    raw outputs in D:\EUREKA-2026\artifacts\raw (no simulation).
    -Rerun: also run the report audit, tuning acceptance, verification gate and all
    simulations. Existing raw outputs are overwritten only with -Force.
    Stops at the first failing step.

.EXAMPLE
    powershell -NoProfile -ExecutionPolicy RemoteSigned -File D:\EUREKA-2026\repo\scripts\reproduce_all.ps1
#>
[CmdletBinding()]
param([switch]$Rerun, [switch]$Force)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'activate.ps1')
Set-Location $EurekaRepoDir
$py = Join-Path $env:UV_PROJECT_ENVIRONMENT 'Scripts\python.exe'

function Step([string[]]$PyArgs) {
    Write-Host ("> python " + ($PyArgs -join ' ')) -ForegroundColor Cyan
    & $py @PyArgs
    if ($LASTEXITCODE -ne 0) { throw "step failed (exit $LASTEXITCODE): $($PyArgs -join ' ')" }
}

if ($Rerun) {
    $raw = Join-Path $env:EUREKA_ROOT 'artifacts\raw'
    if ((Test-Path -LiteralPath $raw) -and (Get-ChildItem -LiteralPath $raw).Count -gt 0 -and -not $Force) {
        throw "Raw outputs exist in $raw. Rerun with -Force to overwrite them."
    }
    Step @('scripts/audit_report.py')
    Step @('scripts/tuning_acceptance.py')
    Step @('scripts/run_gate.py')
    foreach ($e in 'primary', 'gamma_sweep', 'fixed_family') { Step @('scripts/run_experiment.py', $e) }
    Step @('scripts/run_experiment.py', 'robustness', '--stage', 'pilot')
    Step @('scripts/analyze.py', 'robustness', '--pilot')
    Step @('scripts/run_experiment.py', 'robustness', '--stage', 'main')
}
foreach ($e in 'primary', 'gamma_sweep', 'fixed_family', 'robustness') { Step @('scripts/analyze.py', $e) }
Step @('scripts/energy_breakdown.py')
Step @('scripts/make_figures.py')
Step @('scripts/build_evidence.py')
Write-Host 'All steps completed.' -ForegroundColor Green
