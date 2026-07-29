# packaging-investigation output contract

Downstream consumer: package-onboarding (`load_investigation_verdict` in
`package_onboarding.claude.verdict`). Schema:
`schemas/investigation-verdict.json`.

## Output files

| File | Purpose |
|------|---------|
| `.investigation-verdict.json` | Machine-parsed verdict (required) |
| `.investigation-output.md` | Full packaging analysis (required when `verdict` is `completed`) |

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

Validate with:

```bash
uv run --script ${CLAUDE_SKILL_DIR}/scripts/write_json.py \
  ${CLAUDE_SKILL_DIR}/schemas/investigation-verdict.json \
  /workspace/.investigation-verdict.json \
  --input /workspace/.investigation-verdict.json
```

## Markdown report

`.investigation-output.md` must be Markdown body only (no surrounding fences)
and follow the structure produced by
`odh-ai-helpers:python-packaging-investigator` (do not rearrange sections).
Typical sections include executive summary, source discovery, build system,
compilation requirements, dependencies, environment, packaging issues, CI/CD,
and recommended packaging strategy.

When `verdict` is `failed`, the Markdown report is optional; the verdict JSON
must still be valid with `complexity_score: 0` and observations explaining the
failure.

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
