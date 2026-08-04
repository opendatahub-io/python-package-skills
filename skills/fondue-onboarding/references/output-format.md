# fondue-onboarding output format

This document defines the output contract for the fondue-onboarding skill.
The output is one or two git commits in the fondue monorepo (not a file).
Downstream CI reads the committed configuration under `builder/` and/or
`rhai-pipeline/`.

## Output artifact

| Mode | Commits | Subtrees touched |
|------|---------|------------------|
| `pipeline-only` | Exactly 1 | `rhai-pipeline/` only |
| `combined` | Exactly 2 | First: `builder/` (and optionally `.gitlab-triggers.yaml`); second: `rhai-pipeline/` |

The working tree must be clean after the final commit (no uncommitted changes,
no staged `_run/` directory).

## Builder commit (combined mode only)

### Commit message format

```
<ticket>: add <package_name>

<Body describing what was added, which variant(s), and the build strategy.
If transitive dependencies were identified but not configured, list them
in a "Transitive dependencies:" section, one per line.>

Relates-to: <ticket>
```

- **Subject**: follows AGENTS.md rules (typically `<ticket>: add <package_name>`).
- **Body**: mention the collection variant (CPU, CUDA, ROCm), build strategy
  (source or pre-built), and notable configuration details.
- **Trailer**: `Relates-to: <ticket>` as the last line (not `Closes`).

### Expected file changes

- Configuration under `builder/` (collections, plugins, overrides, settings as needed).
- Optionally `.gitlab-triggers.yaml` when required for the package.
- Package is added to the active torch collection (directory under
  `builder/collections/torch-*` whose `cpu-ubi9/constraints.txt` contains a
  `torch==` pin). Prefer the highest version that meets that rule. No new
  collections are created.

### Build strategy

| Strategy | When to use |
|----------|-------------|
| Source | Default. Always attempt source-based building first. |
| Pre-built | Last resort only, after source building is proven impossible. |

### Variant placement (builder)

| Variant | When to include |
|---------|-----------------|
| CPU | Always. Every package gets added to the CPU variant. |
| CUDA | Only when the package depends on the CUDA toolkit or has CUDA-specific build output. |
| ROCm | Only when the package depends on ROCm libraries or has ROCm-specific build output. |

### Staging

`make linter` auto-generates `.gitlab-triggers.yaml` (via `make regen` / `regen-ci.py`) whenever `builder/` collections change. Do not create that file by hand. After lint exits 0:

```bash
git add -A -- builder/ .gitlab-triggers.yaml :!_run
```

Always include `.gitlab-triggers.yaml` in the builder commit. Do not stage `rhai-pipeline/` in the builder commit.

## RHAI-pipeline commit (always)

### Commit message format

```text
<ticket>: add package <package_name> into 'onboarding' collection

<summary from context>

Closes: <ticket>
```

- **Subject**: exactly `<ticket>: add package <package_name> into 'onboarding' collection`.
- **Body**: the `summary` field from the context JSON. If transitive dependencies
  are identified that are not already configured, list them in a
  "Transitive dependencies:" section, one per line (pipeline-only mode only for
  this listing when there is no builder commit; in combined mode prefer listing
  them on the builder commit).
- **Trailer**: `Closes: <ticket>` as the last line.

### Requirements file format

One file per variant at
`rhai-pipeline/collections/onboarding/<variant>/requirements/<package_name>.txt`.

Each file contains exactly one line:

- **Pinned version**: `<package_name>==<package_version>  <requirements_comment>`
- **Unpinned**: `<package_name>  <requirements_comment>`

### Staging

```bash
git add -A -- rhai-pipeline/ :!_run
```

## Constraints

- Only one package per onboarding run. Transitive dependencies are listed in a
  commit body but not configured.
- The `_run/` directory must never be staged.
- All changes must pass `make linter` before the final commit(s).
- All AGENTS.md rules (architecture-specific exclusions, platform markers,
  commit format) must be followed.
- No unrelated files may be modified.
- In combined mode, builder and rhai-pipeline changes must be in separate commits.

## Validation rules

- Commit count must match mode (1 for pipeline-only, 2 for combined).
- The rhai-pipeline commit (last commit) must include a `Closes: <ticket>` trailer.
- In combined mode, the builder commit must include a `Relates-to: <ticket>` trailer.
- The working tree must be clean after committing (`git status --porcelain` empty).
- No files from `_run/` may appear in any commit.
- A requirements file must exist for every variant under
  `rhai-pipeline/collections/onboarding/`.
- Each requirements file must contain exactly one line with the package specifier
  and tracking comment.
- In combined mode, the builder package must appear only in the CPU variant unless
  it has accelerator dependencies.
- `make linter` must exit 0 before every commit (and again after, amending if it
  rewrites files). On the combined path it regenerates `.gitlab-triggers.yaml`,
  which must be included in the builder commit.

## Downstream consumers

- **Builder CI**: reads committed `builder/` configuration to build package wheels.
- **Pipeline CI**: reads `rhai-pipeline/collections/onboarding/` requirements to
  install and test the package across variant environments.
- **package-onboarding orchestrator**: validates commits exist, creates a single
  fondue MR, and applies Jira labels (`package-builder-onboarded` and/or
  `package-pipeline-onboarded`).
