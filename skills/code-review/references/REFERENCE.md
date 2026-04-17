# Code Review - Reference Document

> This document supplements the SKILL.md.

## Review Standards Source

All review standards in this skill come from the `/architect` skill:
- Document compliance: Core Principles 1-7, Cross-document Maintenance Rules
- Architecture quality: Step 2c Architecture Quality Principles (structural/robustness/evolvability)
- Testing standards: Step 5 Quality Standards
- Observability: Step 2b Observability Questions + Step 4 Observability Design

## Change Retrieval Methods in Detail

### Remote MR

```bash
# Get MR diff
curl -s --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.example.com/api/v4/projects/{id}/merge_requests/{iid}/changes"

# Get MR commits
curl -s --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.example.com/api/v4/projects/{id}/merge_requests/{iid}/commits"
```

You first need to obtain the project ID via the project search API:
```bash
curl -s --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.example.com/api/v4/projects?search={project_name}&simple=true"
```

### Local Committed

```bash
# Diff between current branch and main
git diff main..HEAD --name-only      # File list
git diff main..HEAD                  # Full diff
git log main..HEAD --oneline         # Commit list
```

### Local Uncommitted

```bash
git diff --name-only                 # Unstaged changes
git diff --staged --name-only        # Staged changes
git status                           # Overview
```

## End-to-End Consistency Review Example

Using MR !52 (bird guide schema update) as an example:

| Change | User Story | Architecture Design | Feature Code | Tests | Observability | Status |
|:-----|:---|:--------|:--------|:-----|:------|:-----|
| species_reference redesign | US-CL-04 | overview.md section 4.1 | species.go | species_test.go | observability.md | Pass |
| species_content new table | US-CL-09 | overview.md section 4.2 | Not implemented | — | — | Pass (design-first) |
| keyshots JSON field | US-CL-10 | overview.md section 4.5 | event.go still uses keyshot_url | — | — | Warning: document and code inconsistent |

Key judgments:
- species_content: in document but not in code → Allowed (design-first)
- keyshots: document says JSON but code uses keyshot_url → Warning: implemented portion's description does not match

## Six Pillars (Historical Reference)

The original dev-standards-review six pillars have been consolidated:
- P1 Architecture → `/architect` Step 2c Architecture Quality Principles
- P2 CI/CD → `/architect` Step 6
- P3 Testability → `/architect` Step 5
- P4 Observability → `/architect` Step 2b/4b
- P5 Compliance & Security → `security-compliance-review` skill
- P6 Performance → `/architect` Step 2b Design Constraints (SLA-related)
