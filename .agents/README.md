# python-package-skills Agent Guide

`AGENTS.md` contains the rules that apply to every task. Use this index to load
the smallest relevant guide before editing.

## Task guides

- [Skill authoring](skills-authoring/README.md): add or change a pipeline skill, its eval, or a shared script.

The skill list lives in `README.md`. Use this tree for how to change the
repository.

## Portable skills

- `python-package-skills`: add or change a skill, eval, or shared script in this repository.

Read a skill's `SKILL.md` before using it. An agent runtime that does not
discover skills automatically can read the file directly.

## Portable settings and runtime guidance

Use [settings.json](settings.json) as the portable, machine-readable policy
manifest. It is not automatically loaded by any runtime. Follow
[runtime-guidance.md](runtime-guidance.md) for its operational explanation and
runtime-specific notes.
