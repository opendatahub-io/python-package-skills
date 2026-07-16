---
name: deterministic-commit
description: >-
  Deterministic git commit creation for onboarding steps. Handles staging,
  commit message formatting with Jira trailers, and post-linter amend loops
  programmatically — replacing prompt-driven git operations that are
  non-deterministic and frequently fail.
allowed-tools: Bash Read
metadata:
  author: ODH
  version: "1.0"
  tags: git, commit, utility, onboarding
---

# Deterministic Commit

Utility skill providing a deterministic bash script for creating git commits in onboarding workflows. This is not invoked as a standalone task — other onboarding skills call the script after completing their file changes.

## Script Location

```
${CLAUDE_SKILL_DIR}/../deterministic-commit/scripts/commit.sh
```

## Usage

```bash
bash "${CLAUDE_SKILL_DIR}/../deterministic-commit/scripts/commit.sh" \
  --ticket "AIPCC-12345" \
  --subject "AIPCC-12345: add package numpy into 'onboarding' collection" \
  --body "Summary of changes..." \
  --lint-cmd "make linter"
```

## Options

| Flag | Required | Description |
|------|----------|-------------|
| `--ticket KEY` | Yes | Jira ticket key (added as `Closes:` trailer) |
| `--subject LINE` | Yes | Full commit subject line |
| `--body TEXT` | No | Commit message body (multi-line) |
| `--body-file PATH` | No | Read body from file (overrides `--body`) |
| `--lint-cmd CMD` | No | Linter command; runs pre-commit and in post-commit amend loop |
| `--trailer "Key: Value"` | No | Additional trailer line (repeatable) |
| `--exclude PATTERN` | No | Extra git-add exclusion pathspec (repeatable) |

## Behavior

1. Runs the linter (if `--lint-cmd` is given) to catch auto-fixes before staging
2. Stages all changes with `git add -A -- . :!_run` (plus any `--exclude` patterns)
3. Builds the commit message: subject + body + trailers + `Closes: <ticket>`
4. Creates the commit
5. Runs a post-commit linter-amend loop (up to 3 passes) if `--lint-cmd` is given
6. Verifies the working tree is clean
7. Prints the commit hash and message for verification
