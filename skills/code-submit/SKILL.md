---
name: code-submit
description: Cross-platform code submission workflow - Lint check, non-destructive review, manual verification document, smart staging, clean commit, MR creation. Auto-detects project type (Android/iOS/backend) and adapts to the corresponding lint/build tools. Triggers when the user says "submit code", "prepare to submit", "submit", "start submission flow", or "code submit".
argument-hint: "--target=<target-branch> [--from=stage1-6] [--type=android|ios|backend]"
---

# Cross-Platform Code Submission Workflow

Chains 6 stages together, each with a user confirmation gate. Core principle: **lint first, review without changing logic, human verification as backstop, clean commit to production.**

Prerequisite: The current repository remote points to `gitlab.example.com` and `glab` CLI is installed.

---

## Parameter Parsing

Parse from `$ARGUMENTS`:
- `--target=<branch>`: Target branch (**required**), e.g., `--target=test/VH_2.92.0_20260310140519`
- `--from=<stage>`: Start from a specific stage (optional), values `stage1` through `stage6`, skipping earlier stages
- `--type=<android|ios|backend>`: Force a specific project type (optional, defaults to auto-detection)

If `--target` is not provided, **you must ask the user** for the target branch before continuing.

---

## Step 0: Project Type Detection

Auto-detect the current project type to determine which specific commands are used in subsequent stages.

### Detection Rules (by priority)

1. **Android**: `build.gradle` or `build.gradle.kts` exists AND `**/AndroidManifest.xml` exists
   - Lint: `./gradlew :<module>:lint --no-daemon`
   - Test directory pattern: `src/test/`, `src/androidTest/`
   - Excluded directories: `build/`, `.idea/`, `.gradle/`, `debugpanel/`, `*.iml`

2. **iOS**: `*.xcodeproj` or `*.xcworkspace` or `Package.swift` exists
   - Lint: `swiftlint lint --reporter json`
   - Test directory pattern: `*Tests/`, `*UITests/`
   - Excluded directories: `DerivedData/`, `.build/`, `Pods/`, `*.xcuserstate`

3. **Backend (by language)**:
   - **Java/Kotlin (Spring Boot)**: `pom.xml` exists OR (`build.gradle` without `AndroidManifest.xml`)
     - Lint: `./gradlew checkstyleMain` or `./mvnw checkstyle:check`
   - **Python**: `pyproject.toml` or `requirements.txt` exists
     - Lint: `ruff check .` or `flake8`
   - **Go**: `go.mod` exists
     - Lint: `golangci-lint run`
   - **Node.js**: `package.json` exists (without the above characteristic files)
     - Lint: `npm run lint` or `npx eslint .`

Output confirmation after detection:
```
Project type: Android (evidence: build.gradle + AndroidManifest.xml)
Lint command: ./gradlew :<module>:lint --no-daemon
Test directories: src/test/, src/androidTest/
```

If the user specified `--type`, skip auto-detection.

---

## Stage 1: Lint Check

> Goal: Run lint before code review to avoid repeated CI failures due to lint issues

### 1a. Detect Change Scope

```bash
TARGET_BRANCH="<from parameter parsing>"
git fetch origin "$TARGET_BRANCH" 2>/dev/null
CHANGED_FILES=$(git diff --name-only "origin/$TARGET_BRANCH"...HEAD)
```

If `CHANGED_FILES` is empty, notify the user "no changed files relative to the target branch" and terminate.

### 1b. Execute Lint (by project type)

**Android**:
1. Derive Gradle modules from changed file paths:
   - `app/src/...` → `:app`
   - `BaseLib/xxx/src/...` → `:BaseLib:xxx`
   - `ThirdPartLib/xxx/src/...` → `:ThirdPartLib:xxx`
   - Files that cannot be mapped → fall back to `:app:lint`
2. Execute for each changed module (timeout: 300000):
   ```bash
   ./gradlew :<module>:lint --no-daemon
   ```

**iOS**:
1. Filter changed `.swift` files
2. Execute:
   ```bash
   swiftlint lint --path <file1> --path <file2> --reporter json
   ```

**Backend**: Execute the lint command determined in Step 0 (timeout: 120000).

### 1c. Parse Results

**Android**: Read `build/reports/lint-results*.xml`, extract `severity="Error"` entries.
**iOS**: Parse SwiftLint JSON output for `severity: "error"` entries.
**Backend**: Parse the corresponding tool's output.

For each error, list: file path + line number + error type + description.

### 1d. Handle Errors

- **Has Errors**: Display the error list, attempt auto-fix for simple issues (import sorting, formatting, unused imports). Re-lint after fixing. If errors remain, list remaining issues and ask the user whether to continue (with risk warning).
- **No Errors**: Pass. Warnings are displayed but do not block.

### 1e. Gate

```
Lint check result: 0 errors, N warnings
Continue to Code Review?
```

Wait for user confirmation.

---

## Stage 2: Non-Destructive Code Review

> Goal: Quality review only — never alter the user's designed business flow

### 2a. Collect Changes

```bash
git diff "origin/$TARGET_BRANCH"...HEAD -- '*.kt' '*.java' '*.swift' '*.py' '*.go' '*.ts' '*.js' ':!*Test*' ':!*test*' ':!*spec*' ':!*Mock*'
```

Only review production code; exclude test files.

### 2b. Execute Review

Review the diff of each changed file, following these **inviolable rules**:

#### Absolutely Prohibited Modifications

The following represent the user's design decisions — **only raise questions, never modify**:

- **Control flow logic**: if/when/for/while/switch conditions and branch structure
- **API call order**: Call chain and sequence of network requests, database operations, SDK calls
- **State management**: Emission and subscription of StateFlow/LiveData/Combine/Redux/MobX state flows
- **Method signatures**: Parameter lists, return types, method names, access modifiers
- **Class hierarchy**: Inheritance relationships, interface implementations, protocol conformance, generic constraints
- **Business rules**: Price calculations, permission checks, flow transition conditions, data validation rules
- **Architecture decisions**: Design pattern choices, module partitioning, dependency injection approach, data flow direction

#### Allowed Suggestions (output as suggestions; user decides whether to adopt)

- Variable/method/class naming improvements
- Code style and formatting consistency
- Potential null pointer / resource leak / memory leak
- Performance issues (unnecessary object creation, N+1 queries, main thread blocking operations)
- Security risks (hard-coded keys, injection vulnerabilities, plaintext storage of sensitive data)
- Duplicate code reminders
- Missing error handling (supplement only within existing try-catch scope)
- Unclosed resources (Cursor, Stream, Connection)

### 2c. Output Suggestions

Categorized by priority:

```
══ Code Review Suggestions ══

CRITICAL (must address)
  1. [file:line] Description...

HIGH (strongly recommended)
  2. [file:line] Description...

MEDIUM (suggested improvement)
  3. [file:line] Description...

LOW (optional optimization)
  4. [file:line] Description...

Total N suggestions (CRITICAL: X, HIGH: X, MEDIUM: X, LOW: X)
```

If no issues are found, output "Code Review passed — no improvements needed."

### 2d. Gate

Display the suggestion list and ask the user:
```
Select suggestions to adopt (enter numbers like 1,3,5 or all or none):
```

- Selected suggestions: AI automatically applies changes to code
- When the user chooses to skip CRITICAL-level items: require additional confirmation "I understand the risk and choose to skip"
- After applying changes, display the diff for user confirmation

---

## Stage 3: Manual Verification Document Generation

> Goal: Generate a detailed review document (flow diagrams + architecture diagrams + key code) for final human review

### 3a. Analyze Changes

Read all changed files (`git diff "origin/$TARGET_BRANCH"...HEAD`) and analyze:
- Which classes/methods/functions were modified
- Which business modules are involved
- Data flow direction and inter-component call relationships
- Added/removed/modified public APIs

### 3b. Generate Review Document

File path: `docs/reviews/<branch-short-name>-review.md`

`<branch-short-name>` takes the last segment of the branch name, e.g., `bugfix/VH_2.92.0_20260310140519` → `VH_2.92.0_20260310140519`

Document content:

```markdown
# Code Review Document

> Branch: <current branch>
> Target: <target branch>
> Generated: <YYYY-MM-DD HH:mm>

## 1. Change Summary

| File | Change Type | Description |
|------|---------|------|
| path/to/File.kt | Added/Modified/Deleted | One-line description of the change |

Total N files changed, X lines added, Y lines deleted.

## 2. Business Flow Diagram

Use Mermaid flowchart to describe the **complete business flow involving the changes** (not just the changed parts, but the full flow context where the changes occur).
Use different colors to highlight changed nodes.

## 3. Architecture Diagram

Use Mermaid classDiagram to describe the class/interface relationships involved.
Or use sequenceDiagram for key interaction flows (e.g., network request chains, event propagation chains).

If changes span multiple modules, show inter-module dependency relationships.

## 4. Key Code

List the most critical code snippets (no more than 5), each with annotations explaining:
- The design intent of this code
- Why it was implemented this way
- Boundary cases to watch for

## 5. Risk Assessment

| Risk Item | Level (High/Medium/Low) | Description | Mitigation |
|--------|---------------|------|---------|

## 6. Manual Testing Recommendations

- [ ] Normal scenario: ...
- [ ] Error scenario: ...
- [ ] Boundary scenario: ...
- [ ] Regression scenario: ... (verify that unmodified related features are not affected)
```

### 3c. Gate

```
Review document generated: docs/reviews/<branch>-review.md
Please read and confirm: does the manual review pass?
```

**You must wait for explicit user confirmation before continuing.** This is the most important human verification checkpoint.

---

## Stage 4: Smart Staging

> Goal: Automatically exclude test/debug code; stage only files that need to be committed

### 4a. Scan Changes

```bash
git status --porcelain
```

List all modified, added, and deleted files.

### 4b. Classify Files

Classify each file based on project type:

#### Auto-Exclude (do not stage)

**Universal exclusions**:
- `.idea/`, `*.iml`, `local.properties`, `.DS_Store`
- `build/`, `out/`, `dist/`, `target/`
- `docs/reviews/*-review.md` (Stage 3 documents are for local reading only, not committed)

**Android additional exclusions**:
- New files under `src/test/` (except modifications to existing test files, e.g., updating tests for a bug fix)
- New files under `src/androidTest/`
- `debugpanel/` directory
- `.gradle/` directory

**iOS additional exclusions**:
- New files under `*Tests/`
- New files under `*UITests/`
- `DerivedData/`, `.build/`, `Pods/`
- `*.xcuserstate`, `*.xcuserdata`

**Backend additional exclusions**:
- New files under `tests/`, `test/`, `__tests__/`
- New `*_test.go`, `*.test.ts`, `*.test.js`, `*_test.py` files
- `venv/`, `node_modules/`, `__pycache__/`, `.pytest_cache/`

#### Needs Confirmation (content detection flagged as suspicious)

Scan **production code** files pending staging for the following suspicious patterns:

- Debug statements: `Log.d("test`, `print("debug`, `console.log("test`, `fmt.Println("debug`
- Hard-coded test IPs/URLs: `192.168.`, `10.0.0.`, `http://localhost` (except in config files)
- Temporary markers: `// TODO: remove`, `// FIXME`, `// HACK`, `// TEMP`, `// XXX`
- Debug flags: Newly added `BuildConfig.DEBUG` conditions, `#if DEBUG` blocks, `if __debug__` blocks

#### Normal Staging

Files not matched by the above rules.

### 4c. Display Staging Plan

```
══ Staging Plan ══

Will stage (N files):
  + path/to/Feature.kt
  + path/to/layout.xml
  ...

Will exclude (M files):
  - path/to/FeatureTest.kt (test file)
  - docs/reviews/xxx-review.md (review document, local only)
  ...

Needs confirmation (K files):
  ? path/to/Utils.kt — line 42 contains Log.d("test data")
  ...

Confirm staging? (for "needs confirmation" files, enter numbers to exclude)
```

### 4d. Gate

After user confirmation, stage files one by one with `git add <file>`. **Never use `git add -A` or `git add .`**.

---

## Stage 5: Clean Commit

> Goal: Rebase onto the latest target branch and generate a clean commit

### 5a. Rebase to Latest Target Branch

```bash
git fetch origin "$TARGET_BRANCH"
git rebase "origin/$TARGET_BRANCH"
```

**If there are conflicts**:
1. Run `git diff --name-only --diff-filter=U` to list conflicted files
2. For each conflicted file, show both sides' differences and suggest a resolution strategy
3. Assist the user in resolving conflicts
4. After user confirmation: `git add <resolved-file>` then `git rebase --continue`
5. If the user wants to abort the rebase: `git rebase --abort`

**Note**: Do not auto force-push after rebase; Stage 6 handles the unified push.

### 5b. Generate Changelog

```bash
git log "origin/$TARGET_BRANCH"..HEAD --oneline --no-merges
```

Group commits by type and format:

```
## Changelog

### Features
- <commit message>

### Bug Fixes
- <commit message>

### Refactoring
- <commit message>

### Other
- <commit message>
```

If there is only one commit, the changelog is that commit's description.

### 5c. Construct Commit Message

Analyze the staged file changes and generate a conventional commit message:

```
<type>(<scope>): <concise description>

<detailed explanation (optional, from changelog)>
```

- `type`: Inferred from change content (feat/fix/refactor/docs/test/chore/perf/ci/style)
- `scope`: Module name inferred from changed file paths
- Description: One-line summary of the change purpose

### 5d. Gate

```
══ Commit Preview ══

Commit message:
  feat(payment): add retry logic for Stripe payment

  - Add exponential backoff for failed payments
  - Handle network timeout gracefully

Staged files (N):
  M path/to/PaymentRetry.kt
  A path/to/RetryPolicy.kt
  ...

Confirm commit? (Y=commit / edit=edit message / n=cancel)
```

After user confirmation, execute:
```bash
git commit -m "<message>"
```

---

## Stage 6: MR Creation

> Goal: Create an MR with complete documentation and drive it to mergeable

### 6a. Push Branch

```bash
git push -u origin "$(git branch --show-current)" --force-with-lease
```

Uses `--force-with-lease` (since Stage 5 performed a rebase) — safer than `--force`.

### 6b. Prepare MR Documentation

1. Check if `docs/plans/` or `docs/04-user-stories/` contains documentation related to this change
2. If not:
   - Based on Stage 3's review document "Change Summary" and "Business Flow Diagram" sections, create a condensed version
   - Path: `docs/plans/YYYY-MM-DD-<feature-name>.md`
   - Content must cover this MR's core changes (CI checks for relevance)
3. Commit and push the document:
   ```bash
   git add docs/plans/<doc>.md
   git commit -m "docs: add <feature> design document"
   git push
   ```

### 6c. Create MR

Construct the blob link: Parse group/project from `git remote get-url origin`, concatenate with branch name and file path.

```bash
glab mr create \
  --title "<Stage 5 commit title>" \
  --description "$(cat <<'EOF'
## Changelog

<changelog generated in Stage 5>

## Related Documents

- Design document: <GitLab blob link to docs/plans/ document>

## Change Type

- [x] <corresponding type: Bug fix / New feature / Refactoring / ...>
EOF
)" \
  --target-branch "$TARGET_BRANCH"
```

If an MR already exists, use `glab mr update` to update the description.

### 6d. CI Polling (reuses gitlab-mr skill logic)

```bash
sleep 5
glab ci status
```

Poll pipeline status and handle common failures:

| Failed Job | Fix Approach |
|----------|---------|
| `check:mr-documentation` | Update MR description, add blob link |
| `check:mr-us-relevance` | Modify document content to cover MR changes |
| Merge conflict | `git fetch && git rebase && git push --force-with-lease` |
| Other | Display failed job logs, provide fix suggestions |

Loop until CI is all green + no conflicts, or report issues that cannot be auto-fixed.

### 6e. Completion Report

```
══ Submission Complete ══

MR: https://gitlab.example.com/xxx/project/-/merge_requests/XXX
CI: Passed / Running / Failed (details...)
Document: <blob link>
Changelog:
  - feat: ...
  - fix: ...
```

---

## Notes

- `./gradlew` and `xcodebuild` commands are set with `timeout: 300000` (5 minutes)
- Stage files one by one with `git add` — **never use `git add -A` or `git add .`**
- Both rebase conflicts and force push require user confirmation
- Stage 3 review documents are for local reading only and are not committed to remote
- Stage 6 MR documents are a separate condensed design document committed to remote
- Blob link branch names and file paths must point to already-pushed files
- When using `--from=stageN` to skip earlier stages, skipped stages are marked "skipped" in the final report
- Every stage's gate must wait for explicit user confirmation — auto-skipping is not allowed

---

## Examples

### Good Example — Full Workflow Execution

```
User: /code-submit --target=test/VH_2.92.0_20260310140519

AI: Project type: Android (evidence: build.gradle + AndroidManifest.xml)

══ Stage 1: Lint Check ══
Changed modules: :app, :BaseLib:payment
Running ./gradlew :app:lint :BaseLib:payment:lint ...
Lint check result: 0 errors, 3 warnings
Continue to Code Review?

User: Y

══ Stage 2: Code Review ══
CRITICAL (must address)
  1. [PaymentRetry.kt:42] Unclosed Cursor — query result in fetchPaymentHistory() is not closed
HIGH (strongly recommended)
  2. [PaymentRetry.kt:78] Variable naming — `d` should be renamed to `retryDelay`
Total 2 suggestions
Select suggestions to adopt:

User: all

[Applying changes...]

══ Stage 3: Manual Verification Document ══
Review document generated: docs/reviews/VH_2.92.0_20260310140519-review.md
Please read and confirm: does the manual review pass?

User: Y

══ Stage 4: Smart Staging ══
Will stage (5 files):
  + app/src/main/.../PaymentRetry.kt
  + app/src/main/.../RetryPolicy.kt
  ...
Will exclude (2 files):
  - app/src/test/.../PaymentRetryTest.kt (test file)
  - docs/reviews/VH_2.92.0_20260310140519-review.md (review document)
Confirm staging?

User: Y

══ Stage 5: Clean Commit ══
Commit message: feat(payment): add retry logic for failed payments
Confirm commit?

User: Y

══ Stage 6: MR Creation ══
MR: https://gitlab.example.com/team/my-project/-/merge_requests/456
CI: Passed
```

### Bad Example — Review Modifies Business Logic

```
# BAD: Code Review stage directly modified the user's if-condition logic
AI: I have changed line 35 of PaymentRetry.kt from `if (retryCount < 3)` to `if (retryCount < 5)`
    because 3 retries might not be enough.

# GOOD: Only raise suggestions without directly modifying
AI: MEDIUM
  3. [PaymentRetry.kt:35] Retry count — current maxRetry=3; may be insufficient for unstable networks.
     Consider whether to adjust. (Note: this is a business decision, for reference only)
```

### Bad Example — Using git add -A for Staging

```
# BAD: Stage all files at once
git add -A
git commit -m "feat: add payment retry"

# GOOD: Stage files individually, excluding test and debug files
git add app/src/main/.../PaymentRetry.kt
git add app/src/main/.../RetryPolicy.kt
git commit -m "feat(payment): add retry logic for failed payments"
```
