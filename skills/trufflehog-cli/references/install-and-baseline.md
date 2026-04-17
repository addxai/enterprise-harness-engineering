# Installation and Unified Baseline

## Single Source of Truth

- Pinned version: [`../assets/trufflehog-version.txt`](../assets/trufflehog-version.txt)
- Binary source: `trufflesecurity/trufflehog` official GitHub Releases
- Documentation source: TruffleHog official docs (Running the scanner, Pre-commit hooks, Analyzers)

When the team approves a version upgrade, only modify `trufflehog-version.txt`.

## Unified Rules

- All commands must include `--no-update` by default
- Only use official release assets; do not use unverified mirrors
- After downloading, verify the SHA256 checksum against the official checksum file
- Prefer the in-repo checksum file; remote checksum fallback is disabled by default (requires explicit opt-in)
- Checksum signature verification (cosign) is optional but recommended by default
- Scan artifacts are written to the system temp directory by default
- Tokens must not appear in URLs, command-line arguments, or reports
- Reports must never output `Raw` values; only `Redacted` is allowed
- By default, only look at `verified` findings; enable `unknown` when broader investigation is needed
- For self-hosted GitHub/GitLab verification anomalies, follow the official on-prem verification guide

## Installation Methods

Prefer the built-in scripts in this Skill to ensure consistent version and verification rules:

- POSIX:
  `./skills/trufflehog-cli/scripts/install-trufflehog.sh`
- PowerShell:
  `.\skills\trufflehog-cli\scripts\install-trufflehog.ps1`

Script behavior:

- Reads the version from `assets/trufflehog-version.txt`
- Downloads the corresponding version archive and preferentially reads the local checksum file
- Attempts `cosign` signature verification on the official checksum by default (enhances origin trustworthiness)
- Only extracts and installs after verification passes

Optional flags:

- `TRUFFLEHOG_VERIFY_CHECKSUM_SIGNATURE=0`: disable cosign signature verification (enabled by default)
- `TRUFFLEHOG_ALLOW_REMOTE_CHECKSUM=1`: allow remote checksum fallback when no local checksum is available (disabled by default)

## Temp Directory Convention

Each run uses its own temp directory:

- Linux / macOS:
  `${TMPDIR:-/tmp}/trufflehog-<workflow>-<target>`
- Windows PowerShell:
  `Join-Path $env:TEMP "trufflehog-<workflow>-<target>"`

## Minimum Report Fields

Every summary must include at least:

- Scan target
- Workflow type
- TruffleHog version
- Result mode
- Output directory
- `verified` count
- `unknown` count (if enabled)
- Coverage boundaries (e.g., branch, commit range, max-depth)
