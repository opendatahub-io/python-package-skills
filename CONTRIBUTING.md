# Contributing to python-package-skills

Thank you for your interest in contributing to python-package-skills! This repository provides AI skills for Python package onboarding into the RHAI pipeline.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/<your-username>/python-package-skills.git
   cd python-package-skills
   ```
3. **Create a branch** for your work:
   ```bash
   git checkout -b my-change
   ```

## Repository Layout

```text
skills/                      Skill directories (SKILL.md + references/)
  <skill-name>/
    SKILL.md                 Frontmatter + prompt body
    references/              Templates, schemas, output format docs
eval/                        Eval test case directories
  cases-<skill-name>/        Test cases per skill
eval-<skill-name>.yaml       Eval configs at repo root
hooks/                       Claude Code event hooks
scripts/                     Shared scripts
```

Read [AGENTS.md](AGENTS.md) for architecture details and conventions.

## Ways to Contribute

- **Add or improve a skill** in `skills/<skill-name>/`
- **Add eval cases and judges** for existing skills
- **Fix a bug** or improve existing functionality
- **Improve documentation** or reference materials

## Development Setup

### Prerequisites

- **Python 3.10+** with [ruff](https://docs.astral.sh/ruff/) (`pip install ruff`)
- **[skillsaw](https://skillsaw.org/)** (`pip install skillsaw` or use via `uvx skillsaw`)
- **Git**

### Validate Your Changes

Before submitting, always run:

```bash
make lint
```

The `lint` target runs:
- **skillsaw** validates skill frontmatter, structure, and content quality
- **ruff check** checks Python code for errors
- **ruff format** verifies Python code formatting

### Skill Structure

Each skill lives in `skills/<name>/` and must contain:

- `SKILL.md` with YAML frontmatter (`name`, `description`, `allowed-tools`, `metadata`) and a markdown prompt body
- An "Authority and Data Boundaries" section in the prompt
- `references/output-format.md` documenting the output contract

Optional directories:
- `scripts/` for executable scripts the skill invokes
- `references/` for templates, schemas, and reference docs

### Eval Structure

Each skill should have a corresponding eval config (`eval-<skill-name>.yaml`) and test cases (`eval/cases-<skill-name>/`).

Each test case directory contains:
- `input.yaml` with the skill reference and configuration
- `annotations.yaml` with expected values and test metadata
- `_context/` with the context JSON the skill reads
- `*.fixture` files for workspace setup (optional)

## Submitting Your Contribution

1. **Run validation** before committing:
   ```bash
   make lint
   ```
2. **Commit your changes** with a clear, descriptive commit message.
3. **Push to your fork** and open a Pull Request against `main`.
4. **Fill out the PR description** with a summary and test plan.

### Commit Messages

Write concise commit messages that explain *why* the change was made:

- `feat:` for new skills or features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `chore:` for maintenance tasks

Example: `feat: add eval cases for failure-analysis skill`

## Pull Request Process

1. **All PRs must pass CI checks**, including `make lint`.
2. **At least one maintainer review** is required before merging.
3. **Keep PRs focused**: one skill or logical change per PR.

## Style and Conventions

### Naming

- Use lowercase kebab-case for skill names: `failure-analysis`, `builder-onboarding`
- Skill names follow the `<domain>-<action>` pattern

### Python

- Format with `ruff format`
- Pass `ruff check` with no errors
- Use Python 3.10+ type annotations

### Skills

- Each skill is self-contained: everything needed is in the skill directory
- Context is passed via JSON files in `/workspace/_context/`, not template variable substitution
- Every SKILL.md must include `metadata.x-artifacts` declaring files/dirs the skill creates
- Skills reference sibling files via `${CLAUDE_SKILL_DIR}`

## Code of Conduct

We are committed to providing a welcoming and respectful environment for everyone. Be kind, constructive, and professional in all interactions.

## Getting Help

- **Questions?** Open an [issue](https://github.com/opendatahub-io/python-package-skills/issues/new) or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).
