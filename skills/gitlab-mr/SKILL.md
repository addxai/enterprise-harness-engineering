---
name: gitlab-mr
description: Create and manage GitLab Merge Requests on gitlab.example.com repositories, driving them to a truly mergeable state. Automatically generates User Story documentation, constructs MR descriptions (with blob links), pushes and creates MRs, polls CI pipeline status via API and fixes failures, resolves merge conflicts, and loops until all MR checks pass with no conflicts. Triggers when the user says "submit MR", "create MR", "push and create MR", "merge to main", or needs to submit the current branch for review.
---

# GitLab MR

Create an MR and drive it to a **truly mergeable** state (all CI green + no merge conflicts). Core principle: **write documentation first, then submit the MR, verify with APIs, and loop through fixes until the MR is mergeable.**

Prerequisite: The current repository's remote points to `gitlab.example.com`, and `glab` CLI is installed.

---

## Rules

1. **Never use the `skip-doc-check` label** — every MR must have a real documentation link
2. **User Story must be relevant to the MR changes** — CI checks relevance (`check:mr-us-relevance`); irrelevant links will be rejected
3. **Blob links must point to pushed files** — the branch name and file path in the link must exist on the remote
4. **Verify with APIs, don't guess** — confirm results at every step using `glab` commands

---

## Execution Flow

### Step 1: Check Prerequisites

```bash
# Confirm remote points to gitlab.example.com
git remote get-url origin

# Confirm current branch is not main/master
git branch --show-current

# Confirm no uncommitted changes
git status
```

If there are uncommitted changes, commit or stash them first.

### Step 2: Ensure Documentation Exists

The MR description must contain documentation links. CI performs two checks:
- `check:mr-documentation`: whether the link format is valid
- `check:mr-us-relevance`: whether the linked document is relevant to the MR changes

**Prefer GitLab blob links** pointing to documentation files within the repository.

#### 2a: Find or Create Documentation

Check whether related documentation already exists in the repository:

```bash
# Look for potentially related documents
ls docs/plans/ docs/04-user-stories/ 2>/dev/null
```

If no related documentation exists, create one for this MR:

- Place the document at `docs/plans/YYYY-MM-DD-<feature-name>.md` (design doc) or `docs/04-user-stories/<feature-name>.md` (User Story)
- The document content must **cover the core changes in this MR** (otherwise the relevance check will fail)
- The document does not need to be long, but must describe: what was done and why

#### 2b: Commit and Push Documentation

```bash
git add docs/plans/<doc-file>.md
git commit -m "docs: add <feature> design document"
```

### Step 3: Push the Branch

```bash
git push -u origin <branch-name>
```

### Step 4: Create or Update MR

#### Check if an MR already exists

```bash
glab mr list --source-branch <branch-name>
```

#### If no MR exists, create one

Analyze all commits in `git log main..HEAD` to write the MR title and description.

Blob link format: `https://gitlab.example.com/<group>/<project>/-/blob/<branch>/<filepath>`

- `<group>/<project>` parsed from `git remote get-url origin`
- `<branch>` is the current branch name
- `<filepath>` is the in-repo path to the document

```bash
glab mr create \
  --title "<concise title, <70 chars>" \
  --description "$(cat <<'EOF'
## Change Summary
<Summary based on all commits, 2-3 bullet points>

## Related Documentation
- User Story (required): https://gitlab.example.com/<group>/<project>/-/blob/<branch>/docs/plans/<doc>.md
- Tech Design: <fill if available, otherwise remove this line>

## Change Type
- [x] <corresponding type>
EOF
)" \
  --push
```

#### If an MR exists but the description lacks documentation links

```bash
glab mr update <mr-id> --description "$(cat <<'EOF'
<complete description with blob links>
EOF
)"
```

### Step 5: Wait and Check Pipeline

After creating/updating the MR, wait for the pipeline to trigger and complete.

```bash
# Wait for pipeline to start (usually takes a few seconds after push)
sleep 5

# Check pipeline status
glab ci status
```

If the pipeline is still running, wait and check again:

```bash
sleep 20
glab ci status
```

### Step 6: Handle Failed Jobs

If the pipeline fails, check which specific job failed:

```bash
# Get status of all jobs in the pipeline
glab api "projects/:id/merge_requests/<mr-iid>/pipelines" | python3 -c "
import sys,json
pipelines = json.load(sys.stdin)
if pipelines:
    pid = pipelines[0]['id']
    print(f'Latest pipeline: {pid}, status: {pipelines[0][\"status\"]}')
"
```

```bash
# View failed job logs
glab api "projects/:id/pipelines/<pipeline-id>/jobs" | python3 -c "
import sys,json
for j in json.load(sys.stdin):
    if j['status'] == 'failed':
        print(f'FAILED: {j[\"name\"]} (id={j[\"id\"]})')
"
```

```bash
# Get the tail of a failed job's log
glab api "projects/:id/jobs/<job-id>/trace" 2>&1 | tail -30
```

#### Common Failures and Fixes

| Failed Job | Cause | Fix |
|----------|------|---------|
| `check:mr-documentation` | MR description missing a valid documentation link | `glab mr update <id> --description "..."` to add blob links |
| `check:mr-us-relevance` | Document content is not relevant to MR changes | Edit the document to cover the MR's core changes, commit and push |
| `validate:skills` | SKILL.md format is non-compliant | Run `uv run python scripts/validate.py --skills` to fix locally |
| `validate:security` | Security scan detected an issue | Run `uv run python scripts/validate.py --security` to fix locally |
| Merge conflict | Branch conflicts with main | `git fetch origin main && git rebase origin/main`, resolve conflicts and force push |

After fixing:
- If the issue was in the MR description (`check:mr-documentation`): update the description then retry the job
- If the issue was in code/docs: commit the fix, push, and a new pipeline will trigger automatically

```bash
# Retry a failed job
glab ci retry <job-id>

# Or push a new commit to trigger a new pipeline
git push
```

### Step 7: Confirm MR Is Mergeable

After CI passes, also confirm the MR has no merge conflicts. **CI passing does not mean mergeable.**

```bash
glab ci status        # Confirm CI is all green
glab mr view <branch> # Confirm no merge conflict
```

If there are merge conflicts, resolve them (rebase onto main), force push, and wait for the new CI to pass.

**Loop through Steps 5-7 until both conditions are met: CI all green + no conflicts.**

Once the MR is truly mergeable, report the MR URL to the user.

---

## Examples

### Full Workflow Example

```
# Create MR
glab mr create --title "feat: add retry logic" --description "..." --push

# Loop until CI passes
glab ci status  # -> if failed, check logs, fix -> check again

# After CI passes, check merge status
glab mr view feat/add-retry-logic
# -> conflicts? rebase to resolve -> force push -> wait for new CI

# Final confirmation: CI all green + no conflicts -> report MR URL
```

---

## Bad/Good Examples

### Bad — Declaring done just because CI passed

```
glab ci status  # -> success
# -> "MR !42 is created, CI passed!"  <- but there's actually a merge conflict, cannot merge
```

### Bad — Posting an irrelevant link

```
glab mr create --description "User Story: .../README.md"  # unrelated to changes, CI will reject
```

### Good — Driving to a truly mergeable state

```
# Create MR -> poll CI and fix failures -> check merge status -> resolve conflicts -> confirm mergeable
```

---

## Notes

- Branch names containing `/` (e.g., `feat/my-branch`) are correctly handled by GitLab in blob links
- `glab ci status` shows the status of all jobs in the latest pipeline
- If the pipeline doesn't trigger for a long time, you can manually run: `glab ci run`
- After updating the MR description, you need to retry the failed job or wait for a new pipeline
