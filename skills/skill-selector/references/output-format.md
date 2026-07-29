# skill-selector output format

## `.selector-verdict.json`

| Field | Type | Description |
|---|---|---|
| `selected_skill` | string or `null` | Skill name chosen, or `null` if none should run |
| `rationale` | string | One short sentence explaining the choice |

Allowed `selected_skill` values:

- `license-check`
- `security-audit`
- `failure-analysis`
- `packaging-investigation`
- `builder-onboarding`
- `pipeline-onboarding`
- `probe-test-onboarding`
- `jira-context-summary`
- `executive-summary`
- `null`

Schema: `schemas/selector-verdict.json`.

### Example (skill selected)

```json
{
  "selected_skill": "license-check",
  "rationale": "Request asks for SPDX redistribution compatibility assessment."
}
```

### Example (no skill)

```json
{
  "selected_skill": null,
  "rationale": "Request is unrelated to RHAI Python packaging skills."
}
```
