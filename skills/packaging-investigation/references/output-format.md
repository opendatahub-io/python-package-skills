# packaging-investigation output contract

Downstream consumer: package-onboarding (`load_investigation_verdict` in
`package_onboarding.claude.verdict`). Schema:
`schemas/investigation-verdict.json`.

## Output files

| File | Purpose |
|------|---------|
| `.investigation-verdict.json` | Machine-parsed verdict (required) |
| `.investigation-output.md` | Full packaging analysis (required when `verdict` is `completed`) |
| `.torch-evidence.json` | Structured Torch linkage evidence, including `unknown` when unavailable (always required) |

## Verdict JSON

```json
{
  "verdict": "completed",
  "complexity_score": 5,
  "observations": [
    "Key observation about the package"
  ]
}
```

| Field | Rules |
|-------|--------|
| `verdict` | One of `completed`, `failed` |
| `complexity_score` | Integer 0–10 inclusive; must be `0` when `verdict` is `failed` |
| `observations` | Non-empty array of non-empty, non-whitespace strings |

### Complexity scale (guidance)

| Score | Typical package |
|-------|-----------------|
| 0–3 | Pure Python / trivial setuptools or flit; `py3-none-any` |
| 4–6 | Limited native code or non-trivial build customization |
| 7–10 | Heavy C/Cython/Fortran/CUDA, system libs, multi-arch wheels |

Validate the verdict with the bundled schema and writer:

```bash
skill_dir="${CLAUDE_SKILL_DIR:-}"
if [ -z "$skill_dir" ]; then
  skill_file=$(find "${CODEX_HOME:-$HOME/.codex}" -type f -path '*/skills/packaging-investigation/SKILL.md' -print -quit)
  skill_dir="${skill_file%/SKILL.md}"
fi
test -f "$skill_dir/scripts/write_json.py" || exit 1
uv run --script "$skill_dir/scripts/write_json.py" \
  "$skill_dir/schemas/investigation-verdict.json" \
  .investigation-verdict.json \
  --input .investigation-verdict.json
```

## Markdown report

`.investigation-output.md` must be Markdown body only (no surrounding fences)
and follow the structure produced by
`odh-python-packaging:python-packaging-investigator` (do not rearrange sections).
Typical sections include executive summary, source discovery, build system,
compilation requirements, dependencies, environment, packaging issues, CI/CD,
and recommended packaging strategy.

When `verdict` is `failed`, the Markdown report is optional; the verdict JSON
must still be valid with `complexity_score: 0` and observations explaining the
failure.

## Torch evidence report

`.torch-evidence.json` follows `schemas/torch-evidence.json` and is consumed by
package-onboarding before fondue onboarding. It distinguishes a Python Torch
runtime dependency from native libTorch or Torch ABI linkage. Record the
classification (`torch-linked`, `torch-candidate`, `not-torch-linked`, or
`unknown`), confidence, observed signals, specific reasons, and source files.
For a public PyPI wheel, verify the distribution name/version and inspect
extracted native libraries' ELF dependencies for `torchlib*.so`,
`libtorch*.so`, or `libc10*.so`; record observed names in
`signals.native_torch_libraries` and the wheel/member in `source_files`. Do not
infer a native link from an import or runtime requirement alone. Use `unknown`
when evidence is missing or conflicting. Even a failed investigation must
write a valid report with an explanation.

## Example (pure Python)

Context:

```json
{
  "package_name": "sample-http-client",
  "package_info": "Pure Python HTTP client. No C extensions. setuptools.",
  "git_repo": "https://github.com/example/sample-http-client",
  "jira_context": "Investigate packaging for RHAI onboarding."
}
```

`.investigation-verdict.json`:

```json
{
  "verdict": "completed",
  "complexity_score": 2,
  "observations": [
    "Pure Python package; no native extensions or system library build deps",
    "setuptools with py3-none-any wheels; source build is straightforward"
  ]
}
```

## Example (native extension)

```json
{
  "verdict": "completed",
  "complexity_score": 8,
  "observations": [
    "C/Cython extensions via setup.py ext_modules require a C compiler",
    "Links against BLAS/LAPACK; multi-arch manylinux wheels expected"
  ]
}
```
