#!/usr/bin/env python3
"""State persistence utility for python-package-skills orchestrator workflows.

Provides read/write access to orchestrator state files and a
dispatch-context subcommand for context-compression recovery.

All I/O through Python (no cat/echo that trigger auth prompts in sandbox).

Subcommands:
    get <state-file> <key>          Read a value from the state file
    set <state-file> <key> <value>  Write a value to the state file
    init <state-file>               Initialize a new state file
    dispatch-context <state-file>   Print dispatch instructions for context recovery

State files use YAML for readability and are written to the workspace
directory (the cloned repo working dir), which persists across context
compression.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


def _load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    if yaml:
        return yaml.safe_load(raw) or {}
    return json.loads(raw)


def _save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if yaml:
        path.write_text(
            yaml.dump(state, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
    else:
        path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


def cmd_init(state_file: Path) -> int:
    """Initialize an empty state file."""
    scripts_dir = str(Path(__file__).resolve().parent)
    initial = {
        "phase": "start",
        "ticket_key": "",
        "iteration": 0,
        "max_iterations": 3,
        "skill_name": "",
        "scripts_dir": scripts_dir,
        "last_action": "",
    }
    _save_state(state_file, initial)

    recovery_script = state_file.parent / "dispatch-recovery.sh"
    recovery_script.write_text(
        f'#!/bin/bash\npython3 "{scripts_dir}/state.py" dispatch-context "{state_file}"\n',
        encoding="utf-8",
    )

    print(f"Initialized state file: {state_file}")
    return 0


def cmd_get(state_file: Path, key: str) -> int:
    """Read a value from the state file."""
    state = _load_state(state_file)
    value = state.get(key)
    if value is None:
        print(f"Key not found: {key}", file=sys.stderr)
        return 1
    if isinstance(value, (list, dict)):
        print(json.dumps(value, indent=2))
    else:
        print(value)
    return 0


def cmd_set(state_file: Path, key: str, value: str) -> int:
    """Write a value to the state file."""
    state = _load_state(state_file)

    if value.lower() in ("true", "false"):
        state[key] = value.lower() == "true"
    elif value.isdigit():
        state[key] = int(value)
    elif value.startswith("[") or value.startswith("{"):
        try:
            state[key] = json.loads(value)
        except json.JSONDecodeError:
            state[key] = value
    else:
        state[key] = value

    _save_state(state_file, state)
    return 0


def cmd_dispatch_context(state_file: Path) -> int:
    """Print human-readable dispatch instructions for context recovery.

    Called by the SessionStart hook after context compression.
    Reads the state file and tells the LLM exactly what to do next.
    """
    state = _load_state(state_file)

    if not state:
        print("No state file found. Starting fresh.")
        return 0

    phase = state.get("phase", "unknown")
    ticket_key = state.get("ticket_key", "unknown")
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 3)
    skill_name = state.get("skill_name", "")
    last_action = state.get("last_action", "")

    print("=" * 60)
    print("CONTEXT RECOVERY -- State restored from disk")
    print("=" * 60)
    print()
    print(f"Ticket:      {ticket_key}")
    print(f"Skill:       {skill_name}")
    print(f"Phase:       {phase}")
    print(f"Iteration:   {iteration}/{max_iterations}")
    print(f"Last action: {last_action}")
    print()

    context_path = f"/workspace/_context/{skill_name}-context.json"

    instructions = {
        "start": [
            "NEXT: Read the context JSON and begin the workflow.",
            f"Load {context_path} and extract all fields.",
            "Then read the target repository's AGENTS.md (if present).",
        ],
        "investigate": [
            "NEXT: Continue analysis/investigation of the package.",
            f"Re-read {context_path} for the original requirements.",
            "Check git status to see what work has already been done.",
        ],
        "implement": [
            f"NEXT: Continue making changes (iteration {iteration + 1}/{max_iterations}).",
            "Run git status and git diff to see current state.",
            "If review findings exist, address them before continuing.",
        ],
        "review": [
            "NEXT: Run the review agent to check the implementation.",
            "Read the review prompt file from prompts/ and follow it.",
            "Write findings to the designated review-findings output.",
        ],
        "validate": [
            "NEXT: Run linters and fix any issues.",
            "Execute the lint command for this repository.",
            "Iterate until all linters pass with zero errors.",
        ],
        "commit": [
            "NEXT: Run the deterministic commit script.",
            "Ensure all file changes are complete and linters pass.",
            "Execute scripts/commit.sh with --ticket and --subject.",
        ],
        "done": [
            "DONE: Pipeline completed.",
            "Verify all expected output files exist.",
            "Upload the chat log to the Jira ticket if applicable.",
        ],
    }

    lines = instructions.get(phase)
    if lines:
        for line in lines:
            print(line)
    else:
        print(f"NEXT: Phase '{phase}' is not a standard phase.")
        print("Read the full state file to understand context:")
        print(f"  python3 scripts/state.py get {state_file} phase")
        print(f"  python3 scripts/state.py get {state_file} last_action")
        print("Then resume from where last_action left off.")

    print()
    print("=" * 60)
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: state.py <command> <state-file> [args...]", file=sys.stderr)
        print("Commands: init, get, set, dispatch-context", file=sys.stderr)
        return 1

    command = sys.argv[1]
    if command == "init":
        if len(sys.argv) < 3:
            print("Usage: state.py init <state-file>", file=sys.stderr)
            return 1
        return cmd_init(Path(sys.argv[2]))
    elif command == "get":
        if len(sys.argv) < 4:
            print("Usage: state.py get <state-file> <key>", file=sys.stderr)
            return 1
        return cmd_get(Path(sys.argv[2]), sys.argv[3])
    elif command == "set":
        if len(sys.argv) < 5:
            print("Usage: state.py set <state-file> <key> <value>", file=sys.stderr)
            return 1
        return cmd_set(Path(sys.argv[2]), sys.argv[3], sys.argv[4])
    elif command == "dispatch-context":
        if len(sys.argv) < 3:
            print("Usage: state.py dispatch-context <state-file>", file=sys.stderr)
            return 1
        return cmd_dispatch_context(Path(sys.argv[2]))
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
