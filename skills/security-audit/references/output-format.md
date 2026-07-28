# security-audit output contract

Downstream consumer: package-onboarding (`load_security_verdict` in
`package_onboarding.claude.verdict`). Schema:
`schemas/security-verdict.json`.

## Output files

| File | Purpose |
|------|---------|
| `.security-verdict.json` | Machine-parsed verdict (required) |
| `.security-audit-output.md` | Jira-facing Markdown report (required) |

## Verdict JSON

```json
{
  "verdict": "passed",
  "risk_rating": "low_risk",
  "summary": "Brief one-line summary of the audit outcome",
  "findings": [
    "Finding 1 description"
  ]
}
```

| Field | Rules |
|-------|--------|
| `verdict` | One of `passed`, `blocked` |
| `risk_rating` | One of `no_issues`, `low_risk`, `needs_review`, `critical` |
| `summary` | Non-empty brief summary |
| `findings` | Array of non-empty strings (empty array when clean) |

### Risk rating → verdict mapping

| `risk_rating` | `verdict` |
|---------------|-----------|
| `no_issues` | `passed` |
| `low_risk` | `passed` |
| `needs_review` | `blocked` |
| `critical` | `blocked` |

Validate with:

```bash
uv run --script ${CLAUDE_SKILL_DIR}/scripts/write_json.py \
  ${CLAUDE_SKILL_DIR}/schemas/security-verdict.json \
  /workspace/.security-verdict.json \
  --input /workspace/.security-verdict.json
```

## Markdown report

`.security-audit-output.md` must be Markdown body only (no surrounding fences)
and include at minimum:

- Package identification (name, repository if known)
- Summary of findings, flagged issues, and recommendations
- Detailed findings grouped by category (vulnerabilities, license concerns,
  dependency risks, code quality signals)
- A risk rating line in the exact format:

```markdown
**Risk Rating:** {no_issues | low_risk | needs_review | critical}
```

## Example (clean package)

Context:

```json
{
  "package_name": "sample-clean-pkg",
  "git_repo": "https://github.com/example/sample-clean-pkg",
  "scan_outputs": {
    "hexora": "scans/hexora-results.json",
    "binary_scan": "scans/binary-scan.json",
    "malcontent": "scans/malcontent-results.json"
  }
}
```

`.security-verdict.json`:

```json
{
  "verdict": "passed",
  "risk_rating": "no_issues",
  "summary": "No security concerns found in static, binary, or git triage.",
  "findings": []
}
```

`.security-audit-output.md` (excerpt):

```markdown
# Security Audit: sample-clean-pkg

Repository: https://github.com/example/sample-clean-pkg

## Summary

Pre-computed scans reported no findings. No vulnerabilities, license concerns,
dependency risks, or code-quality security signals were identified.

## Findings

### Vulnerabilities
None.

### License concerns
None.

### Dependency risks
None.

### Code quality signals
None.

**Risk Rating:** no_issues
```

## Example (blocked / critical)

```json
{
  "verdict": "blocked",
  "risk_rating": "critical",
  "summary": "High-confidence malicious code patterns and CVE-linked findings.",
  "findings": [
    "hexora: eval() on remote content in pkg/evil.py (CVE-2024-99999)",
    "hexora: obfuscated dynamic import of subprocess in pkg/loader.py"
  ]
}
```
