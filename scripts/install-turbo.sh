#!/usr/bin/env sh
# Spec Kit Turbo bootstrap installer.
# This file intentionally downloads no repository: it delegates component
# resolution and installation to the native Specify CLI.
set -eu

REPOSITORY_ROOT="https://raw.githubusercontent.com/lorbiesky/speckit-turbo/main"
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

add_catalog_once() {
  catalog_kind="$1"
  catalog_url="$2"
  catalog_config="$3"
  shift 3
  if [ -f "$catalog_config" ] && grep -Fq "$catalog_url" "$catalog_config"; then
    return 0
  fi
  "$SPECIFY_BIN" "$catalog_kind" catalog add "$catalog_url" "$@"
}

add_catalog_once extension "$EXTENSION_CATALOG" .specify/extension-catalogs.yml --name speckit-turbo --install-allowed
add_catalog_once workflow "$WORKFLOW_CATALOG" .specify/workflow-catalogs.yml --name speckit-turbo
add_catalog_once bundle "$BUNDLE_CATALOG" .specify/bundle-catalogs.yml --id speckit-turbo --policy install-allowed

for workflow_id in turbo-feature turbo-bugfix turbo-refactor turbo-maintenance turbo-hotfix turbo-discovery turbo-constitution; do
  if ! "$SPECIFY_BIN" workflow list 2>/dev/null | grep -Fq "($workflow_id)"; then
    "$SPECIFY_BIN" workflow add "$workflow_id"
  fi
done

"$SPECIFY_BIN" bundle install speckit-turbo
"$SPECIFY_BIN" extension list | grep -Fq 'turbo'
printf '%s\n' 'Spec Kit Turbo instalado com sucesso.'
