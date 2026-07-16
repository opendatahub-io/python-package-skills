# python-package-skills

AI skills for Python package onboarding into Red Hat's AI package distribution pipeline (RHAI). These skills are consumed by the [agentic-ci](https://github.com/opendatahub-io/agentic-ci) Claude runner image and orchestrated by the [package-onboarding](https://gitlab.com/redhat/rhel-ai/core/package-onboarding) pipeline.

## Skills

| Skill | Description |
|---|---|
| [builder-onboarding](skills/builder-onboarding/) | Configure a Python package in the RHAI builder repository |
| [deterministic-commit](skills/deterministic-commit/) | Deterministic git commit with staging, message formatting, and trailers |
| [executive-summary](skills/executive-summary/) | Generate a 2-3 line executive summary of a packaging analysis |
| [failure-analysis](skills/failure-analysis/) | Analyze a Python package build failure from log output |
| [jira-context-summary](skills/jira-context-summary/) | Summarize Jira ticket context for downstream pipeline steps |
| [license-check](skills/license-check/) | Check license compatibility for redistribution |
| [packaging-investigation](skills/packaging-investigation/) | Deep investigation of a Python package for enterprise distribution |
| [pipeline-onboarding](skills/pipeline-onboarding/) | Add a package to the RHAI pipeline onboarding collection |
| [probe-test-onboarding](skills/probe-test-onboarding/) | Create probe tests for a package in the wheels-test repository |
| [security-audit](skills/security-audit/) | Run a security audit and produce a risk-rated report |

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
    +-- skills/deterministic-commit/   (utility: commit script for onboarding skills)
    +-- skills/executive-summary/
    +-- skills/failure-analysis/
    +-- skills/jira-context-summary/
    +-- skills/license-check/
    +-- skills/packaging-investigation/
    +-- skills/pipeline-onboarding/
    +-- skills/probe-test-onboarding/
    +-- skills/security-audit/
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
