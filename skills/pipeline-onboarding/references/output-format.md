# pipeline-onboarding output format

This document defines the output contract for the pipeline-onboarding skill.
The output is a git commit containing requirements files that add a package
to the onboarding collection across all pipeline variants.

## Output artifact

A single git commit in the pipeline repository. The commit includes one
requirements file per variant directory under `collections/onboarding/`.
The working tree must be clean after the commit (no uncommitted changes,
no staged `_run/` directory).

## Commit message format

```
<pipeline_ticket>: add package <package_name> into 'onboarding' collection

<summary from context>

Closes: <pipeline_ticket>
```

- **Subject**: `<pipeline_ticket>: add package <package_name> into 'onboarding' collection` (exactly this format).
- **Body**: the `summary` field from the context JSON. If `builder_mr_dependency`
  is non-empty, include it in the body as well. If transitive dependencies are
  identified that are not already configured in the repository, list them in a
  "Transitive dependencies:" section, one per line.
- **Trailer**: `Closes: <pipeline_ticket>` as the last line.
- Additional commit format rules from the repository's AGENTS.md also apply.

## Requirements file format

One file per variant at `collections/onboarding/<variant>/requirements/<package_name>.txt`.

Each file contains exactly one line:

- **Pinned version**: `<package_name>==<package_version>  <requirements_comment>`
- **Unpinned**: `<package_name>  <requirements_comment>`

The `requirements_comment` value comes from the context JSON and is appended
after the package specifier, separated by two spaces. No extra newlines, no
additional packages, no blank lines.

### Example

```
text-utils==1.2.0  # AIPCC-99010
```

### Example (unpinned version)

When `package_version` is empty:

```
text-utils  # AIPCC-99010
```

## Constraints

- **All variants**: a requirements file must be created for EVERY directory
  under `collections/onboarding/`, not just CPU or a subset.
- **Single package only**: only the package from the context is added. Transitive
  dependencies are never included in the requirements files.
- **Clean working tree**: after the commit, `git status` must show no
  uncommitted changes.
- **No `_run/` directory**: the `_run/` directory (runtime telemetry) must
  never be staged or committed.
- **Linting**: `make linter` must pass after the final commit. If the linter
  modifies files, the commit is amended until the tree is clean.

## Validation rules

- Exactly one commit must be produced.
- The commit subject must exactly match `<pipeline_ticket>: add package <package_name> into 'onboarding' collection`.
- The commit must include a `Closes: <pipeline_ticket>` trailer.
- The working tree must be clean after committing (`git status --porcelain` returns empty).
- No files from the `_run/` directory may appear in the commit.
- A requirements file must exist at `collections/onboarding/<variant>/requirements/<package_name>.txt` for every variant directory.
- Each requirements file must contain exactly one line with the package specifier and tracking comment.
- If `package_version` is non-empty, the specifier must use `==` pinning.
- `make linter` must pass with no errors after the final commit (enforced indirectly via working_tree_clean in evals; linters auto-fix files, so a dirty tree signals linter failure).

## Downstream consumers

- **Pipeline CI**: reads the requirements files from `collections/onboarding/`
  to install and test the package across all variant environments (CPU, CUDA,
  ROCm, and others). Each variant directory is processed independently, so
  missing a variant causes that environment to skip the package entirely.
