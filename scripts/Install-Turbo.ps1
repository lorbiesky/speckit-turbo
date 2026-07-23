param(
    [string]$ProjectRoot = "."
)

$ErrorActionPreference = "Stop"
$repositoryRoot = "https://raw.githubusercontent.com/lorbiesky/speckit-turbo/v2.0.3"
$extensionCatalog = "$repositoryRoot/catalogs/extensions.json"
$workflowCatalog = "$repositoryRoot/catalogs/workflows.json"
$bundleCatalog = "$repositoryRoot/catalogs/bundles.json"
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
    function Ensure-ManagedCatalog([string]$Kind, [string]$CatalogUrl, [string]$ConfigPath, [string]$CatalogFile, [string[]]$CatalogArguments) {
        if (Test-Path $ConfigPath) {
            $content = Get-Content -Raw $ConfigPath
            if ($content.Contains($CatalogUrl)) { return }
            $pattern = "https://raw\.githubusercontent\.com/lorbiesky/speckit-turbo/(main|v[^/]+)/catalogs/$([regex]::Escape($CatalogFile))"
            if ($content -match $pattern) {
                [System.IO.File]::WriteAllText((Resolve-Path $ConfigPath), [regex]::Replace($content, $pattern, $CatalogUrl))
                return
            }
        }
        & specify $Kind catalog add $CatalogUrl @CatalogArguments
    }

    Ensure-ManagedCatalog "extension" $extensionCatalog $extensionConfig "extensions.json" @("--name", "speckit-turbo", "--install-allowed")
    Ensure-ManagedCatalog "workflow" $workflowCatalog $workflowConfig "workflows.json" @("--name", "speckit-turbo")
    Ensure-ManagedCatalog "bundle" $bundleCatalog $bundleConfig "bundles.json" @("--id", "speckit-turbo", "--policy", "install-allowed")

    $workflowIds = @("turbo-feature", "turbo-bugfix", "turbo-refactor", "turbo-maintenance", "turbo-hotfix", "turbo-discovery", "turbo-constitution")
    foreach ($workflowId in $workflowIds) {
        # `workflow update` prompts for confirmation. Catalog add is idempotent
        # and refreshes only the managed workflow asset.
        & specify workflow add $workflowId
    }

    if ((& specify extension list 2>&1 | Out-String) -match "turbo") {
        # Preserve local extension configuration while refreshing managed files.
        & specify extension add turbo --force
    }
    else {
        & specify extension add turbo
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
