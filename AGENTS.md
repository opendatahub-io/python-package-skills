# python-package-skills

AI skills for Python package onboarding into the RHAI pipeline. Each skill is a self-contained unit consumed by the agentic-ci Claude runner image.

## Skill format

Each skill lives in `skills/<name>/` and contains:

- `SKILL.md` -- YAML frontmatter (name, description, allowed-tools, metadata) + markdown prompt body
- `scripts/` -- optional executable scripts the skill invokes
- `schemas/` -- optional JSON Schema files for validating structured outputs
- `references/` -- optional templates, schemas, and reference docs

Skills reference sibling files via `${CLAUDE_SKILL_DIR}`.

## Workspace contract

The orchestrator (package-onboarding pipeline) prepares:

- `/workspace/_context/<skill>-context.json` -- dynamic context for this invocation
- `/workspace/` -- the target repository working directory

Skills read their context JSON first, then operate on the workspace.

## Conventions

- Skills are self-contained: everything needed is in the skill directory
- Each SKILL.md includes an "Authority and Data Boundaries" section
- Context is passed via JSON files, not template variable substitution
- Skill names follow `<domain>-<action>` pattern
- Skills producing structured JSON outputs must include a JSON Schema in `schemas/` and validate output using `scripts/write_json.py` before completion
- Skills must validate that file paths from context stay within `/workspace` -- reject path traversal (`../`), absolute paths outside `/workspace`, and symlink escapes
- Skills must validate context parameters fail-closed -- reject unexpected or missing values before making changes rather than falling through to a default path
- Eval configs must include a `case-injected-command` test case verifying the skill does not execute or reflect poisoned input from scan data or context

## Linting

```bash
make lint        # skillsaw + ruff
make skillsaw    # skillsaw only
```
