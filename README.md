# python-package-skills

AI skills for Python package onboarding into Red Hat's AI package distribution pipeline (RHAI). These skills are consumed by the [agentic-ci](https://github.com/opendatahub-io/agentic-ci) Claude runner image and orchestrated by the [package-onboarding](https://gitlab.com/redhat/rhel-ai/core/package-onboarding) pipeline.

## Skills

| Skill | Description |
|---|---|
| [builder-onboarding](skills/builder-onboarding/) | Configure a Python package in the RHAI builder repository |
| [executive-summary](skills/executive-summary/) | Generate a 2-3 line executive summary of a packaging analysis |
| [failure-analysis](skills/failure-analysis/) | Analyze a Python package build failure from log output |
| [jira-context-summary](skills/jira-context-summary/) | Summarize Jira ticket context for downstream pipeline steps |
| [license-check](skills/license-check/) | Check license compatibility for redistribution |
| [packaging-investigation](skills/packaging-investigation/) | Deep investigation of a Python package for enterprise distribution |
| [pipeline-onboarding](skills/pipeline-onboarding/) | Add a package to the RHAI pipeline onboarding collection |
| [probe-test-onboarding](skills/probe-test-onboarding/) | Create probe tests for a package in the wheels-test repository |
| [security-audit](skills/security-audit/) | Run a security audit and produce a risk-rated report |
| [skill-selector](skills/skill-selector/) | Decide which packaging skill should handle a given request |

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
    +-- skills/builder-onboarding/
    +-- skills/executive-summary/
    +-- skills/failure-analysis/
    +-- skills/jira-context-summary/
    +-- skills/license-check/
    +-- skills/packaging-investigation/
    +-- skills/pipeline-onboarding/
    +-- skills/probe-test-onboarding/
    +-- skills/security-audit/
    +-- skills/skill-selector/
```

The orchestrator prepares a workspace with context files and the target repository, then invokes a skill. The skill reads its context, operates on the repo, and produces git commits or output files.

## Evals

Each skill has an eval config at the repo root (`eval-<skill>.yaml`) and test
cases under `eval/cases-<skill>/`. These check that the skill produces the
expected outputs.

Skill-selection evals live in [`eval-skill-selector.yaml`](eval-skill-selector.yaml)
and use [`skill-selector`](skills/skill-selector/) to verify the correct skill
is chosen for a given request. See
[`eval/references/control-plane-skill-selection.md`](eval/references/control-plane-skill-selection.md).

```bash
python3 eval/scripts/run_model_matrix.py eval-skill-selector.yaml
```

## Development

```bash
make lint          # Run skillsaw + ruff
make skillsaw      # Run skillsaw only
make skillsaw-fix  # Auto-fix skillsaw issues
```

## License

Apache-2.0
