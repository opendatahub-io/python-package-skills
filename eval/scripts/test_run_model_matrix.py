"""Unit tests for run_model_matrix helpers."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from types import ModuleType


def _load_module(name: str) -> ModuleType:
    path = Path(__file__).resolve().parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_parse_model_matrix = _load_module("run_model_matrix")._parse_model_matrix


class RunModelMatrixTest(unittest.TestCase):
    def test_parses_matrix_list(self) -> None:
        text = """
models:
  skill: claude-sonnet-4-6
  judge: claude-sonnet-4-6

model_matrix:
  skill:
    - claude-sonnet-4-6
    - claude-haiku-4-5
"""
        self.assertEqual(
            _parse_model_matrix(text),
            ["claude-sonnet-4-6", "claude-haiku-4-5"],
        )

    def test_falls_back_to_models_skill(self) -> None:
        text = """
models:
  skill: claude-sonnet-4-6
  judge: claude-sonnet-4-6
"""
        self.assertEqual(_parse_model_matrix(text), ["claude-sonnet-4-6"])


if __name__ == "__main__":
    unittest.main()
