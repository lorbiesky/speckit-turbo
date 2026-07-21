#!/usr/bin/env sh
set -eu

SOURCE_ROOT=${1:-.}
TARGET=${2:-.}
exec "$(CDPATH= cd -- "$SOURCE_ROOT" && pwd)/scripts/install.sh" --upgrade "$TARGET"
