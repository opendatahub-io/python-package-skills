# constraint-bug-description output format

## Output file

Write `.constraint-bug-description-output.md` in the current working directory.
The file contains Markdown only, with no surrounding fence or preamble.

## Required structure

The first line must be exactly:

```text
repository: <fondue_web_url from context>
```

After that line, concise headings and bullets should identify:

- the package, blocking constraint, and constraint source file;
- the latest PyPI version and current production-index version;
- relevant diagnostic evidence from the build log, if any;
- the precise constraint or compatibility change and validation needed.

## Example

```markdown
repository: https://gitlab.com/redhat/rhel-ai/wheels/fondue

## Constraint blocking example-package 2.0.0

`example-package<2` in `builder/collections/example/constraints.txt` prevents
the resolver from selecting PyPI version 2.0.0, leaving the production index
on 1.9.0.

## Required change

- Verify 2.0.0 against the collection's dependency set.
- Relax or remove the `<2` constraint and run the package build and collection
  validation.
```

## Validation rules

- The required repository line is byte-for-byte the first line.
- The constraint, source, latest PyPI version, and index version are present.
- Build-log claims are evidence-based.
- The requested resolution is actionable.
