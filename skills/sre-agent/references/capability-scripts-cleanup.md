# Shared Capability: Temporary Script Cleanup

All modes (patrol, oncall/diagnosis) create temporary script directories under `.scripts/` during execution. These must be cleaned up after completion.

## Script

`scripts/scripts-cleanup.sh` (relative to the skill base directory `~/.claude/skills/sre-agent/`)

When calling, concatenate the skill base directory to get the full path. The relative path only works when the working directory happens to be the skill base directory.

## Usage

```bash
# Clean up a single directory
bash scripts/scripts-cleanup.sh Patrol-main
bash scripts/scripts-cleanup.sh Patrol-prod
bash scripts/scripts-cleanup.sh Diagnosis-k8s-443167
```

## Safety Mechanisms

- Name must start with `Patrol-` or `Diagnosis-`
- Only alphanumeric characters, hyphens, and underscores are allowed
- Path traversal characters are rejected (`..`, `/`, `\`, `~`)
- Symlinks are rejected
- Only operates on directories under `.scripts/`
- Idempotent: exits silently if directory does not exist

## Cleanup Responsibilities Per Mode

### Patrol Mode

| Role | Cleanup Target | Timing |
|------|---------|------|
| Level 2 Teammate | `.scripts/Patrol-{name}-{service}/` | After SendMessage to Level 1 |
| Level 1 Teammate | `.scripts/Patrol-{name}/` | After SendMessage to Lead |
| Lead (Patrol-main) | `.scripts/Patrol-main/` | After notification sent successfully |

### Diagnosis Mode

| Role | Cleanup Target | Timing |
|------|---------|------|
| Diagnosis Teammate | `.scripts/Diagnosis-{name}/` | After SendMessage to Triage |
