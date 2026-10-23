# Shared helpers for setup.ps1, verify.ps1 and activate.ps1.
# Keep this file ASCII-only: Windows PowerShell 5.1 reads BOM-less files as ANSI.

$EurekaRepoDir = Split-Path -Parent $PSScriptRoot

function Import-ProjectEnv {
    # Loads KEY=VALUE lines from project.env into the current process environment.
    # project.env is UTF-8 (the project root path is not ASCII), so never read it as ANSI.
    param([string]$Path = (Join-Path $EurekaRepoDir 'project.env'))
    if (-not (Test-Path -LiteralPath $Path)) { throw "project.env not found: $Path" }
    $vars = [ordered]@{}
    foreach ($line in Get-Content -LiteralPath $Path -Encoding UTF8) {
        $t = $line.Trim()
        if (-not $t -or $t.StartsWith('#')) { continue }
        $i = $t.IndexOf('=')
        if ($i -lt 1) { throw "Malformed line in ${Path}: $line" }
        $vars[$t.Substring(0, $i).Trim()] = $t.Substring($i + 1).Trim()
    }
    foreach ($k in $vars.Keys) { Set-Item -Path "Env:$k" -Value $vars[$k] }
    return $vars
}

function Write-Log {
    param([string]$LogFile, [string]$Text)
    Write-Host $Text
    if ($LogFile) { Add-Content -LiteralPath $LogFile -Value $Text -Encoding UTF8 }
}

function Invoke-Native {
    # Runs a native command, logs the command line, combined output and exit code.
    # stderr is merged without letting PowerShell 5.1 turn it into terminating errors.
    param(
        [Parameter(Mandatory)][string]$Exe,
        [string[]]$Arguments = @(),
        [string]$LogFile,
        [switch]$Quiet
    )
    $cmdline = ($(@($Exe) + $Arguments) | ForEach-Object { if ($_ -match '\s') { '"' + $_ + '"' } else { $_ } }) -join ' '
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $out = @(& $Exe @Arguments 2>&1 | ForEach-Object { "$_" })
        $code = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $prev
    }
    $text = $out -join [Environment]::NewLine
    if ($LogFile) {
        Add-Content -LiteralPath $LogFile -Encoding UTF8 -Value @("> $cmdline", $text, "[exit $code]", '')
    }
    if (-not $Quiet) {
        Write-Host "> $cmdline" -ForegroundColor Cyan
        if ($text) { Write-Host $text }
        Write-Host "[exit $code]" -ForegroundColor $(if ($code -eq 0) { 'Green' } else { 'Red' })
    }
    return [pscustomobject]@{ Command = $cmdline; ExitCode = $code; Output = $text }
}

function Assert-Success {
    param($Result, [string]$What)
    if ($Result.ExitCode -ne 0) { throw "$What failed (exit $($Result.ExitCode)): $($Result.Command)" }
}
