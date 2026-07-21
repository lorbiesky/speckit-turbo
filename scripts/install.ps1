[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Target = "."
)

$ErrorActionPreference = "Stop"
$SourceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if (-not (Test-Path -LiteralPath $Target -PathType Container)) {
    throw "Target directory does not exist: $Target"
}

$TargetRoot = (Resolve-Path -LiteralPath $Target).Path
$HadSpecify = Test-Path -LiteralPath (Join-Path $TargetRoot ".specify") -PathType Container
$SkillsTarget = Join-Path $TargetRoot ".agents/skills"
$TurboTarget = Join-Path $TargetRoot ".specify/turbo"
$RuntimeTarget = Join-Path $TurboTarget "runtime"

New-Item -ItemType Directory -Force -Path $SkillsTarget | Out-Null
New-Item -ItemType Directory -Force -Path $RuntimeTarget | Out-Null

Get-ChildItem -LiteralPath (Join-Path $SourceRoot "skills") -Directory | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $SkillsTarget -Recurse -Force
}

foreach ($Directory in @("schemas", "workflows")) {
    $Destination = Join-Path $RuntimeTarget $Directory
    if (Test-Path -LiteralPath $Destination) {
        Remove-Item -LiteralPath $Destination -Recurse -Force
    }
    Copy-Item -LiteralPath (Join-Path $SourceRoot $Directory) -Destination $RuntimeTarget -Recurse -Force
}

Copy-Item -LiteralPath (Join-Path $SourceRoot "AGENTS.md") -Destination (Join-Path $TurboTarget "AGENTS.turbo.md") -Force
Copy-Item -LiteralPath (Join-Path $SourceRoot "scripts/doctor.py") -Destination (Join-Path $TurboTarget "doctor.py") -Force

$ProjectTarget = Join-Path $TurboTarget "project.yml"
if (-not (Test-Path -LiteralPath $ProjectTarget)) {
    Copy-Item -LiteralPath (Join-Path $SourceRoot "templates/project.yml") -Destination $ProjectTarget
    Write-Host "Created .specify/turbo/project.yml"
} else {
    Write-Host "Preserved existing .specify/turbo/project.yml"
}

$StateTarget = Join-Path $TurboTarget "state.json"
if (-not (Test-Path -LiteralPath $StateTarget)) {
    Copy-Item -LiteralPath (Join-Path $SourceRoot "templates/state.json") -Destination $StateTarget
    Write-Host "Created .specify/turbo/state.json"
} else {
    Write-Host "Preserved existing .specify/turbo/state.json"
}

$AgentsFile = Join-Path $TargetRoot "AGENTS.md"
$StartMarker = "<!-- speckit-turbo:start -->"
$EndMarker = "<!-- speckit-turbo:end -->"

if (-not (Test-Path -LiteralPath $AgentsFile)) {
    New-Item -ItemType File -Path $AgentsFile | Out-Null
}

$AgentsContent = Get-Content -LiteralPath $AgentsFile -Raw
if ($null -eq $AgentsContent) {
    $AgentsContent = ""
}

if (-not $AgentsContent.Contains($StartMarker)) {
    $Separator = if ($AgentsContent.Length -gt 0 -and -not $AgentsContent.EndsWith("`n")) { "`r`n`r`n" } elseif ($AgentsContent.Length -gt 0) { "`r`n" } else { "" }
    $ManagedBlock = @"
$StartMarker
## Spec Kit Turbo

Follow the shared rules in ``.specify/turbo/AGENTS.turbo.md`` and use the installed specialist skills under ``.agents/skills/turbo-*``.
Persist resumable workflow state in ``.specify/turbo/state.json`` and load project gates from ``.specify/turbo/project.yml``.
$EndMarker
"@
    Add-Content -LiteralPath $AgentsFile -Value ($Separator + $ManagedBlock)
    Write-Host "Added Spec Kit Turbo block to AGENTS.md"
} else {
    Write-Host "Preserved existing Spec Kit Turbo block in AGENTS.md"
}

if (-not $HadSpecify) {
    Write-Warning "No existing .specify directory was detected. Initialize GitHub Spec Kit before starting a workflow."
}

Write-Host "Installed Spec Kit Turbo into $TargetRoot"
Write-Host "Next: edit .specify/turbo/project.yml and run: python .specify/turbo/doctor.py"
