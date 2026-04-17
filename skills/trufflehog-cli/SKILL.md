---
name: trufflehog-cli
description: Perform local secret scanning, remote repository scanning, pre-commit integration, and single-credential verification using TruffleHog CLI. Triggers when the user mentions trufflehog, secret scan, leaked credential investigation, Git history scan, remote repo scan, pre-commit, or post-rotation credential verification.
---

# trufflehog-cli

Unified entry point Skill for TruffleHog CLI in this repository.

Load modules on demand:

- Installation, version pinning, checksum verification, and temp-file strategy:
  [install-and-baseline.md](references/install-and-baseline.md)
- Local workspace + local Git history scanning:
  [local-scan.md](references/local-scan.md)
- Pre-commit integration:
  [pre-commit.md](references/pre-commit.md)
- Remote GitLab repository scanning:
  [remote-repo-scan.md](references/remote-repo-scan.md)
- Single-credential identification and verification:
  [credential-verify.md](references/credential-verify.md)
- Common credential types and verification patterns:
  [credential-types.md](references/credential-types.md)
- JSONL report field reference:
  [trufflehog-jsonl-format.md](references/trufflehog-jsonl-format.md)

For reproducible, auditable installation workflows, use the built-in scripts:

- POSIX install:
  [install-trufflehog.sh](scripts/install-trufflehog.sh)
- PowerShell install:
  [install-trufflehog.ps1](scripts/install-trufflehog.ps1)

For pre-commit, use the built-in wrapper script:

- POSIX pre-commit wrapper:
  [pre-commit-trufflehog.sh](scripts/pre-commit-trufflehog.sh)

## Description

Treat this Skill as the company's standard operating manual for TruffleHog CLI.

It covers four primary workflows:

- Local scanning: developer workstation files and local Git history
- Pre-commit integration: block new leaks before they are committed
- Remote repository scanning: scan a single HTTPS remote repository
- Credential verification: confirm whether a leaked credential is still active

Do not extend this Skill into general-purpose SAST, dependency vulnerability scanning, or code auditing.

## Rules

### Rule 1 - Read the unified baseline first

Read [install-and-baseline.md](references/install-and-baseline.md) first.

Baseline rules apply to all workflows:

- Version is sourced from [trufflehog-version.txt](assets/trufflehog-version.txt) as the single source of truth
- Must use official GitHub Release binaries and verify the official checksum
- All commands must include `--no-update` by default
- Scan artifacts go to the system temp directory, never the repository root
- Tokens must not appear in repository URLs or command-line arguments
- Reports may only use TruffleHog's `Redacted` output; raw secret values must never be printed

### Rule 2 - Select one primary workflow at a time

Determine the task type first, then load the corresponding reference:

- Local repository / developer workstation self-check:
  [local-scan.md](references/local-scan.md)
- Pre-commit integration:
  [pre-commit.md](references/pre-commit.md)
- Remote GitLab HTTPS repository scanning:
  [remote-repo-scan.md](references/remote-repo-scan.md)
- Single-credential leak investigation or post-rotation verification:
  [credential-verify.md](references/credential-verify.md)

Do not load all references at once by default.

### Rule 3 - Match commands to scenarios

Choose the command family based on the actual scan scope:

- `trufflehog filesystem .`: current workspace files
- `trufflehog git file://...`: local repository history
- `trufflehog git <https-repo-url>`: remote repository history
- `trufflehog analyze`: only when an interactive TUI session is available

Do not force the same command onto every scenario.

### Rule 4 - Least privilege first

Follow least-privilege for credentials:

- For remote repository clone scanning, prefer `read_repository`
- Only escalate to `read_api`/`api` when GitLab API-level verification is needed (e.g., PAT self-check)
- Prefer short-lived credentials and explicitly clean up after the workflow completes

### Rule 5 - Reports must clearly state scope and boundaries

Every result summary must include:

- Scan target
- Actual command family used
- Execution directory or target repository
- Result file location
- Count of `verified` vs `unknown` findings
- Scope constraints (e.g., `--branch`, `--since-commit`, `--max-depth`)

Do not claim coverage of branches that were not explicitly scanned.

## Examples

### Bad

```text
User says “scan the repo,” and I run a generic command, write JSON to the repo root,
output plaintext secrets, and conclude “all branches are clean.”
```

Problems:

- Command does not match scope
- Pollutes the workspace
- Leaks sensitive information
- Conclusion exceeds actual coverage

### Good

```text
Confirm version, installation, and output strategy per the unified baseline first,
then select a single workflow with its corresponding command;
artifacts go to a temp directory, and the report clearly states what was and was not covered.
```

Strengths:

- Single entry point + single baseline avoids duplicate maintenance
- Progressive loading keeps the main document concise
- Centralized rules simplify collaboration and auditing
- Output is traceable and does not leak sensitive information
