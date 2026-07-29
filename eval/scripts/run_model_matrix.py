#!/usr/bin/env python3
"""Emit model-matrix run commands for an eval config (AIPCC-28036).

Reads `model_matrix.skill` from an eval-*.yaml (or falls back to models.skill)
and prints one command per model. Does not execute the harness — that stays
with whatever runner the team uses (agentic-ci / Claude eval CLI).

Usage:
    python3 eval/scripts/run_model_matrix.py eval-skill-selector.yaml
    python3 eval/scripts/run_model_matrix.py eval-skill-selector.yaml --runner 'eval-run'
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _parse_model_matrix(text: str) -> list[str]:
    """Minimal YAML subset parser for model_matrix.skill list / models.skill."""
    models: list[str] = []
    in_matrix = False
    in_skill_list = False
    default_skill: str | None = None

    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        if line.startswith("model_matrix:"):
            in_matrix = True
            in_skill_list = False
            continue

        if in_matrix:
            if line.startswith("  skill:"):
                rest = line.split(":", 1)[1].strip()
                if rest.startswith("[") and rest.endswith("]"):
                    inner = rest[1:-1].strip()
                    if inner:
                        models.extend(p.strip().strip("'\"") for p in inner.split(","))
                    in_matrix = False
                    in_skill_list = False
                elif rest == "":
                    in_skill_list = True
                else:
                    models.append(rest.strip("'\""))
                    in_matrix = False
                    in_skill_list = False
                continue
            if in_skill_list:
                stripped = line.strip()
                if stripped.startswith("- "):
                    models.append(stripped[2:].strip().strip("'\""))
                    continue
                # left the list
                in_matrix = False
                in_skill_list = False

        if line.startswith("models:"):
            continue
        if line.startswith("  skill:") and not in_matrix:
            rest = line.split(":", 1)[1].strip().strip("'\"")
            if rest and not rest.startswith("["):
                default_skill = rest

    if models:
        # de-dupe preserving order
        seen: set[str] = set()
        out: list[str] = []
        for m in models:
            if m and m not in seen:
                seen.add(m)
                out.append(m)
        return out
    if default_skill:
        return [default_skill]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("eval_config", type=Path, help="Path to eval-*.yaml")
    parser.add_argument(
        "--runner",
        default="eval-run",
        help="Command prefix to print (default: eval-run)",
    )
    args = parser.parse_args(argv)

    if not args.eval_config.is_file():
        print(f"error: {args.eval_config} not found", file=sys.stderr)
        return 2

    models = _parse_model_matrix(args.eval_config.read_text(encoding="utf-8"))
    if not models:
        print(
            "error: no models found in model_matrix.skill or models.skill",
            file=sys.stderr,
        )
        return 2

    print(f"# Model matrix for {args.eval_config} ({len(models)} models)")
    for model in models:
        print(f"{args.runner} --config {args.eval_config} --model {model}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
