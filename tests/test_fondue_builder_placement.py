"""Check fixture inputs and exercise the eval's real builder-placement judge."""

import shutil
import textwrap
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "eval/cases-fondue-onboarding"
COMBINED = sorted(CASES.glob("case-combined-*"))
SUCCESSFUL = [
    case
    for case in COMBINED
    if yaml.safe_load((case / "annotations.yaml").read_text())["expected_commit_count"]
    > 0
]
CONFIG = yaml.safe_load((ROOT / "eval-fondue-onboarding.yaml").read_text())
JUDGE = next(
    judge
    for judge in CONFIG["judges"]
    if judge["name"] == "builder_collection_placement"
)


def _materialize(source, workspace):
    for fixture in source.rglob("*.fixture"):
        target = workspace / fixture.relative_to(source).with_suffix("")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(fixture, target)
    return yaml.safe_load((source / "annotations.yaml").read_text())


def _judge(annotations):
    namespace = {}
    # Exercise the trusted, checked-in judge exactly as the eval harness does.
    exec(  # noqa: S102
        "def check(annotations):\n" + textwrap.indent(JUDGE["check"], "    "), namespace
    )
    return namespace["check"](annotations)


def _add_package(workspace, placement, package, *, directory=False):
    target = workspace / "builder/collections" / placement
    if directory:
        (target / "requirements.txt").unlink(missing_ok=True)
        target = target / "requirements" / "packages.txt"
    else:
        target = target / "requirements.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a") as stream:
        stream.write(f"{package}==1.0; python_version >= '3.11'  # eval package\n")


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.mark.parametrize("source", COMBINED, ids=lambda case: case.name)
def test_combined_fixture_inputs(source, workspace):
    annotations = _materialize(source, workspace)
    assert (
        workspace / ".agents/builder/onboarding/04-collection-integration.md"
    ).is_file()
    for placement in annotations.get("expected_builder_placements", []):
        assert (
            workspace / "builder/collections" / placement / "requirements.txt"
        ).is_file()
    pipeline = yaml.safe_load((workspace / "ci-job-definitions.yml").read_text())[
        "rhai_pipeline"
    ]
    for settings in pipeline["torch_versions"].values():
        collection = settings["builder_collection"]
        constraints = (
            workspace / "builder/collections" / collection / "cpu-ubi9/constraints.txt"
        )
        assert f"torch=={collection.removeprefix('torch-')}" in constraints.read_text()
    for variant in pipeline["collections"]["onboarding"]["variants"]:
        assert (workspace / "rhai-pipeline/collections/onboarding" / variant).is_dir()


@pytest.mark.parametrize("source", SUCCESSFUL, ids=lambda case: case.name)
def test_expected_placements_pass(source, workspace):
    annotations = _materialize(source, workspace)
    for placement in annotations["expected_builder_placements"]:
        _add_package(workspace, placement, annotations["expected_package"])
    passed, detail = _judge(annotations)
    assert passed, detail


@pytest.mark.parametrize("source", SUCCESSFUL, ids=lambda case: case.name)
def test_wrong_collection_fails(source, workspace):
    annotations = _materialize(source, workspace)
    expected = annotations["expected_builder_placements"]
    if expected == ["universal/cpu-ubi9"]:
        wrong = "torchless/cpu-ubi9"
    elif expected[0].startswith("torchless/"):
        wrong = "universal/cpu-ubi9"
    else:
        wrong = "torch-99.0.0/cpu-ubi9"
    _add_package(workspace, wrong, annotations["expected_package"])
    passed, detail = _judge(annotations)
    assert not passed
    assert wrong in detail


def test_missing_cuda_variant_fails(workspace):
    annotations = _materialize(CASES / "case-combined-accelerator", workspace)
    _add_package(workspace, "torchless/cpu-ubi9", annotations["expected_package"])
    passed, detail = _judge(annotations)
    assert not passed
    assert "torchless/cuda12.9-ubi9" in detail


def test_extra_lane_fails(workspace):
    annotations = _materialize(CASES / "case-combined-pure-python", workspace)
    for placement in ["universal/cpu-ubi9", "torchless/cpu-ubi9"]:
        _add_package(workspace, placement, annotations["expected_package"])
    passed, detail = _judge(annotations)
    assert not passed
    assert "torchless/cpu-ubi9" in detail


def test_normalized_name_in_requirements_directory_passes(workspace):
    annotations = _materialize(CASES / "case-combined-pure-python", workspace)
    package = annotations["expected_package"].upper().replace("-", "_")
    _add_package(workspace, "universal/cpu-ubi9", package, directory=True)
    passed, detail = _judge(annotations)
    assert passed, detail
