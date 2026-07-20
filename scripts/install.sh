#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SOURCE_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
TARGET=${1:-.}

if [ ! -d "$TARGET" ]; then
  echo "Target directory does not exist: $TARGET" >&2
  exit 2
fi

TARGET=$(CDPATH= cd -- "$TARGET" && pwd)
HAD_SPECIFY=false
if [ -d "$TARGET/.specify" ]; then
  HAD_SPECIFY=true
fi

mkdir -p "$TARGET/.agents/skills"
mkdir -p "$TARGET/.specify/turbo/runtime"

cp -R "$SOURCE_ROOT/skills/." "$TARGET/.agents/skills/"
cp -R "$SOURCE_ROOT/schemas" "$TARGET/.specify/turbo/runtime/"
cp -R "$SOURCE_ROOT/workflows" "$TARGET/.specify/turbo/runtime/"
cp "$SOURCE_ROOT/AGENTS.md" "$TARGET/.specify/turbo/AGENTS.turbo.md"
cp "$SOURCE_ROOT/scripts/doctor.py" "$TARGET/.specify/turbo/doctor.py"
cp "$SOURCE_ROOT/scripts/validate.py" "$TARGET/.specify/turbo/validate.py"

if [ ! -f "$TARGET/.specify/turbo/project.yml" ]; then
  cp "$SOURCE_ROOT/templates/project.yml" "$TARGET/.specify/turbo/project.yml"
  echo "Created .specify/turbo/project.yml"
else
  echo "Preserved existing .specify/turbo/project.yml"
fi

if [ ! -f "$TARGET/.specify/turbo/state.json" ]; then
  cp "$SOURCE_ROOT/templates/state.json" "$TARGET/.specify/turbo/state.json"
  echo "Created .specify/turbo/state.json"
else
  echo "Preserved existing .specify/turbo/state.json"
fi

AGENTS_FILE="$TARGET/AGENTS.md"
START_MARKER='<!-- speckit-turbo:start -->'
END_MARKER='<!-- speckit-turbo:end -->'

if [ ! -f "$AGENTS_FILE" ]; then
  : > "$AGENTS_FILE"
fi

if ! grep -Fq "$START_MARKER" "$AGENTS_FILE"; then
  if [ -s "$AGENTS_FILE" ]; then
    printf '\n' >> "$AGENTS_FILE"
  fi
  cat >> "$AGENTS_FILE" <<EOF
$START_MARKER
## Spec Kit Turbo

Follow the shared rules in \`.specify/turbo/AGENTS.turbo.md\` and use the installed specialist skills under \`.agents/skills/turbo-*\`.
Persist resumable workflow state in \`.specify/turbo/state.json\` and load project gates from \`.specify/turbo/project.yml\`.
$END_MARKER
EOF
  echo "Added Spec Kit Turbo block to AGENTS.md"
else
  echo "Preserved existing Spec Kit Turbo block in AGENTS.md"
fi

if [ "$HAD_SPECIFY" = false ]; then
  echo "Warning: no existing .specify directory was detected. Initialize GitHub Spec Kit before starting a workflow." >&2
fi

echo "Installed Spec Kit Turbo into $TARGET"
echo "Next: edit .specify/turbo/project.yml and run: python .specify/turbo/doctor.py"
