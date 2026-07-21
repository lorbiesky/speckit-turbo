[CmdletBinding()]
param(
    [Parameter(Position = 0)] [string]$Target = ".",
    [ValidateSet("auto", "clean", "existing")] [string]$Mode = "auto",
    [string]$SpecKitVersion,
    [switch]$Upgrade,
    [switch]$Version
)

$ErrorActionPreference = "Stop"
$SourceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Python = (Get-Command python3 -ErrorAction SilentlyContinue).Source
if (-not $Python) { $Python = (Get-Command python -ErrorAction SilentlyContinue).Source }
if (-not $Python) { throw "Python 3 is required to install Spec Kit Turbo." }
$Arguments = @()
if ($Version) { $Arguments += "--version" }
else {
    $Arguments += @("--mode", $Mode, $Target)
    if ($SpecKitVersion) { $Arguments += @("--spec-kit-version", $SpecKitVersion) }
    if ($Upgrade) { $Arguments += "--upgrade" }
}
& $Python (Join-Path $SourceRoot "scripts/turbo_install.py") @Arguments
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
