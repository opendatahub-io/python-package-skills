import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    ROOT / "skills/packaging-investigation/scripts/write_json.py",
    ROOT / "skills/security-audit/scripts/write_json.py",
]


def _load(path: Path):
    name = path.parents[1].name.replace("-", "_")
    spec = importlib.util.spec_from_file_location(f"write_json_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(params=SCRIPTS, ids=lambda path: path.parents[1].name)
def mod(request):
    return _load(request.param)


def _layout(tmp_path, monkeypatch, mod):
    cwd = tmp_path / "sandbox" / "pkg"
    mount = tmp_path / "workspace"
    cwd.mkdir(parents=True)
    mount.mkdir()
    monkeypatch.chdir(cwd)
    monkeypatch.setattr(mod, "_sandbox_root", lambda: tmp_path / "sandbox")
    monkeypatch.setattr(mod, "_openshell_workspace_mount", lambda: mount)
    return cwd, mount


def test_codex_allows_cwd_only(tmp_path, monkeypatch, mod):
    cwd, mount = _layout(tmp_path, monkeypatch, mod)
    monkeypatch.setenv("AGENT_TOOL", "codex")
    assert mod._constrain_artifact_path(cwd / "out.json", label="Output")
    assert mod._constrain_artifact_path(mount / "out.json", label="Output") is None
    assert mod._constrain_artifact_path(tmp_path / "out.json", label="Output") is None


def test_openshell_allows_cwd_and_workspace_mount(tmp_path, monkeypatch, mod):
    cwd, mount = _layout(tmp_path, monkeypatch, mod)
    monkeypatch.setenv("AGENT_TOOL", "claude")
    assert mod._constrain_artifact_path(cwd / "out.json", label="Output")
    assert mod._constrain_artifact_path(mount / "out.json", label="Output")
    assert mod._constrain_artifact_path(tmp_path / "out.json", label="Output") is None


def test_symlink_outside_cwd_is_rejected(tmp_path, monkeypatch, mod):
    cwd, _mount = _layout(tmp_path, monkeypatch, mod)
    monkeypatch.setenv("AGENT_TOOL", "codex")
    outside = tmp_path / "other"
    outside.mkdir()
    link = cwd / "out.json"
    link.symlink_to(outside / "out.json")
    assert mod._constrain_artifact_path(link, label="Output") is None
