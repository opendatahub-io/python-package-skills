# Skill Authoring

How to add or change a pipeline skill in this repository. The skill list stays
in `README.md`. Human contribution steps stay in `CONTRIBUTING.md`.

The invocable skill is
[`.agents/skills/python-package-skills/SKILL.md`](../skills/python-package-skills/SKILL.md).

## Setup

Python 3.11+ and `uv` (which provides `uvx`). CI runs Python 3.13.
The validation commands below use isolated tool environments; no local
`pip install` step is needed.

## Execution

Copy the closest existing skill under `skills/`. The skills-registry marketplace
entry for this plugin sets no `skills` path, so the installer only picks up
`skills/`, `.claude/skills/`, and `.opencode/skills/`.

| Piece | Path |
|-------|------|
| Prompt | `skills/<name>/SKILL.md` |
| Output contract | `skills/<name>/references/output-format.md` |
| JSON schema | `skills/<name>/schemas/` |
| JSON writer | `skills/<name>/scripts/write_json.py` |
| Eval config | `eval-<name>.yaml` |
| Eval cases | `eval/cases-<name>/` |
| Plugin manifest | `.claude-plugin/plugin.json` |

`name` in `SKILL.md` matches the directory. The pipeline skill reads
`_context/<skill>-context.json` when the orchestrator runs it. That file is
not in this checkout. Eval cases use the skill's real filename, for example
`investigation-context.json`, `security-context.json`, or
`license-context.json`. Sibling files use `${CLAUDE_SKILL_DIR}`.

`license-check`, `hardware-variant`, `packaging-investigation`, and
`security-audit` validate JSON with that skill's `scripts/write_json.py`.
The schema path is under `${CLAUDE_SKILL_DIR}` and is not limited to the
working directory.

Eval cases need `input.yaml`, `annotations.yaml`, and
`_context/<skill>-context.json`. Include `case-injected-command`. Seed files
use a `.fixture` suffix. Start from `eval/references/eval-template.yaml` and
`eval/references/cross-cutting-judges.md`.

Fondue combined-mode cases include the collection-integration guide, the root
job matrix, and existing builder lane directories. Successful cases declare
`expected_builder_placements` as exact `collection/variant` pairs; the eval
checks every target-package requirement against those pairs. Run the fixture
and judge checks with
`uvx --with pyyaml pytest tests/test_fondue_builder_placement.py -q`.

`tests/test_write_json_workspace.py` loads the `packaging-investigation` and
`security-audit` writers. Extend that list when another writer's containment
changes.

## Validation

```bash
uvx skillsaw
uvx ruff check .
uvx ruff format --check --diff .
uvx --with jsonschema --with pyyaml pytest tests/ -q
```

## Troubleshooting

| Symptom | Where to look |
|---------|----------------|
| Skill missing from the runner | Directory is not under `skills/`, `.claude/skills/`, or `.opencode/skills/` |
| `write_json` rejects the output path | `license-check` and `hardware-variant` allow the working directory only. `packaging-investigation` and `security-audit` also allow `/workspace` when `AGENT_TOOL` is `claude` or `opencode`; `codex` stays on the working directory |
| Schema path rejected | Do not apply the workspace check to `${CLAUDE_SKILL_DIR}/schemas/` |
| Injected command appears in the output | `eval/cases-<name>/case-injected-command/` and the skill's Authority section |
| Eval still sees `*.fixture` | SessionStart command in `eval/references/eval-template.yaml` |

## Escalation

- Merge review: GitHub pull request on `opendatahub-io/python-package-skills`
- Runner discovery or `${CLAUDE_SKILL_DIR}`: package-onboarding and agentic-ci
- Marketplace skills path: `opendatahub-io/skills-registry` `.claude-plugin/marketplace.json`
