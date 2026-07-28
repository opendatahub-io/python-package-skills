# probe-test-onboarding output format

This document defines the output contract for the probe-test-onboarding skill.
The output is a git commit containing test files, not a standalone file.

## Output artifact

A single git commit on the current branch of the wheels-test repository. The
commit adds probe test files for the target package.

## Commit message format

```
<probe_test_ticket>: add probe tests for <package_name>

Closes: <probe_test_ticket>
```

- **Subject line**: `<probe_test_ticket>: add probe tests for <package_name>`
  where both values come from the context JSON.
- **Trailer**: `Closes: <probe_test_ticket>` as the last line, separated from
  the subject by a blank line.

## Test file format

Test files are created in the `tests/` directory following the naming and
structure conventions established by existing probe tests in the repository.

- File names and directory layout must match the patterns used by other probe
  test files already in the repository.
- Use any existing `conftest.py` fixtures and helpers as appropriate.
- Each test function should be small, focused, and independently runnable.

## Test writing rules

- **Imports inside test functions only.** All package imports must be inside
  individual test functions, never at module level. Module-level imports cause
  the entire file to fail on ImportError, masking which tests would pass.
- **Match existing patterns.** Study 2-3 existing probe test files and follow
  their style, structure, and conventions.
- **Follow repository documentation.** Adhere to README.md, CLAUDE.md, and the
  probe-test-creator skill at `.claude/skills/probe-test-creator/SKILL.md`.
- **All linters must pass.** Run `probe_test_linter.py`, `ruff check`, and
  `ruff format` and fix any errors before committing.

## Import patterns

| Pattern | Allowed | Why |
|---------|---------|-----|
| `import pkg` inside test function | Yes | Failure is scoped to one test. |
| `from pkg import func` inside test function | Yes | Failure is scoped to one test. |
| `import pkg` at module level | No | ImportError fails the entire file, masking individual test results. |
| `import pytest` at module level | Yes | Test infrastructure imports are an exception. |
| `from conftest import ...` at module level | Yes | Test infrastructure imports are an exception. |

## Constraints

- **Clean working tree.** After committing, the working tree must have no
  uncommitted changes. Verify with `git status`.
- **No `_run/` directory.** The `_run/` directory (runtime telemetry) must
  never be staged. Use `git add -A -- . :!_run` to exclude it.
- **Single package only.** Create tests only for the package specified in the
  context JSON. Do not add tests for transitive dependencies.

## Example

For a package `text-utils` with main module `text_utils` and functions `clean_text()`, `tokenize()`:

**Test file** at `tests/test_text_utils.py`:

```python
def test_import():
    import text_utils

    assert text_utils is not None


def test_version():
    import text_utils

    assert hasattr(text_utils, "__version__")


def test_clean_text():
    from text_utils import clean_text

    result = clean_text("  hello  ")
    assert isinstance(result, str)


def test_tokenize():
    from text_utils import tokenize

    tokens = tokenize("hello world")
    assert isinstance(tokens, list)
    assert len(tokens) > 0
```

**Commit message:**

```
AIPCC-99020: add probe tests for text-utils

Closes: AIPCC-99020
```

Note: All imports are inside test functions, not at module level. Each test is small, focused, and independently runnable.

## Validation rules

- Exactly one commit must be produced.
- The commit subject must match `<probe_test_ticket>: add probe tests for <package_name>`.
- The commit must include a `Closes: <probe_test_ticket>` trailer.
- The working tree must be clean after committing (`git status --porcelain` returns empty).
- No files from the `_run/` directory may appear in the commit.
- At least one new `.py` test file must appear in the commit diff.
- No package imports may appear at module level (only inside test functions).
- All three linters must pass: `probe_test_linter.py`, `ruff check`, `ruff format` (enforced indirectly via working_tree_clean in evals; linters auto-fix files, so a dirty tree signals linter failure).
- Tests must only cover the single package from the context, not transitive dependencies.

## Downstream consumers

- **CI test runner**: executes the committed probe tests against the built
  package wheel to verify that the package installs correctly and core
  functionality works as expected.
