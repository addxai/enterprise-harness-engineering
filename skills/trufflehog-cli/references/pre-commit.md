# Pre-commit Integration

For team-wide local pre-commit interception; does not replace unified CI gates.

## Applicable Scenarios

- "Block leaks before they are committed"
- "Add pre-commit secret scanning to the repo"

## Integration Principles

- Follow the official TruffleHog pre-commit setup
- Use `--no-update` by default
- Check `verified` findings first by default
- Output only `Redacted` values; never print raw secrets
- Pre-commit is a commit-blocking scenario; generating a JSON report file is optional

## Minimal Example

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: trufflehog-verified
        name: trufflehog verified scan
        entry: ./skills/trufflehog-cli/scripts/pre-commit-trufflehog.sh
        language: system
        pass_filenames: false
```

Script behavior:

- If `HEAD~1` exists: performs an incremental git scan
- If `HEAD~1` does not exist (e.g., initial commit): falls back to `filesystem` scanning

## Initialization

```bash
pre-commit install
pre-commit run --all-files
```

## Rollout Recommendations

- Phase 1: only block on `verified` findings
- Once the team stabilizes, extend to `unknown` investigation
- If the local pre-commit hook fails, re-run it after the fix
