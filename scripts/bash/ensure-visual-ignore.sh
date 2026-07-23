#!/usr/bin/env sh
set -eu

project_root=${1:-.}
gitignore="$project_root/.gitignore"
start='# speckit-turbo:visual-references:start'
end='# speckit-turbo:visual-references:end'
rule='.specify/visual-references/'

if [ -f "$gitignore" ] && grep -Fq "$start" "$gitignore" && ! grep -Fq "$end" "$gitignore"; then
  echo "Spec Kit Turbo visual ignore block is corrupted in $gitignore" >&2
  exit 1
fi

if [ -f "$gitignore" ] && grep -Fq "$end" "$gitignore" && ! grep -Fq "$start" "$gitignore"; then
  echo "Spec Kit Turbo visual ignore block is corrupted in $gitignore" >&2
  exit 1
fi

if [ -f "$gitignore" ] && grep -Fq "$start" "$gitignore"; then
  exit 0
fi

{
  [ -f "$gitignore" ] && [ -s "$gitignore" ] && printf '\n'
  printf '%s\n%s\n%s\n' "$start" "$rule" "$end"
} >> "$gitignore"

git -C "$project_root" check-ignore -q .specify/visual-references/.speckit-turbo-probe
