# executive-summary output format

This document defines the output contract for the executive-summary skill.
Downstream skills (pipeline-onboarding) consume this output via the
`summary` field in their context JSON.

## Output file

`.executive-summary-output.txt` -- written to the workspace root.

## Required structure

Plain prose, 2-3 lines. No headings, no bullet lists, no code blocks.

## Content rules

- State the build outcome (success or failure).
- If the build failed, mention the root cause.
- End with the key next step or recommendation.
- Use `**bold**` sparingly for emphasis on critical points only.
- No preamble ("Here is a summary...") -- output only the summary text.

## Example (failed build)

```
The build of native-crypto 2.1.0 **failed** due to missing OpenSSL development
headers (openssl-devel) in the build environment. Installing the system package
and retrying the source build is the recommended next step.
```

## Example (successful build)

```
numpy 1.26.4 built successfully from source across all configured variants
(CPU). No additional system dependencies were required. The package is ready
for pipeline onboarding.
```

## Validation rules

- The output file must be named exactly `.executive-summary-output.txt`.
- The content must be plain prose only: no headings (`#`), no bullet lists (`-` or `*`), no code blocks.
- Length must be 2-3 lines (sentences). Not a single word, not a paragraph.
- Must not start with preamble like "Here is a summary" or "Summary:".
- Must state the build outcome (success or failure) (enforced by LLM quality judge).
- If the build failed, the root cause must be mentioned (enforced by LLM quality judge).
- Must end with a next step or recommendation (enforced by LLM quality judge).

## Downstream consumers

- **pipeline-onboarding**: reads this output as the `summary` field in
  `pipeline-context.json`. The pipeline skill includes it in the commit message
  body when adding the package to the onboarding collection.
