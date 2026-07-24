# jira-context-summary output format

This document defines the output contract for the jira-context-summary skill.
Downstream skills (builder-onboarding, pipeline-onboarding) consume this output
via the `jira_context` field in their context JSON.

## Output file

`.jira-context-summary-output.txt` -- written to `/workspace/`.

## Required structure

The output must contain exactly four sections, each with a heading:

```
Ticket overview
<one sentence describing the package and onboarding request>

Key requirements and constraints
<bullet list of actionable packaging requirements>

Recent updates or decisions
<bullet list of latest updates, most recent first>

Known blockers or open questions
<bullet list of unresolved issues, or "None identified.">
```

## Section details

- **Ticket overview**: one sentence only. Name the package and what is being
  requested.
- **Key requirements and constraints**: bullet list. Include target versions,
  architectures, special build flags, dependencies, and any constraints from
  stakeholders.
- **Recent updates or decisions**: bullet list, most recent first. When
  contradictions exist between earlier and later comments, the later comment
  wins (latest-wins rule).
- **Known blockers or open questions**: bullet list. If none, write
  "None identified." Do not leave the section empty.

All four section headings must always be present, even if a section has no
relevant content (use "None identified." as the body).

## Example

A complete output for a numpy onboarding request:

```
Ticket overview
Request to onboard numpy 1.26.4 into the RHAI Python package pipeline for CPU and CUDA variants.

Key requirements and constraints
- Target version: numpy 1.26.4
- Architectures: x86_64 and aarch64
- Must build from source (no pre-built wheels)
- Requires OpenBLAS or MKL as the linear algebra backend
- CUDA variant needs cupy compatibility

Recent updates or decisions
- 2025-07-15 (maintainer): Confirmed OpenBLAS is the preferred backend over MKL for licensing reasons.
- 2025-07-10 (requester): Updated target version from 1.26.3 to 1.26.4 due to a security patch.

Known blockers or open questions
- aarch64 builds may need NEON-specific compiler flags; needs testing.
- Unclear whether CUDA 12.x or 11.x toolkit should be used for the CUDA variant.
```

## Validation rules

- The output file must be named exactly `.jira-context-summary-output.txt`.
- All four section headings must be present: "Ticket overview", "Key
  requirements and constraints", "Recent updates or decisions", "Known blockers
  or open questions".
- Section headings must appear in the order listed above.
- No section may be empty. If there is no relevant content, write
  "None identified." as the body.
- "Ticket overview" must be exactly one sentence.
- "Key requirements and constraints" must use bullet list format.
- "Recent updates or decisions" must use bullet list format, ordered most recent
  first.
- "Known blockers or open questions" must use bullet list format, or
  "None identified." if none exist.
- When Jira comments contradict each other, the later (more recent) comment
  wins.

## Downstream consumers

- **builder-onboarding**: reads this output as the `jira_context` field in
  `builder-context.json`. The builder skill uses it to understand stakeholder
  requirements and constraints for the package.
- **pipeline-onboarding**: reads this output as the `jira_context` field in
  `pipeline-context.json`. The pipeline skill uses it to verify requirements
  when creating collection files.
