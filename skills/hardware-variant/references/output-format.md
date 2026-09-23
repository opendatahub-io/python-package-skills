# hardware-variant output format

## Output file

`.hardware-variant-verdict.json`, written in the current working directory as
raw JSON with no Markdown fence or surrounding text.

## Resolved verdict

```json
{
  "verdict": "resolved",
  "variant": "cuda13.0-ubi9",
  "reason": "CUDA 13 explicitly matches the allowed CUDA 13 variant."
}
```

`variant` must be one of the `allowed_variants` supplied in context.

## Unresolved verdict

```json
{
  "verdict": "unresolved",
  "variant": null,
  "reason": "The requested accelerator family is not available in the allowed variants."
}
```

Use `unresolved` only when non-empty requirements cannot map to an allowed
variant. Empty and placeholder requirements resolve to `default_variant`.

## Downstream consumer

`package-onboarding` loads this file, validates the verdict and membership in
its configured variant set, and falls back to the pipeline input when the
verdict is unresolved or invalid.
