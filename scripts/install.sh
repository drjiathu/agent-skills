#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_root="$repo_root/skills"
destination="${AGENT_SKILLS_DIR:-$HOME/.agents/skills}"
mode="link"

if [[ "${1:-}" == "--copy" ]]; then
  mode="copy"
  shift
fi

mkdir -p "$destination"

if (( $# > 0 )); then
  skill_names=("$@")
else
  skill_names=()
  while IFS= read -r skill_dir; do
    skill_names+=("$(basename "$skill_dir")")
  done < <(find "$source_root" -mindepth 1 -maxdepth 1 -type d | sort)
fi

for name in "${skill_names[@]}"; do
  source_path="$source_root/$name"
  target_path="$destination/$name"

  if [[ ! -f "$source_path/SKILL.md" ]]; then
    echo "error: skill not found or missing SKILL.md: $name" >&2
    exit 1
  fi

  if [[ -e "$target_path" || -L "$target_path" ]]; then
    echo "error: destination already exists: $target_path" >&2
    echo "remove or relocate it explicitly before installing" >&2
    exit 1
  fi

  if [[ "$mode" == "copy" ]]; then
    cp -R "$source_path" "$target_path"
    echo "copied $name -> $target_path"
  else
    ln -s "$source_path" "$target_path"
    echo "linked $name -> $target_path"
  fi
done

