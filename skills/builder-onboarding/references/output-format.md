# builder-onboarding output format

This document defines the output contract for the builder-onboarding skill.
The output is a git commit (not a file). The builder CI pipeline reads the
committed configuration files to build the package wheels.

## Output artifact

A single git commit on the builder repository working tree. The commit contains
configuration file changes that add a new Python package to the builder
collection. The working tree must be clean after the commit (no uncommitted
changes, no staged `_run/` directory).

## Commit message format

```
<builder_ticket>: add <package_name>

<Body describing what was added, which variant(s), and the build strategy.
If transitive dependencies were identified but not configured, list them
in a "Transitive dependencies:" section, one per line.>

Closes: <builder_ticket>
```

- **Subject**: `<builder_ticket>: add <package_name>` -- follows AGENTS.md
  rules for commit message format.
- **Body**: one or more lines describing the change. Mention the collection
  variant (CPU, CUDA, ROCm), the build strategy (source or pre-built), and
  any notable configuration details.
- **Trailer**: `Closes: <builder_ticket>` as the last line.

## Expected file changes

- Configuration files added or modified in collection variant directories.
- The package is added to the collection with the highest (most recent) torch
  version. No new collections are created.

## Build strategy

| Strategy | When to use |
|----------|-------------|
| Source | Default. Always attempt source-based building first. Covers pure-Python packages, packages with C extensions where build deps are available, and packages with Fortran/Rust extensions. |
| Pre-built | Last resort only. Use when source building has been attempted and proven impossible (e.g., proprietary code, missing unreproducible build environment, binary-only distribution). |

## Variant placement

| Variant | When to include |
|---------|-----------------|
| CPU | Always. Every package gets added to the CPU variant. |
| CUDA | Only when the package depends on the CUDA toolkit or has CUDA-specific build output (e.g., GPU kernels, cuDNN bindings). |
| ROCm | Only when the package depends on ROCm libraries or has ROCm-specific build output. |

## Constraints

- Only one package per commit. Transitive dependencies are listed in the commit
  body but not configured; each dependency is onboarded in its own pipeline run.
- The `_run/` directory must never be staged. Use `git add -A -- . :!_run`.
- All changes must pass `make linter` before the final commit.
- All AGENTS.md rules (architecture-specific exclusions, platform markers,
  commit format) must be followed.
- No unrelated files may be modified.

## Example

For a pure-Python package `text-utils`, the commit would:

**Commit message:**

```
AIPCC-99001: add text-utils

Add text-utils package to CPU variant. Pure Python package with no native
dependencies. Source-based build configured.

Closes: AIPCC-99001
```

**Files changed** (example paths vary by repository structure):

```
collections/<torch-version>/cpu/packages/text-utils.yaml
```

**Example config file content:**

```yaml
name: text-utils
build_strategy: source
```

Note: The exact config file format depends on the repository's AGENTS.md.
This example is illustrative.

## Validation rules

- Exactly one commit must be produced.
- The commit subject must match `<builder_ticket>: add <package_name>` or
  follow AGENTS.md format.
- The commit must include a `Closes: <builder_ticket>` trailer.
- The working tree must be clean after committing (`git status --porcelain`
  returns empty).
- No files from the `_run/` directory may appear in the commit.
- The package must appear only in the CPU variant unless it has accelerator
  dependencies.
- `make linter` must pass with no errors after the final commit (enforced indirectly via working_tree_clean in evals; linters auto-fix files, so a dirty tree signals linter failure).
- No configuration for transitive dependencies may be included.

## Downstream consumers

- **Builder CI pipeline**: reads the committed configuration files to build
  the package wheels. The pipeline uses the collection variant directories
  and package configuration to determine build parameters, target
  architectures, and dependency resolution.
