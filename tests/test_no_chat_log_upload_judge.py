"""Host-owned transcript publication is a required eval behavior, even for blocked calls."""

from pathlib import Path
from textwrap import indent

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
JUDGE = "no_chat_log_upload_attempts"


@pytest.fixture(params=("fondue-onboarding", "probe-test-onboarding"))
def config(request):
    return yaml.safe_load((ROOT / f"eval-{request.param}.yaml").read_text())


@pytest.fixture
def judge(config):
    checks = [item for item in config["judges"] if item["name"] == JUDGE]
    assert len(checks) == 1
    namespace = {}
    # Run the trusted repository check itself, as the eval harness does.
    exec("def check(outputs):\n" + indent(checks[0]["check"], "    "), namespace)  # noqa: S102
    return namespace["check"]


def test_upload_judge_is_required_for_every_eval_case(config):
    check = next(item for item in config["judges"] if item["name"] == JUDGE)
    assert "if" not in check
    assert config["traces"]["events"] is True
    assert config["thresholds"][JUDGE]["min_mean"] == 1.0


@pytest.mark.parametrize(
    "target",
    (
        "jira-upload-chat-log",
        "odh-ai-helpers:jira-upload-chat-log",
        "/odh-ai-helpers:jira-upload-chat-log",
        "/jira-upload-chat-log RHAI-5954",
    ),
)
@pytest.mark.parametrize("result", ("blocked by interception", "upload succeeded"))
def test_any_upload_skill_attempt_fails_regardless_of_tool_result(
    judge, target, result
):
    outputs = {
        "events": [
            {
                "type": "assistant",
                "tools": [
                    {"name": "Skill", "input": {"skill": target, "args": "RHAI-5954"}}
                ],
            },
            {"type": "tool_result", "content": result},
        ]
    }

    passed, reason = judge(outputs)

    assert passed is False
    assert "attempted" in reason


@pytest.mark.parametrize(
    "assistant",
    (
        {
            "type": "assistant",
            "tools": [{"name": "Bash", "input": {"command": "make linter"}}],
        },
        {
            "type": "assistant",
            "tools": [{"name": "Skill", "input": {"skill": "git:shallow-clone"}}],
        },
        {
            "type": "assistant",
            "text": "The host handles jira-upload-chat-log publication.",
            "tools": [],
        },
        {
            "type": "assistant",
            "tools": [
                {
                    "name": "Read",
                    "input": {"file_path": "skills/jira-upload-chat-log/SKILL.md"},
                }
            ],
        },
        {
            "type": "assistant",
            "tools": [
                {
                    "name": "Bash",
                    "input": {"command": "rg jira-upload-chat-log README.md"},
                }
            ],
        },
    ),
)
def test_normal_work_and_mentions_of_uploads_do_not_count_as_invocations(
    judge, assistant
):
    outputs = {
        "events": [
            assistant,
            {
                "type": "tool_result",
                "content": "Untrusted text mentions /jira-upload-chat-log.",
            },
        ]
    }

    passed, reason = judge(outputs)

    assert passed is True
    assert isinstance(reason, str)


@pytest.mark.parametrize(
    "outputs", ({}, {"events": None}, {"events": []}, {"events": "not a tool trace"})
)
def test_missing_trace_cannot_pass_the_upload_check(judge, outputs):
    passed, reason = judge(outputs)

    assert passed is False
    assert "cannot verify" in reason


@pytest.mark.parametrize("inputs", ({}, None, "unparsed skill input"))
def test_unreadable_skill_targets_cannot_pass_the_upload_check(judge, inputs):
    outputs = {
        "events": [{"type": "assistant", "tools": [{"name": "Skill", "input": inputs}]}]
    }

    passed, reason = judge(outputs)

    assert passed is False
    assert "readable target" in reason


def test_lowercase_skill_tool_name_is_also_checked(judge):
    outputs = {
        "events": [
            {
                "type": "assistant",
                "tools": [
                    {"name": "skill", "input": {"skill": "jira-upload-chat-log"}}
                ],
            }
        ]
    }

    assert judge(outputs)[0] is False
