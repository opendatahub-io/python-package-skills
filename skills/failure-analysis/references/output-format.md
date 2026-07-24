# failure-analysis output format

This document defines the output contract for the failure-analysis skill.
Downstream skills (builder-onboarding) consume this output via the
`failure_summary` field in their context JSON.

## Output file

`.failure-analysis-output.md` -- written to the workspace root.

## Required structure

```markdown
## Build Failure Analysis: <package_name>

### Root Cause

<Clear description of what went wrong, or description of symptoms if uncertain>

### Evidence

<Relevant lines from the log excerpt, in code blocks>

### Recommended Fix

<Specific, actionable steps to resolve the failure, focused on source-based building>

### Confidence

<High / Medium / Low -- with brief justification>
```

## Section details

- **Root Cause**: one or more paragraphs describing the failure. Use `**bold**`
  for key terms (package names, missing headers, system packages).
- **Evidence**: relevant log lines in fenced code blocks. Include only the lines
  that support the root cause diagnosis, not the entire log.
- **Recommended Fix**: actionable steps. Use bullet lists for multiple steps.
  Always prefer source-build solutions over pre-built wheels.
- **Confidence**: exactly one of `High`, `Medium`, or `Low` in bold, followed
  by a brief justification after `--`.

## Confidence levels

| Level | When to use |
|-------|-------------|
| High | Single, unambiguous error with a direct mapping to a known fix (e.g., missing system header, clear version incompatibility). |
| Medium | Likely root cause identified but the log contains multiple failure signals, is truncated, or the fix has not been verified. |
| Low | Symptoms described but root cause is uncertain. The log is ambiguous, incomplete, or shows a rare/undocumented failure mode. |

## Example

A complete output for a missing system header failure:

````markdown
## Build Failure Analysis: fast-xml

### Root Cause

The C extension `fast_xml._parser` failed to compile because the **libxml2 development headers** are not installed in the build environment. The source file `_parser.c` includes `libxml/parser.h`, which is provided by the `libxml2-devel` system package.

### Evidence

```
fast_xml/_parser.c:8:10: fatal error: libxml/parser.h: No such file or directory
    8 | #include "libxml/parser.h"
error: command '/usr/bin/gcc' failed with exit code 1
```

### Recommended Fix

Install the `libxml2-devel` package in the build environment. Add it to the pipeline's build dependency list:
- RHEL/Fedora: `dnf install libxml2-devel`
- Debian/Ubuntu: `apt-get install libxml2-dev`

### Confidence

**High** -- the error is a single, unambiguous missing header with a direct mapping to a well-known system package.
````

## Validation rules

- The output file must be named exactly `.failure-analysis-output.md`.
- The `##` title line must include the package name from the context.
- All four `###` section headings must be present, in order: Root Cause, Evidence, Recommended Fix, Confidence.
- The Confidence section must start with exactly one of **High**, **Medium**, or **Low** in bold.
- Evidence must contain at least one fenced code block with actual log lines.
- Recommended Fix must not recommend pre-built wheels unless source building is impossible (enforced by LLM quality judge; inherently subjective).

## Downstream consumers

- **builder-onboarding**: reads this output as the `failure_summary` field in
  `builder-context.json`. The builder skill uses it to understand what failed
  and determine the correct configuration for the package.
