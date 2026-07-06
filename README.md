# python-package-skills

AI skills for Python package onboarding into Red Hat's AI package distribution pipeline (RHAI). These skills are consumed by the [agentic-ci](https://github.com/opendatahub-io/agentic-ci) Claude runner image and orchestrated by the [package-onboarding](https://gitlab.com/redhat/rhel-ai/core/package-onboarding) pipeline.

## Skills

| Skill | Description |
|---|---|
| [builder-onboarding](skills/builder-onboarding/) | Configure a Python package in the RHAI builder repository |
| [probe-test-onboarding](skills/probe-test-onboarding/) | Create probe tests for a Python package in the wheels-test repository |

## Architecture

```text
package-onboarding pipeline (orchestrator)
    |
    v
agentic-ci Claude runner (container)
    |
    v
python-package-skills (this repo, mounted as plugin)
    |
    +-- skills/builder-onboarding/SKILL.md
    +-- skills/...
```

The orchestrator prepares a workspace with context files and the target repository, then invokes a skill. The skill reads its context, operates on the repo, and produces git commits or output files.

## Development

```bash
make lint          # Run skillsaw + ruff
make skillsaw      # Run skillsaw only
make skillsaw-fix  # Auto-fix skillsaw issues
```

## License

Apache-2.0
