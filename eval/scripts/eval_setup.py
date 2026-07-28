#!/usr/bin/env python3
"""Activate fixture files and commit workspace state.

Called as a SessionStart hook before the skill runs. Two jobs:

1. Rename *.fixture files to their real names (e.g. AGENTS.md.fixture
   -> AGENTS.md).  Fixtures use a safe extension in the repo so they
   are not auto-discovered as real configuration files, which is
   particularly important for security guardrail test cases.

2. Commit everything so seeded files do not appear in the eval
   harness git diff (which tracks agent modifications).
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def _activate_fixtures() -> None:
    """Rename *.fixture files to strip the .fixture suffix."""
    for p in Path(".").rglob("*.fixture"):
        if p.is_symlink():
            continue
        target = p.with_suffix("")
        if not target.exists():
            p.rename(target)
            print(f"eval_setup: {p} -> {target}")


def main() -> None:
    _activate_fixtures()

    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "eval-setup",
        "GIT_AUTHOR_EMAIL": "eval@setup",
        "GIT_COMMITTER_NAME": "eval-setup",
        "GIT_COMMITTER_EMAIL": "eval@setup",
    }
    subprocess.run(
        ["git", "add", "-A"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-q", "-m", "case setup", "--allow-empty"],
        check=True,
        capture_output=True,
        env=env,
    )
    print("eval_setup: workspace committed")


if __name__ == "__main__":
    main()
