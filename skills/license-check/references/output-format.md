# license-check output contract

Downstream consumer: package-onboarding (`load_license_verdict` in
`package_onboarding.claude.verdict`). Schema:
`schemas/license-verdict.json`.

## Output files

| File | Purpose |
|------|---------|
| `.license-verdict.json` | Machine-parsed verdict (required) |
| `.license-check-output.txt` | Jira-facing text report (required) |

## Verdict JSON

```json
{
  "verdict": "compatible",
  "license": "Apache-2.0",
  "compatible": true,
  "reason": "Apache-2.0 is a permissive license that allows redistribution."
}
```

| Field | Rules |
|-------|--------|
| `verdict` | One of `compatible`, `incompatible`, `unknown` |
| `license` | SPDX id, or `Unknown` when undetermined |
| `compatible` | `true` only when `verdict` is `compatible`; otherwise `false` |
| `reason` | One sentence explaining the assessment |

Validate the verdict with the bundled schema and writer:

```bash
skill_dir="${CLAUDE_SKILL_DIR:-}"
if [ -z "$skill_dir" ]; then
  skill_file=$(find "${CODEX_HOME:-$HOME/.codex}" -type f -path '*/skills/license-check/SKILL.md' -print -quit)
  skill_dir="${skill_file%/SKILL.md}"
fi
test -f "$skill_dir/scripts/write_json.py" || exit 1
uv run --script "$skill_dir/scripts/write_json.py" \
  "$skill_dir/schemas/license-verdict.json" \
  .license-verdict.json \
  --input .license-verdict.json
```

## Text report (Jira markup)

```
*License:* <SPDX identifier>
*Redistribution Compatible:* YES, NO, or UNKNOWN
*Reason:* <one-sentence explanation>
```

| Text value | `verdict` | `compatible` |
|------------|-----------|--------------|
| YES | `compatible` | `true` |
| NO | `incompatible` | `false` |
| UNKNOWN | `unknown` | `false` |

## Example (Apache-2.0)

Context:

```json
{
  "package_name": "sample-lib",
  "source_url": "https://github.com/example/sample-lib"
}
```

`.license-check-output.txt`:

```
*License:* Apache-2.0
*Redistribution Compatible:* YES
*Reason:* Apache-2.0 is a permissive license that allows redistribution.
```

`.license-verdict.json`:

```json
{
  "verdict": "compatible",
  "license": "Apache-2.0",
  "compatible": true,
  "reason": "Apache-2.0 is a permissive license that allows redistribution."
}
```
