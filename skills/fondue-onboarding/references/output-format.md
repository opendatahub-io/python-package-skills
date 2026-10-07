# fondue-onboarding output format

This document defines the output contract for the fondue-onboarding skill.
Successful output is one or two git commits in the fondue monorepo (not a
file). A combined-mode fail-closed source-strategy outcome produces no commits.
Downstream CI reads committed configuration under `builder/` and/or
`rhai-pipeline/` when onboarding succeeds.

## Output artifact

| Mode | Commits | Subtrees touched |
|------|---------|------------------|
| `pipeline-only` | Exactly 1 | `rhai-pipeline/` only |
| `combined` (successful) | Exactly 2 | First: `builder/` (and optionally `.gitlab-triggers.yaml`); second: `rhai-pipeline/` |
| `combined` (fail-closed source strategy) | Exactly 0 | None; remove partial changes and leave a clean tree |

The working tree must be clean after completion (no uncommitted changes and no
staged `_run/` directory), including a fail-closed outcome with no commits.

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
- **Body**: mention the collection variant (CPU, CUDA, ROCm), source build
  strategy, and notable configuration details.
- **Trailer**: `Relates-to: <ticket>` as the last line (not `Closes`).

### Expected file changes

- Configuration under `builder/` (collections, plugins, overrides, settings as needed).
- Optionally `.gitlab-triggers.yaml` when required for the package.
- For each relevant onboarding job, map its `TORCH_VERSION` through
  `rhai_pipeline.torch_versions[version].builder_collection` in the root
  `ci-job-definitions.yml` and configure the package in that exact builder
  collection. This mapping supplies `BUILDER_TORCH_COLLECTION`; do not
  substitute the numerically highest collection. No new collections are
  created.

### Build strategy

| Strategy | When to use |
|----------|-------------|
| Source | Required for automated Path B onboarding. |
| Pre-built | Forbidden for automated Path B onboarding. |

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

Ordinary packages use one file per supported variant at
`rhai-pipeline/collections/onboarding/<variant>/requirements/<package_name>.txt`.
Torch-linked packages include `vllm`, `torchvision`, `torchaudio`, `torchao`,
`torchcodec`, `flash-attn`, `xformers`, `deep-ep`, `deep-gemm`, `nixl`,
`pplx-kernels`, `kvcached`, `detectron2`, `amd-aiter`, `amd-quark`, vLLM plugins,
and any package with native libTorch/Torch ABI evidence. For other packages,
inspect the requested distribution's public PyPI wheel when available: download
it without installing, verify its `.dist-info/METADATA` name and version, then
inspect extracted native libraries' ELF dependency metadata for `torchlib*.so`,
`libtorch*.so`, or `libc10*.so` links. A Python import or `Requires-Dist: torch`
alone establishes a runtime relationship, not native ABI linkage. If no
compatible wheel is available, use source/build evidence; wheel absence alone
does not prove the package is not Torch-linked.

Read the root `ci-job-definitions.yml` to determine which Torch channels
actually run for each variant. The current onboarding matrix is:

| Variant | Torch channels with jobs |
|---------|--------------------------|
| `cpu-ubi9` | 2.11, 2.13, 2.14 |
| `cuda13.0-ubi9` | 2.11, 2.13, 2.14 |
| `cuda12.9-ubi9` | 2.11, 2.13 |
| `rocm7.14-ubi9` | 2.11, 2.12 |
| `spyre-ubi9` | 2.11 |

The job-definition file is authoritative if this matrix changes. Add exactly
one package entry to
`rhai-pipeline/collections/onboarding/<variant>/torch/requirements-torch-X.Y.txt`
only for a variant/channel pair that both has a job and is supported by the
ticket and compatibility evidence. A job is necessary, but not sufficient, to
claim package support. No job reads a 2.13 overlay under ROCm or Spyre. CPU and
CUDA 13.0 jobs also run Torch 2.14, but leave that package out until its support
is established. A channel without a package entry does not build it. Preserve
unrelated entries. Channel-specific constraints, when needed, go in the
matching `torch/constraints-torch-X.Y.txt`; never put Torch-linked packages in
shared requirements or constraints.

Use the package version specified by the onboarding ticket/context. If none is
specified, leave the RHAI requirement unpinned unless the builder collection
provides an exact pin. Do not copy historical 3.6-EA1/EA2 migration pins as the
version for a new onboarding ticket. Use different versions across channels
only when the ticket or compatibility evidence calls for that. If the matching
builder Torch collection already pins the package with `==`, leave its RHAI
requirement unpinned and do not duplicate the builder pin. Keep platform
markers and the tracking comment on each entry.

Each ordinary requirements file contains exactly one line. A Torch overlay may
contain multiple package entries; add or update only the requested package:

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
- A missing PyPI sdist or a universal metapackage wheel is not sufficient
  justification for pre-built configuration. Use upstream source and a plugin.
- A required source plugin must use the PEP 503-derived identifier defined by
  the Plugin decision rule in `SKILL.md` for both its Fromager entry-point key
  and module under `[project.entry-points."fromager.project_overrides"]`.
- `pre_built: true` is forbidden during automated onboarding.
- No unrelated files may be modified.
- In combined mode, builder and rhai-pipeline changes must be in separate commits.

## Validation rules

- Commit count must match the outcome: 1 for pipeline-only, 2 for successful
  combined onboarding, or 0 for a combined fail-closed source-strategy outcome.
- The rhai-pipeline commit (last commit) must include a `Closes: <ticket>` trailer.
- In successful combined mode, the builder commit must include a
  `Relates-to: <ticket>` trailer.
- The working tree must be clean after committing (`git status --porcelain` empty).
- No files from `_run/` may appear in any commit.
- An ordinary package must have a requirements file for every supported variant.
  A Torch-linked package must appear only in supported channel overlays.
- Each ordinary requirements file contains one line with the package specifier
  and tracking comment. Each Torch overlay entry has its channel pin or remains
  unpinned when the matching builder collection has an exact pin.
- In combined mode, the builder package must appear only in the CPU variant unless
  it has accelerator dependencies.
- `make linter` must exit 0 before every commit (and again after, amending if it
  rewrites files). On a successful combined path it regenerates
  `.gitlab-triggers.yaml`, which must be included in the builder commit.

## Downstream consumers

- **Builder CI**: reads committed `builder/` configuration to build package wheels.
- **Pipeline CI**: reads `rhai-pipeline/collections/onboarding/` requirements to
  install and test the package across variant environments.
- **package-onboarding orchestrator**: validates commits exist, creates a single
  fondue MR, and applies Jira labels (`package-builder-onboarded` and/or
  `package-pipeline-onboarded`).
