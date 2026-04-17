# Local Scanning

For secret self-checks on developer machines or locally checked-out repositories.

## Applicable Scenarios

- "Scan this local repo"
- "Check whether the current workspace has any leaks"
- "Does the local Git history contain old secrets"

## Default Scope

Unless the user explicitly requests a minimal scan, run both steps by default:

1. `trufflehog filesystem .`
2. `trufflehog git file://<repo-name>`

This covers:

- Current workspace files
- Local Git history objects

This does not equate to "explicitly covering all branches."

## Command Examples

### Linux / macOS

```bash
REPO_NAME="$(basename "$PWD")"
SCAN_DIR="${TMPDIR:-/tmp}/trufflehog-local-$REPO_NAME"
mkdir -p "$SCAN_DIR"

trufflehog filesystem . \
  --json \
  --no-update \
  --results=verified,unknown \
  > "$SCAN_DIR/filesystem.json"

(
  cd ..
  trufflehog git "file://$REPO_NAME" \
    --json \
    --no-update \
    --results=verified,unknown \
    > "$SCAN_DIR/git-history.json"
)
```

### Windows PowerShell

```powershell
$RepoName = Split-Path -Leaf (Get-Location)
$ScanDir = Join-Path $env:TEMP "trufflehog-local-$RepoName"
New-Item -ItemType Directory -Force $ScanDir | Out-Null

trufflehog filesystem . --json --no-update --results=verified,unknown |
  Out-File -Encoding utf8 (Join-Path $ScanDir "filesystem.json")

Push-Location ..
trufflehog git "file://$RepoName" --json --no-update --results=verified,unknown |
  Out-File -Encoding utf8 (Join-Path $ScanDir "git-history.json")
Pop-Location
```

## Interpreting Results

- Address `verified` findings first
- Then review `unknown` findings
- Do not treat `Verified: false` as "safe"
- After remediation, re-scan before closing the issue
