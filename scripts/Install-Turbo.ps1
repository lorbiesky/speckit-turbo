param(
    [string]$ProjectRoot = "."
)

$ErrorActionPreference = "Stop"
$extensionCatalog = "https://raw.githubusercontent.com/lorbiesky/speckit-turbo/main/catalogs/extensions.json"
$workflowCatalog = "https://raw.githubusercontent.com/lorbiesky/speckit-turbo/main/catalogs/workflows.json"
$bundleCatalog = "https://raw.githubusercontent.com/lorbiesky/speckit-turbo/main/catalogs/bundles.json"
$specify = Get-Command specify -ErrorAction SilentlyContinue

if (-not $specify) {
    throw "Spec Kit is required. Install Specify CLI first: https://github.com/github/spec-kit"
}

Push-Location (Resolve-Path $ProjectRoot)
try {
    $versionText = (& specify version 2>&1 | Out-String)
    if ($versionText -notmatch '0\.(1[1-9]|[2-9][0-9])\.') {
        throw "Spec Kit >=0.11.4 is required. Run: specify self upgrade"
    }

    $extensionConfig = ".specify/extension-catalogs.yml"
    $workflowConfig = ".specify/workflow-catalogs.yml"
    $bundleConfig = ".specify/bundle-catalogs.yml"
    if (-not (Test-Path $extensionConfig) -or -not (Select-String -Path $extensionConfig -Pattern [regex]::Escape($extensionCatalog) -Quiet)) {
        & specify extension catalog add $extensionCatalog --name speckit-turbo --install-allowed
    }
    if (-not (Test-Path $workflowConfig) -or -not (Select-String -Path $workflowConfig -Pattern [regex]::Escape($workflowCatalog) -Quiet)) {
        & specify workflow catalog add $workflowCatalog --name speckit-turbo
    }
    if (-not (Test-Path $bundleConfig) -or -not (Select-String -Path $bundleConfig -Pattern [regex]::Escape($bundleCatalog) -Quiet)) {
        & specify bundle catalog add $bundleCatalog --id speckit-turbo --policy install-allowed
    }

    $workflowIds = @("turbo-feature", "turbo-bugfix", "turbo-refactor", "turbo-maintenance", "turbo-hotfix", "turbo-discovery", "turbo-constitution")
    $installedWorkflows = (& specify workflow list 2>&1 | Out-String)
    foreach ($workflowId in $workflowIds) {
        if ($installedWorkflows -notmatch "\($([regex]::Escape($workflowId))\)") {
            & specify workflow add $workflowId
        }
    }

    & specify bundle install speckit-turbo
    if ((& specify extension list 2>&1 | Out-String) -notmatch "turbo") {
        throw "Spec Kit Turbo was not registered after installation."
    }
    Write-Output "Spec Kit Turbo instalado com sucesso."
}
finally {
    Pop-Location
}
