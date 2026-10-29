# Run OpenModelica (omc) for this project through a temporary drive-letter alias.
#
# Why: omc 1.27.1 cannot find its bundled C compiler when its install path contains a
# non-ASCII character, and the project root contains one (E-acute). Mapping the root to an
# ASCII drive letter with subst avoids that. See verification\openmodelica-launcher.md.
#
# Keep this file ASCII-only: Windows PowerShell 5.1 reads BOM-less files as ANSI.
#
# Usage (from any directory):
#   & '<project root>\verification\Invoke-OpenModelica.ps1'                 # version + compile/simulate smoke test
#   & '<project root>\verification\Invoke-OpenModelica.ps1' -Mos verification\modelica\scripts\x.mos
#
# Guarantees: the alias is created only if its letter is unused, only the alias created by
# this invocation is removed, and process environment variables are restored in finally.
# Nothing is written to the user or machine environment. Exit code 0 only if every step passed.

[CmdletBinding()]
param(
    [string[]]$Mos = @(),
    [string]$WorkDir = 'verification\modelica-build',
    [switch]$Smoke,
    [ValidatePattern('^[A-Za-z]$')][string]$DriveLetter,
    [string]$Label = 'run',
    [int]$TimeoutSec = 1800
)

Set-StrictMode -Version 2
$ErrorActionPreference = 'Stop'

$exitCode = 1
$created = $false
$letter = $null
$saved = @{}
$lines = New-Object System.Collections.Generic.List[string]
$steps = New-Object System.Collections.Generic.List[object]
$cleanup = [ordered]@{ alias_created = $false; alias_removed = $false; alias_still_mapped = $null; other_mappings_unchanged = $null; env_restored = $false }

function Say([string]$t) { $script:lines.Add($t); Write-Host $t }

function Get-SubstMap {
    # returns hashtable letter -> target text as printed by subst
    $m = @{}
    foreach ($l in @(& subst 2>$null)) {
        if ($l -match '^([A-Za-z]):\\: => (.*)$') { $m[$Matches[1].ToUpper()] = $Matches[2] }
    }
    return $m
}

function Test-LetterInUse([string]$L) {
    $L = $L.ToUpper()
    if ((Get-SubstMap).ContainsKey($L)) { return $true }
    foreach ($d in [System.IO.DriveInfo]::GetDrives()) { if ($d.Name.Substring(0, 1).ToUpper() -eq $L) { return $true } }
    foreach ($d in Get-PSDrive -PSProvider FileSystem) { if ($d.Name.ToUpper() -eq $L) { return $true } }
    if (Test-Path -LiteralPath ($L + ':\')) { return $true }
    return $false
}

try {
    # 1. project root from this script's own location
    $scriptDir = $PSScriptRoot
    $root = (Resolve-Path -LiteralPath (Join-Path $scriptDir '..')).Path
    if ((Split-Path -Leaf $scriptDir) -ne 'verification') { throw "Script is not in a 'verification' folder: $scriptDir" }
    foreach ($marker in 'project.env', '.git', 'configs\parameters.yaml') {
        if (-not (Test-Path -LiteralPath (Join-Path $root $marker))) { throw "Not the project root (missing $marker): $root" }
    }
    Say "project root : $root"

    # 2. OpenModelica installation and compiler
    $omHome = Join-Path $root 'tools\OpenModelica'
    $omc = Join-Path $omHome 'bin\omc.exe'
    $gcc = Join-Path $omHome 'tools\msys\ucrt64\bin\gcc.exe'
    foreach ($p in $omc, $gcc) { if (-not (Test-Path -LiteralPath $p)) { throw "Required file not found: $p" } }
    Say "omc          : $omc"
    Say "gcc (bundled): $gcc"

    $substBefore = Get-SubstMap

    # 3./4. choose an unused letter; fail safely if a requested one is taken
    if ($DriveLetter) {
        $letter = $DriveLetter.ToUpper()
        if (Test-LetterInUse $letter) { throw "Requested drive letter ${letter}: is already in use. Nothing was changed." }
    } else {
        foreach ($c in 'Y', 'X', 'W', 'V', 'U', 'T', 'S', 'R', 'Q', 'P') {
            if (-not (Test-LetterInUse $c)) { $letter = $c; break }
        }
        if (-not $letter) { throw 'No unused drive letter available among P-Y.' }
    }

    # 5. create the alias (only now does this invocation own it)
    & subst ($letter + ':') $root
    if ($LASTEXITCODE -ne 0) { throw "subst failed with exit code $LASTEXITCODE" }
    $created = $true
    $cleanup.alias_created = $true
    $al = $letter + ':'
    # confirm the alias really is this project root: this very script must be identical through it
    $viaAlias = Join-Path $al 'verification\Invoke-OpenModelica.ps1'
    $h1 = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash
    $h2 = (Get-FileHash -LiteralPath $viaAlias -Algorithm SHA256).Hash
    if ($h1 -ne $h2) { throw "Alias $al does not resolve to the project root (script hash mismatch)." }
    Say "alias        : $al -> project root (verified by script hash)"

    # 6. alias-based paths
    $aOmHome = Join-Path $al 'tools\OpenModelica'
    $aOmc = Join-Path $aOmHome 'bin\omc.exe'
    $aWork = Join-Path $al $WorkDir
    $realWork = Join-Path $root $WorkDir
    $logDir = Join-Path $realWork 'logs'
    $tmpDir = Join-Path $realWork 'tmp'
    $userRoot = Join-Path $root 'verification\omc-userdata'
    foreach ($d in $realWork, $logDir, $tmpDir, (Join-Path $userRoot 'Roaming'), (Join-Path $userRoot 'Local')) {
        if (-not (Test-Path -LiteralPath $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
    }
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'

    # 7./8. process-scoped environment, saved for restoration
    $names = 'OPENMODELICAHOME', 'APPDATA', 'LOCALAPPDATA', 'TEMP', 'TMP', 'PATH'
    foreach ($n in $names) { $saved[$n] = [Environment]::GetEnvironmentVariable($n, 'Process') }
    Say ("saved process env OPENMODELICAHOME = [" + $saved['OPENMODELICAHOME'] + "] (machine value is not touched)")
    $new = @{
        OPENMODELICAHOME = $aOmHome
        APPDATA          = (Join-Path $al 'verification\omc-userdata\Roaming')
        LOCALAPPDATA     = (Join-Path $al 'verification\omc-userdata\Local')
        TEMP             = (Join-Path $al ($WorkDir + '\tmp'))
        TMP              = (Join-Path $al ($WorkDir + '\tmp'))
        PATH             = ((Join-Path $aOmHome 'bin') + ';' + $saved['PATH'])
    }
    foreach ($n in $names) { [Environment]::SetEnvironmentVariable($n, $new[$n], 'Process') }

    function Invoke-Omc([string]$Name, [string[]]$OmcArgs, [string]$Cwd) {
        $o = Join-Path $logDir ("$stamp-$Label-$Name.out.txt")
        $e = Join-Path $logDir ("$stamp-$Label-$Name.err.txt")
        $sw = [Diagnostics.Stopwatch]::StartNew()
        $proc = Start-Process -FilePath $aOmc -ArgumentList $OmcArgs -WorkingDirectory $Cwd -NoNewWindow -PassThru -RedirectStandardOutput $o -RedirectStandardError $e
        $null = $proc.Handle   # cache the handle, otherwise ExitCode can be null after -PassThru
        $done = $proc.WaitForExit($TimeoutSec * 1000)
        if (-not $done) { try { $proc.Kill() } catch { }; $code = -999 }
        else {
            $proc.WaitForExit()
            $code = $proc.ExitCode
            if ($null -eq $code) { $code = -998; Say '  warning: exit code unavailable, treated as failure (-998)' }
        }
        $sw.Stop()
        $out = if (Test-Path -LiteralPath $o) { Get-Content -LiteralPath $o -Raw } else { '' }
        $err = if (Test-Path -LiteralPath $e) { Get-Content -LiteralPath $e -Raw } else { '' }
        $r = [pscustomobject]@{ name = $Name; command = ("omc " + ($OmcArgs -join ' ')); exit_code = $code; seconds = [math]::Round($sw.Elapsed.TotalSeconds, 2); stdout_file = $o; stderr_file = $e; stdout = $out; stderr = $err }
        $script:steps.Add($r)
        Say ("step {0}: exit={1} time={2}s  stdout={3}" -f $Name, $code, $r.seconds, $o)
        return $r
    }

    # 9. omc --version
    if (-not (Test-Path -LiteralPath $aWork)) { New-Item -ItemType Directory -Path $realWork -Force | Out-Null }
    $v = Invoke-Omc 'version' @('--version') $aWork
    Say ("omc version : " + $v.stdout.Trim())
    $ok = ($v.exit_code -eq 0 -and $v.stdout -match 'OpenModelica v1\.27\.1')

    # 9. compile + simulate smoke test (linear-drag coast-down, closed form known)
    if ($Smoke -or $Mos.Count -eq 0) {
        $smokeDir = Join-Path $realWork 'launcher-smoke'
        if (-not (Test-Path -LiteralPath $smokeDir)) { New-Item -ItemType Directory -Path $smokeDir | Out-Null }
        $src = ($al + '/verification/openmodelica-smoke/CoastDown.mo')
        $sd = ($al + '/' + ($WorkDir -replace '\\', '/') + '/launcher-smoke')
        $mosText = @(
            ('loadFile("' + $src + '"); getErrorString();'),
            ('cd("' + $sd + '");'),
            'simulate(CoastDown, startTime = 0, stopTime = 20, numberOfIntervals = 2000, tolerance = 1e-10, outputFormat = "csv"); getErrorString();'
        ) -join "`r`n"
        $smokeMos = Join-Path $smokeDir 'smoke.mos'
        [IO.File]::WriteAllText($smokeMos, $mosText + "`r`n", (New-Object Text.UTF8Encoding($false)))
        $s = Invoke-Omc 'smoke' @((Join-Path $al ($WorkDir + '\launcher-smoke\smoke.mos'))) (Join-Path $al ($WorkDir + '\launcher-smoke'))
        $res = Join-Path $smokeDir 'CoastDown_res.csv'
        $sOk = ($s.exit_code -eq 0 -and $s.stdout -match 'The simulation finished successfully' -and (Test-Path -LiteralPath $res))
        if ($sOk) {
            $last = (Get-Content -LiteralPath $res -Tail 1).Split(',')
            $hdr = (Get-Content -LiteralPath $res -TotalCount 1).Replace('"', '').Split(',')
            $iv = [array]::IndexOf($hdr, 'v'); $it = [array]::IndexOf($hdr, 'time')
            $tEnd = [double]::Parse($last[$it], [Globalization.CultureInfo]::InvariantCulture)
            $vEnd = [double]::Parse($last[$iv], [Globalization.CultureInfo]::InvariantCulture)
            $vExact = 10.0 * [math]::Exp(-25.0 * $tEnd / 850.0)
            $err = [math]::Abs($vEnd - $vExact)
            Say ("smoke result: t_end={0} v_end={1} closed form={2} |error|={3:E2}  file={4}" -f $tEnd, $vEnd, $vExact, $err, $res)
            if ($err -gt 1e-6) { $sOk = $false; Say 'smoke result outside 1e-6 sanity tolerance' }
        }
        $ok = $ok -and $sOk
    }

    # user-supplied scripts
    foreach ($m in $Mos) {
        $full = if ([IO.Path]::IsPathRooted($m)) { $m } else { Join-Path $root $m }
        $full = (Resolve-Path -LiteralPath $full).Path
        if (-not $full.StartsWith($root, [StringComparison]::OrdinalIgnoreCase)) { throw "Script is outside the project root: $full" }
        $rel = $full.Substring($root.Length).TrimStart('\')
        $r = Invoke-Omc ([IO.Path]::GetFileNameWithoutExtension($m)) @((Join-Path $al $rel)) $aWork
        $bad = ($r.exit_code -ne 0)
        if ($r.stdout -match '(?m)^Error:' -or $r.stderr -match '(?m)Error') { Say '  note: "Error" text present in omc output, inspect the stdout file' }
        if ($bad) { $ok = $false }
    }
    if ($ok) { $exitCode = 0 } else { $exitCode = 1 }
}
catch {
    Say ("LAUNCHER ERROR: " + $_.Exception.Message)
    $exitCode = 2
}
finally {
    # 10. restore process environment
    try {
        foreach ($n in $saved.Keys) { [Environment]::SetEnvironmentVariable($n, $saved[$n], 'Process') }
        $cleanup.env_restored = $true
    } catch { Say ("env restore failed: " + $_.Exception.Message) }
    # 11./12. remove only the alias this invocation created
    if ($created -and $letter) {
        try {
            & subst ($letter + ':') /D
            $after = Get-SubstMap
            $cleanup.alias_removed = ($LASTEXITCODE -eq 0)
            $cleanup.alias_still_mapped = $after.ContainsKey($letter)
            $same = ($after.Count -eq $substBefore.Count)
            if ($same) { foreach ($k in $substBefore.Keys) { if (-not $after.ContainsKey($k) -or $after[$k] -ne $substBefore[$k]) { $same = $false } } }
            $cleanup.other_mappings_unchanged = $same
        } catch { Say ("alias removal failed: " + $_.Exception.Message) }
    }
    Say ("cleanup      : " + (($cleanup.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join '; '))
    if ($created -and ($cleanup.alias_still_mapped -ne $false -or -not $cleanup.env_restored)) { $exitCode = 3 }
    try {
        if ($logDir -and (Test-Path -LiteralPath $logDir)) {
            $summary = [ordered]@{ label = $Label; time = (Get-Date -Format s); exit_code = $exitCode; project_root = $root; letter = $letter; cleanup = $cleanup
                steps = @($steps | ForEach-Object { [ordered]@{ name = $_.name; command = $_.command; exit_code = $_.exit_code; seconds = $_.seconds; stdout_file = $_.stdout_file } }) }
            $jf = Join-Path $logDir ("$stamp-$Label-launcher.json")
            ($summary | ConvertTo-Json -Depth 5) | Set-Content -LiteralPath $jf -Encoding UTF8
            Say "summary file : $jf"
        }
    } catch { }
    Say "LAUNCHER EXIT CODE: $exitCode"
}
exit $exitCode
