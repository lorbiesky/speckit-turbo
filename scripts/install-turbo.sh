#!/usr/bin/env sh
# Spec Kit Turbo bootstrap installer.
# This file intentionally downloads no repository: it delegates component
# resolution and installation to the native Specify CLI.
set -eu

REPOSITORY_ROOT="https://raw.githubusercontent.com/lorbiesky/speckit-turbo/v2.0.3"
EXTENSION_CATALOG="$REPOSITORY_ROOT/catalogs/extensions.json"
WORKFLOW_CATALOG="$REPOSITORY_ROOT/catalogs/workflows.json"
BUNDLE_CATALOG="$REPOSITORY_ROOT/catalogs/bundles.json"
PROJECT_PATH="${1:-.}"
SPECIFY_BIN="${SPECIFY_BIN:-specify}"

if [ "$#" -gt 1 ]; then
  printf '%s\n' 'Usage: install-turbo.sh [project-directory]' >&2
  exit 2
fi

if ! command -v "$SPECIFY_BIN" >/dev/null 2>&1; then
  printf '%s\n' 'Spec Kit is required. Install Specify CLI first: https://github.com/github/spec-kit' >&2
  exit 1
fi

cd "$PROJECT_PATH"

specify_version="$($SPECIFY_BIN version 2>&1 || true)"
case "$specify_version" in
  *"0.11."*|*"0.12."*|*"0.13."*|*"0.14."*|*"0.15."*|*"0.16."*|*"0.17."*|*"0.18."*|*"0.19."*|*"0.20."*) ;;
  *)
    printf '%s\n' 'Spec Kit >=0.11.4 is required. Run: specify self upgrade' >&2
    exit 1
    ;;
esac

ensure_managed_catalog() {
  catalog_kind="$1"
  catalog_url="$2"
  catalog_config="$3"
  catalog_file="$4"
  shift 4
  if [ -f "$catalog_config" ] && grep -Fq "$catalog_url" "$catalog_config"; then
    return 0
  fi
  if [ -f "$catalog_config" ] && grep -Fq 'raw.githubusercontent.com/lorbiesky/speckit-turbo/' "$catalog_config" && grep -Fq "/catalogs/$catalog_file" "$catalog_config"; then
    temporary_config="${catalog_config}.turbo-update.$$"
    sed "s|https://raw.githubusercontent.com/lorbiesky/speckit-turbo/[^[:space:]]*/catalogs/$catalog_file|$catalog_url|g" "$catalog_config" > "$temporary_config"
    mv "$temporary_config" "$catalog_config"
    return 0
  fi
  "$SPECIFY_BIN" "$catalog_kind" catalog add "$catalog_url" "$@"
}

ensure_managed_catalog extension "$EXTENSION_CATALOG" .specify/extension-catalogs.yml extensions.json --name speckit-turbo --install-allowed
ensure_managed_catalog workflow "$WORKFLOW_CATALOG" .specify/workflow-catalogs.yml workflows.json --name speckit-turbo
ensure_managed_catalog bundle "$BUNDLE_CATALOG" .specify/bundle-catalogs.yml bundles.json --id speckit-turbo --policy install-allowed

for workflow_id in turbo-feature turbo-bugfix turbo-refactor turbo-maintenance turbo-hotfix turbo-discovery turbo-constitution; do
  # `workflow update` asks for interactive confirmation. Adding a catalog
  # workflow is idempotent and replaces only that managed workflow asset.
  "$SPECIFY_BIN" workflow add "$workflow_id"
done

if "$SPECIFY_BIN" extension list 2>/dev/null | grep -Fq 'turbo'; then
  # Keep project configuration while refreshing the extension's managed files.
  "$SPECIFY_BIN" extension add turbo --force
else
  "$SPECIFY_BIN" extension add turbo
fi
"$SPECIFY_BIN" bundle install speckit-turbo
"$SPECIFY_BIN" extension list | grep -Fq 'turbo'
printf '%s\n' 'Spec Kit Turbo instalado com sucesso.'
