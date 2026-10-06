"""Keep verdict validation commands usable by both Codex and Claude."""

import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VALIDATORS = (
    (
        "license-check",
        "license-verdict.json",
        "6. **Validate the verdict:**",
        "SKILL.md",
    ),
    (
        "security-audit",
        "security-verdict.json",
        "7. **Validate the verdict:**",
        "SKILL.md",
    ),
    (
        "packaging-investigation",
        "investigation-verdict.json",
        "7. **Validate the verdict:**",
        "SKILL.md",
    ),
    (
        "hardware-variant",
        "hardware-variant-verdict.json",
        "5. Validate the result:",
        "SKILL.md",
    ),
    (
        "license-check",
        "license-verdict.json",
        "Validate the verdict with the bundled schema and writer:",
        "references/output-format.md",
    ),
    (
        "security-audit",
        "security-verdict.json",
        "Validate the verdict with the bundled schema and writer:",
        "references/output-format.md",
    ),
    (
        "packaging-investigation",
        "investigation-verdict.json",
        "Validate the verdict with the bundled schema and writer:",
        "references/output-format.md",
    ),
)


@pytest.mark.parametrize("skill_name,schema_name,heading,source_path", VALIDATORS)
@pytest.mark.parametrize("harness", ("codex", "claude"))
def test_validator_resolves_bundled_files(
    tmp_path, skill_name, schema_name, heading, source_path, harness
):
    skill_md = (ROOT / "skills" / skill_name / source_path).read_text()
    command = skill_md.split(heading, 1)[1].split("```bash", 1)[1].split("```", 1)[0]

    codex_home = tmp_path / "codex-home"
    skill_dir = codex_home / "skills" / skill_name
    (skill_dir / "scripts").mkdir(parents=True)
    (skill_dir / "schemas").mkdir()
    (skill_dir / "SKILL.md").touch()
    (skill_dir / "scripts" / "write_json.py").touch()
    (skill_dir / "schemas" / schema_name).touch()

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    uv = bin_dir / "uv"
    uv.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "$UV_ARGS_FILE"\n')
    uv.chmod(0o755)
    args_file = tmp_path / "uv-args.txt"

    env = {**os.environ, "CODEX_HOME": str(codex_home), "UV_ARGS_FILE": str(args_file)}
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env.pop("CLAUDE_SKILL_DIR", None)
    if harness == "claude":
        env["CLAUDE_SKILL_DIR"] = str(skill_dir)

    result = subprocess.run(
        ["bash", "-c", command], cwd=tmp_path, env=env, capture_output=True, check=False
    )

    assert result.returncode == 0, result.stderr.decode()
    args = args_file.read_text().splitlines()
    assert args[:4] == [
        "run",
        "--script",
        str(skill_dir / "scripts" / "write_json.py"),
        str(skill_dir / "schemas" / schema_name),
    ]
