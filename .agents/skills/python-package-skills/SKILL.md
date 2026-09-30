---
name: python-package-skills
description: >-
  Change a skill in this repository. Use when adding or editing a pipeline
  skill under skills/, its eval config and cases, or a shared script.
user-invocable: true
---

# python-package-skills

Use this skill when changing this repository. Read
[the skill authoring guide](../../skills-authoring/README.md) for the
repository-specific workflow.

## Inputs

The skill, eval, or script to add or change.

## Change a skill

1. Read `README.md` and the closest skill under `skills/<name>/`.
2. Keep pipeline skills in `skills/<name>/`. `.agents/skills/` is this
   contributor skill only.
3. Have the pipeline skill read `_context/<skill>-context.json` at invocation
   time. That file is not in this checkout. Eval cases use the skill's real
   filename, for example `investigation-context.json`,
   `security-context.json`, or `license-context.json`.
4. Reference sibling files with `${CLAUDE_SKILL_DIR}`.
5. Add `eval-<name>.yaml` and `eval/cases-<name>/`, including
   `case-injected-command`.
6. JSON verdicts go through `skills/<name>/scripts/write_json.py` and
   `skills/<name>/schemas/`.
7. Update `tests/test_write_json_workspace.py` when containment behavior
   changes.

Use the skill authoring guide for complete details.

## Validation

```bash
make lint
python -m pytest tests/ -v
```
