# hardware-variant output contract

Downstream consumer: package-onboarding (`load_hardware_variant_verdict`).
The orchestrator also checks that a `resolved` variant is in
`VARIANT_DEFAULT_COLLECTION`. Schema: `schemas/hardware-variant-verdict.json`.

This file is the human/orchestrator contract. The skill prompt already
contains the rules — do not duplicate catalog lists here (they go stale).

## Output file

`.hardware-variant-verdict.json` — required, workspace root, raw JSON.

## Verdict JSON

Resolved:

```json
{
  "verdict": "resolved",
  "variant": "cuda13.0-ubi9",
  "reason": "Hardware Requirements named CUDA 13."
}
```

Unresolved:

```json
{
  "verdict": "unresolved",
  "variant": null,
  "reason": "No accelerator or CPU/standard signal in the ticket text."
}
```

| Field | Rules |
|-------|--------|
| `verdict` | `resolved` or `unresolved` |
| `variant` | One of context `allowed_variants` when resolved; `null` when unresolved |
| `reason` | One sentence |

## Context JSON

`/workspace/_context/hardware-variant-context.json`

| Field | Trust | Role |
|-------|--------|------|
| `package_name` | trusted (PEP 508) | Identity only; not used for classification |
| `hardware_requirements` | untrusted | Primary signal |
| `ticket_description` | untrusted | Disambiguation only |
| `allowed_variants` | trusted (orchestrator) | Closed list of legal variants |
| `default_variant` | trusted (orchestrator) | Target for Standard / empty / CPU-only |

Orchestrator should keep untrusted fields short (`hardware_requirements` already
capped ~2k chars; prefer a similar cap on `ticket_description` rather than
shipping the full ticket).

## Downstream

Gather Info: a `resolved` variant other than `cpu-ubi9` overrides
`PACKAGE_VARIANT`. `unresolved`, a failed run, or `cpu-ubi9` falls back to
the pipeline input.
