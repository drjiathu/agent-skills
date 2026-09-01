# Repository Instructions

- Follow the Agent Skills open specification.
- Keep each installable skill under `skills/<kebab-case-name>/`.
- Require `SKILL.md`; its frontmatter `name` must match the directory name.
- Make `description` state both what the skill does and when it should trigger.
- Keep the main instructions concise and move detailed material to `references/`.
- Put deterministic, reusable automation in `scripts/` and document dependencies.
- Never add credentials, private keys, internal tokens, or machine-specific secrets.
- Run `python3 scripts/validate_skills.py` before committing.
- Develop on `develop` or a Git Flow branch; reserve `main` for released content.

