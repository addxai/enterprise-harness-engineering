# TruffleHog JSONL Field Reference

TruffleHog's `--json` output is JSONL (one JSON object per line).

## Recommended Report Fields

| Field | Purpose |
|---|---|
| `DetectorName` | Credential type / detector name |
| `Verified` | Whether TruffleHog verified the credential as active |
| `Redacted` | Masked value safe for display |
| `SourceMetadata` | File, commit, and platform source information |

## Prohibited Fields

| Field | Rule |
|---|---|
| `Raw` | Must never be output or persisted to disk |
| Full plaintext credentials | Must never appear in reports |

## Common Extraction Paths

- File path:
  `SourceMetadata.Data.Git.file` (or the corresponding platform field)
- Commit hash:
  `SourceMetadata.Data.Git.commit`
- Author:
  `SourceMetadata.Data.Git.email` (or the corresponding platform field)
- Detail link:
  Platform-specific link fields (if present)

## Minimum Summary Template

- Scan target
- Workflow type
- TruffleHog version
- Result mode
- Output directory
- `verified` count
- `unknown` count (if enabled)
- Key verified results (`DetectorName`, file, commit, `Redacted`)
