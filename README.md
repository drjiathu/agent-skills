# Agent Skills

Personal, reusable Agent Skills maintained as a single source of truth for
Codex and other clients that support the open Agent Skills format.

## Skills

| Skill | Purpose |
| --- | --- |
| `python-wheel-release` | Build, validate, and publish traceable Python wheel releases. |
| `systemd-wheel-deploy` | Deploy and roll back validated Python wheel releases with systemd. |

## Layout

```text
skills/<skill-name>/
├── SKILL.md
├── agents/       # Optional client metadata
├── scripts/      # Optional deterministic helpers
├── references/   # Optional on-demand documentation
└── assets/       # Optional templates and static resources
```

Each skill name uses lowercase kebab-case and must match its directory name.
`SKILL.md` contains YAML frontmatter with at least `name` and `description`.

## Install

Install every skill into the cross-client user directory with symlinks:

```bash
./scripts/install.sh
```

Install selected skills:

```bash
./scripts/install.sh python-wheel-release systemd-wheel-deploy
```

Use independent copies instead of symlinks:

```bash
./scripts/install.sh --copy
```

Override the destination when needed:

```bash
AGENT_SKILLS_DIR="$HOME/.agents/skills" ./scripts/install.sh
```

Restart the agent after installing or changing skills if it discovers skills
only at startup.

## Validate

```bash
python3 scripts/validate_skills.py
```

The same validation runs in GitHub Actions for pushes and pull requests.

## Development

This repository uses Git Flow:

- `main`: released and deployable skill versions
- `develop`: integrated development
- `feature/*`: new skills and substantial changes
- `release/*`: release preparation
- `hotfix/*`: urgent fixes based on `main`

Do not commit credentials, private keys, host-specific secrets, logs, or
generated runtime state. Keep third-party skills separate until their source,
license, scripts, and instructions have been reviewed.

## References

- [Agent Skills specification](https://agentskills.io/specification)
- [OpenAI Plugins](https://github.com/openai/plugins)

