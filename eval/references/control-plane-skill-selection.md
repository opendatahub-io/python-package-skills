# Control-plane skill selection evals

Suite: [`eval-skill-selector.yaml`](../../eval-skill-selector.yaml)  
Cases: [`eval/cases-skill-selector/`](../cases-skill-selector/)  
Skill: [`skills/skill-selector/`](../../skills/skill-selector/)

## Purpose

These are **control-plane** evals: they check whether the *right skill was
chosen* for a request, not whether that skill’s output was good (that’s
covered by each skill’s `eval-<skill>.yaml`).

Given a natural-language prompt and the full plugin loaded, `skill-selector`
picks a packaging skill (or none). Judges confirm the expected skill was
invoked — including ambiguous prompts and should-not-trigger cases.

## Work items (AIPCC-28036)

| Work item | Coverage |
|---|---|
| Ambiguous / multi-skill-eligible input; correct skill selected | `case-ambiguous-license-vs-security`, `case-ambiguous-failure-vs-executive-summary` |
| At least one case per skill: was this skill invoked? | One `case-trigger-<skill>` per packaging skill (9) |
| Deterministic judge on which skill was triggered | `expected_skill_triggered`, `no_skill_triggered`, `forbidden_skills_not_triggered` |
| Edge: multi-match + should-NOT-trigger | Ambiguous cases + `case-should-not-trigger` |

## How a case works

1. Case provides `_context/selector-context.json` with a natural-language `prompt`.
2. Harness starts `/skill-selector`.
3. Selector matches the prompt to skill descriptions, writes
   `.selector-verdict.json`, then invokes the chosen skill (or none).
4. Tool interception stubs the chosen skill’s body so the run stays selection-only.
5. Deterministic judges inspect the verdict file and which skill was invoked.

## Case map

| Case | Expected skill / outcome |
|---|---|
| `case-trigger-license-check` | `license-check` |
| `case-trigger-security-audit` | `security-audit` |
| `case-trigger-failure-analysis` | `failure-analysis` |
| `case-trigger-packaging-investigation` | `packaging-investigation` |
| `case-trigger-builder-onboarding` | `builder-onboarding` |
| `case-trigger-pipeline-onboarding` | `pipeline-onboarding` |
| `case-trigger-probe-test-onboarding` | `probe-test-onboarding` |
| `case-trigger-jira-context-summary` | `jira-context-summary` |
| `case-trigger-executive-summary` | `executive-summary` |
| `case-ambiguous-license-vs-security` | `security-audit` (forbid `license-check`) |
| `case-ambiguous-failure-vs-executive-summary` | `executive-summary` (forbid `failure-analysis`) |
| `case-should-not-trigger` | no skill |

## Multi-model matrix

```bash
python3 eval/scripts/run_model_matrix.py eval-skill-selector.yaml
```
