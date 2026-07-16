#!/usr/bin/env bash
set -eo pipefail

# deterministic-commit.sh — Programmatic git commit for onboarding steps.
# Replaces prompt-driven git add/commit/amend with a single script call
# that handles staging, message formatting, trailers, and linter-amend loops.

usage() {
    cat <<'EOF'
Usage: commit.sh [OPTIONS]

Stage all changes, format a commit message with trailers, and commit.

Required:
  --ticket KEY          Jira ticket key (e.g., AIPCC-12345)
  --subject SUBJECT     Full commit subject line

Optional:
  --body TEXT           Commit message body (multi-line OK)
  --body-file PATH     Read body from file (overrides --body)
  --lint-cmd CMD        Linter command; if it modifies files, amend the commit
  --trailer KEY=VALUE   Additional trailer line (repeatable)
  --exclude PATTERN     Extra git-add exclusion pathspec (repeatable)

The script always adds "Closes: <ticket>" as the final trailer and always
excludes the _run/ directory from staging.
EOF
    exit 1
}

die() { echo "Error: $1" >&2; exit 1; }

ticket=""
subject=""
body=""
body_file=""
lint_cmd=""
extra_trailers=()
extra_excludes=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --ticket)    ticket="$2";               shift 2 ;;
        --subject)   subject="$2";              shift 2 ;;
        --body)      body="$2";                 shift 2 ;;
        --body-file) body_file="$2";            shift 2 ;;
        --lint-cmd)  lint_cmd="$2";             shift 2 ;;
        --trailer)   extra_trailers+=("$2");    shift 2 ;;
        --exclude)   extra_excludes+=("$2");    shift 2 ;;
        -h|--help)   usage ;;
        *)           die "unknown option: $1" ;;
    esac
done

[[ -z "$ticket" ]]  && die "--ticket is required"
[[ -z "$subject" ]] && die "--subject is required"

if [[ -n "$body_file" ]]; then
    [[ -f "$body_file" ]] || die "body file not found: $body_file"
    body="$(< "$body_file")"
fi

# --- Build pathspec exclusions (always exclude _run/) ---
exclude_specs=( ":!_run" )
for pat in "${extra_excludes[@]+"${extra_excludes[@]}"}"; do
    exclude_specs+=( ":!$pat" )
done

# --- Pre-commit linter pass (catch auto-fixes before staging) ---
if [[ -n "$lint_cmd" ]]; then
    echo "==> Running linter (pre-commit)..."
    eval "$lint_cmd" || true
fi

# --- Stage ---
echo "==> Staging changes..."
git add -A -- . "${exclude_specs[@]}"

if git diff --cached --quiet; then
    die "nothing staged — no changes to commit"
fi

echo "Staged files:"
git diff --cached --stat

# --- Build commit message ---
msg="$subject"

if [[ -n "$body" ]]; then
    msg="${msg}

${body}"
fi

trailer_block=""
for t in "${extra_trailers[@]+"${extra_trailers[@]}"}"; do
    trailer_block="${trailer_block}${t}
"
done
trailer_block="${trailer_block}Closes: ${ticket}"

msg="${msg}

${trailer_block}"

# --- Commit ---
echo "==> Committing..."
git commit -m "$msg"

# --- Post-commit linter-amend loop ---
if [[ -n "$lint_cmd" ]]; then
    max_amend=3
    for (( i = 1; i <= max_amend; i++ )); do
        echo "==> Running linter (post-commit pass ${i}/${max_amend})..."
        eval "$lint_cmd" || true

        if git diff --quiet && git diff --cached --quiet; then
            echo "Working tree clean after linting."
            break
        fi

        echo "Linter modified files — amending commit..."
        git add -A -- . "${exclude_specs[@]}"
        git commit --amend --no-edit
    done
fi

# --- Verify ---
echo "==> Verifying clean working tree..."
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "WARNING: working tree is not clean after commit" >&2
    git status --short >&2
    exit 1
fi

echo ""
echo "=== Commit created ==="
git log -1 --format="commit %H%nSubject: %s%n%n%b"
echo "=== Done ==="
