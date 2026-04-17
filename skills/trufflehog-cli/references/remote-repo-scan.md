# Remote Repository Scanning

For scanning a single HTTPS remote Git repository.

## Applicable Scenarios

- "Scan this GitLab repo"
- "Check whether the remote repo has leaked credentials"
- "Run a security baseline check before onboarding the repo"

## Least Privilege

- For Git-over-HTTPS clone scanning, prefer `read_repository`
- Only escalate to `read_api` / `api` when GitLab API-level verification is needed

## Authentication Rules

Tokens must never be embedded in the repository URL.
Use `GIT_ASKPASS` + environment variables consistently.

## Command Examples

### Linux / macOS

```bash
if [ -z "${GITLAB_TOKEN:-}" ]; then
  echo "GITLAB_TOKEN is required" >&2
  exit 1
fi

ASKPASS_SCRIPT="$(mktemp /tmp/trufflehog-askpass-XXXXXX.sh)"
cat > "$ASKPASS_SCRIPT" <<'EOF'
#!/bin/sh
case "$(printf '%s' "${1-}" | tr '[:upper:]' '[:lower:]')" in
  *username*) echo oauth2 ;;
  *password*) echo "$GITLAB_TOKEN" ;;
  *) echo "" ;;
esac
EOF
chmod +x "$ASKPASS_SCRIPT"
export GIT_ASKPASS="$ASKPASS_SCRIPT"
export GIT_TERMINAL_PROMPT=0

REPO_URL="https://gitlab.example.com/group/project.git"
REPO_NAME="$(basename "$REPO_URL" .git)"
SCAN_DIR="${TMPDIR:-/tmp}/trufflehog-remote-$REPO_NAME"
mkdir -p "$SCAN_DIR"

trufflehog git "$REPO_URL" \
  --json \
  --no-update \
  --results=verified \
  > "$SCAN_DIR/git-history.json"

unset GIT_ASKPASS GIT_TERMINAL_PROMPT
rm -f "$ASKPASS_SCRIPT"
```

### Windows PowerShell

```powershell
if (-not $env:GITLAB_TOKEN) { throw "GITLAB_TOKEN is required" }

$AskpassDir = Join-Path $env:TEMP "trufflehog-askpass-$(Get-Random)"
New-Item -ItemType Directory -Force $AskpassDir | Out-Null

$PsPath = Join-Path $AskpassDir "askpass.ps1"
@'
param([string]$Prompt)
$Prompt = ($Prompt ?? "").ToLowerInvariant()
if ($Prompt -like "*username*") {
    "oauth2"
} elseif ($Prompt -like "*password*") {
    $env:GITLAB_TOKEN
} else {
    ""
}
'@ | Out-File -Encoding utf8 $PsPath

$CmdPath = Join-Path $AskpassDir "askpass.cmd"
@"
@echo off
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "$PsPath" %*
"@ | Out-File -Encoding ascii $CmdPath
$env:GIT_ASKPASS = $CmdPath
$env:GIT_TERMINAL_PROMPT = "0"

$RepoUrl = "https://gitlab.example.com/group/project.git"
$RepoName = [System.IO.Path]::GetFileNameWithoutExtension($RepoUrl.TrimEnd('/'))
$ScanDir = Join-Path $env:TEMP "trufflehog-remote-$RepoName"
New-Item -ItemType Directory -Force $ScanDir | Out-Null

& trufflehog git $RepoUrl --json --no-update --results=verified |
  Out-File -Encoding utf8 (Join-Path $ScanDir "git-history.json")

Remove-Item Env:\GIT_ASKPASS -ErrorAction SilentlyContinue
Remove-Item Env:\GIT_TERMINAL_PROMPT -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force $AskpassDir -ErrorAction SilentlyContinue
```

## Notes

- The team default is to check only `verified` findings
- Enable `unknown` when broader investigation is needed
