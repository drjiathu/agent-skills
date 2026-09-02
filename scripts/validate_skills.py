#!/usr/bin/env python3
"""Validate the repository's Agent Skills without third-party dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("must start with YAML frontmatter")

    try:
        closing = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise ValueError("frontmatter is not closed") from exc

    metadata: dict[str, str] = {}
    for line in lines[1:closing]:
        match = re.match(r"^([a-z][a-z0-9-]*):\s*(.*)$", line)
        if match:
            metadata[match.group(1)] = match.group(2).strip().strip("'\"")
    return metadata


def main() -> int:
    errors: list[str] = []
    skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
    if not skill_dirs:
        errors.append("no skill directories found")

    seen_names: set[str] = set()
    for skill_dir in skill_dirs:
        manifest = skill_dir / "SKILL.md"
        if not manifest.is_file():
            errors.append(f"{skill_dir.name}: missing SKILL.md")
            continue

        try:
            metadata = parse_frontmatter(manifest)
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"{skill_dir.name}: {exc}")
            continue

        name = metadata.get("name", "")
        description = metadata.get("description", "")
        if not NAME_RE.fullmatch(name):
            errors.append(f"{skill_dir.name}: invalid or missing frontmatter name: {name!r}")
        if name != skill_dir.name:
            errors.append(f"{skill_dir.name}: frontmatter name must match directory")
        if name in seen_names:
            errors.append(f"{skill_dir.name}: duplicate skill name")
        seen_names.add(name)
        if not description:
            errors.append(f"{skill_dir.name}: missing frontmatter description")
        elif len(description) > 1024:
            errors.append(f"{skill_dir.name}: description exceeds 1024 characters")
        if len(name) > 64:
            errors.append(f"{skill_dir.name}: name exceeds 64 characters")

    if errors:
        print("Skill validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(skill_dirs)} skill(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

