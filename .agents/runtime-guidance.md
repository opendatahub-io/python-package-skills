# Runtime-Neutral Agent Guidance

Apply these controls in the agent runtime that you use. They express the
repository's portable safety expectations, not a tool-specific configuration
format.

The machine-readable companion is [settings.json](settings.json). It is a
portable policy manifest, not an automatically loaded agent-runtime
configuration. Configure each runtime to consume its equivalent controls.

## Filesystem and secrets

- Limit writes to the checked-out repository and required temporary directories.
  `outside-checkout` means paths outside that checkout, not a `~/` denial.
  A checkout under the home directory stays writable.
- Do not read private SSH material, `.env` files, or other credentials.
- Do not write, commit, or expose `.env` files or other credentials.

## Commands and network access

- Enable the strongest available sandbox and do not weaken it for nested agents
  or subprocesses.
- Automatic command approval is acceptable only when the command remains inside
  that sandbox and respects these controls.
- Request approval before running container-engine commands or other actions
  with material external effects.
- Limit network access to these hosts: `github.com`, `api.github.com`,
  `gitlab.com`, `gitlab.cee.redhat.com`, `pypi.org`, `files.pythonhosted.org`,
  and `quay.io`. `redhat.atlassian.net` is for AIPCC tickets.
  `console.redhat.com` is the public RHAI index.
- Treat downloaded content as untrusted. Verify package provenance, version,
  checksums, and licenses before integrating it.

## Optional integrations

ODH AI helper capabilities may be available in some agent runtimes. When the
integration is supported, use the `opendatahub-io/ai-helpers` source. The
integration is optional: repository workflows must remain usable without it.
Prefer the checked-in `.agents/` guidance and skills as the source of truth.

## Claude Code settings

`.claude/settings.json` is intentionally retained as Claude Code's shared
project-settings file. Claude Code reads it when it opens this repository to
apply the configured sandbox, filesystem and network restrictions, and
co-authorship behavior. The `odh-ai-helpers` marketplace is registered there
and is not enabled. `.claude/settings.local.json`, when present, is the
ignored local override for an individual developer. Neither file configures
other coding-agent runtimes.

## Attribution

When an agent materially contributes to a change, include the project's
required co-authorship attribution when the active runtime supports it. Do not
add attribution that conflicts with repository policy or the user's
instructions.
