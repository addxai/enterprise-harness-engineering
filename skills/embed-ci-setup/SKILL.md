---
name: embed-ci-setup
description: Quickly create a CI Pipeline for embedded repositories (SonarQube incremental C-language scanning). Triggers when the user says "add a Pipeline to this repo", "create CI configuration", "integrate SonarQube", "embedded project needs a Pipeline", or when a repo has no .gitlab-ci.yml and cannot merge MRs.
---

# embed-ci-setup

Quickly create a GitLab CI Pipeline for embedded (C language) repositories with SonarQube incremental code scanning.

## Description

Embedded team rule: Repositories without a Pipeline cannot merge MRs. This Skill helps embedded engineers create a standard CI Pipeline for their repository within minutes, including:

- MR-triggered SonarQube incremental scanning (scans only `.c` / `.h` files changed in this MR)
- Quality Gate check (shows a warning on failure, does not block the MR)
- Dynamically generated `sonar-project.properties` (project key auto-generated from the repository path)

**Applicable scenarios:**

- Embedded repository has no Pipeline and needs one quickly
- Existing `.gitlab-ci.yml` repository needs SonarQube scanning added
- All embedded projects primarily using C language

**Not applicable:**

- Non-C language projects (Go, Python, Java, etc. should use the global SonarQube template)
- CI workflows requiring compilation builds (this Skill only does source-code static scanning)

## Rules

### Rule 1 — Environment Constraints (must understand)

All embedded repositories run CI on the company's unified GitLab platform, with these constraints:

| Constraint | Description |
|------|------|
| CI entry point | Managed by `your-org/ci-templates`'s `entrypoint.yml`, which auto-includes the business repository's `.gitlab-ci.yml` |
| Custom stages prohibited | Do not declare `stages:` in `.gitlab-ci.yml`; use GitLab default stages. Custom stages that do not include `test` will cause pipeline creation failures |
| include method | Must use `include: project` rather than `include: local`, because the CI entry point is in an external repository and `local` resolves to the wrong repository |
| Runner tag | Use `sonar-scanner` |
| Docker image | Must specify `image: harbor.example.com/tools/embed-quality:v1.2.0`; runner uses Kubernetes executor |
| SonarQube token | Injected via GitLab CI/CD Variable `SONAR_USER_TOKEN`; project admin must configure in advance |
| SonarQube server | `https://sonarqube.example.com` |
| No heredoc in YAML | Do not use `<<EOF ... EOF` within `script: \|` blocks — it causes YAML parsing errors; use `echo` line by line instead |

### Rule 2 — Execution Flow

After receiving the user's request, execute the following steps:

**Step 1: Check current repository status**

```bash
# check if .gitlab-ci.yml exists
ls .gitlab-ci.yml 2>/dev/null

# check if ci/ directory exists
ls ci/sonar-analysis-embed.yml 2>/dev/null

# check if .gitignore has sonar-project.properties
grep "sonar-project.properties" .gitignore 2>/dev/null
```

**Step 2: Decide action based on check results**

| .gitlab-ci.yml | ci/sonar-analysis-embed.yml | Action |
|----------------|----------------------------|------|
| Does not exist | Does not exist | Create both files (Rule 3 + Rule 4) |
| Exists | Does not exist | Only create `ci/sonar-analysis-embed.yml` (Rule 4), add include to `.gitlab-ci.yml` (Rule 5) |
| Exists | Exists | Verify configuration is correct; no action needed |

**Step 3: Update .gitignore**

If `.gitignore` does not contain `/sonar-project.properties`, add it.

**Step 4: Prompt user to check GitLab CI/CD Variables**

Inform the user to confirm that `SONAR_USER_TOKEN` is configured in the project's GitLab **Settings → CI/CD → Variables**.

### Rule 3 — Generate .gitlab-ci.yml (when no existing file)

When the repository has no `.gitlab-ci.yml`, generate the following content:

```yaml
include:
  - project: $CI_PROJECT_PATH
    ref: $CI_COMMIT_REF_NAME
    file: ci/sonar-analysis-embed.yml

default:
  tags:
    - sonar-scanner

pass:
  stage: test
  script:
    - echo "CI pass"
```

Key points:
- **Do not declare `stages:`**; use GitLab defaults
- The `pass` job uses `stage: test` to ensure the pipeline has a runnable job in non-MR scenarios
- `include` uses `project: $CI_PROJECT_PATH` + `ref: $CI_COMMIT_REF_NAME`

### Rule 4 — Generate ci/sonar-analysis-embed.yml

Create the `ci/` directory and generate the following file:

```yaml
# ============================================================================
# SonarQube Incremental Analysis Job
# Triggered on Merge Request events, scans only changed C files (.c/.h)
#
# Requires: SONAR_USER_TOKEN configured in GitLab CI/CD Variables
# ============================================================================

sonar-analysis:
  stage: test
  tags:
    - sonar-scanner
  image: harbor.example.com/tools/embed-quality:v1.2.0
  variables:
    GIT_DEPTH: "0"
    GIT_STRATEGY: fetch
    SONAR_AUTH_TOKEN: "${SONAR_USER_TOKEN}"
  before_script:
    - git config --global --add safe.directory "${CI_PROJECT_DIR}"
  script:
    - |
      echo "======================================"
      echo "SonarQube Incremental Analysis"
      echo "  Source: ${CI_MERGE_REQUEST_SOURCE_BRANCH_NAME}"
      echo "  Target: ${CI_MERGE_REQUEST_TARGET_BRANCH_NAME}"
      echo "======================================"

      # Step 1: collect changed C files (.c/.h), exclude deleted files
      TARGET_BRANCH="origin/${CI_MERGE_REQUEST_TARGET_BRANCH_NAME}"
      SOURCE_BRANCH="origin/${CI_MERGE_REQUEST_SOURCE_BRANCH_NAME}"
      CHANGED_FILES=$(git diff --name-only --diff-filter=d "${TARGET_BRANCH}...${SOURCE_BRANCH}" -- '*.c' '*.h' | paste -sd ',' -)

      if [ -z "${CHANGED_FILES}" ]; then
        echo "No C files (.c/.h) changed in this MR, skipping SonarQube analysis."
        exit 0
      fi

      echo "Changed C files:"
      echo "${CHANGED_FILES}" | tr ',' '\n' | sed 's/^/  - /'

      # Step 2: generate project key from CI_PROJECT_PATH
      # e.g. rockchip_rk3576/buildroot -> rockchip_rk3576-buildroot
      PROJECT_KEY=$(echo "${CI_PROJECT_PATH}" | tr '/' '-')
      echo "Project Key: ${PROJECT_KEY}"

      # Step 3: generate sonar-project.properties
      PROPS="${CI_PROJECT_DIR}/sonar-project.properties"
      {
        echo "sonar.projectKey=${PROJECT_KEY}"
        echo "sonar.projectName=${PROJECT_KEY}"
        echo "sonar.projectVersion=1.0"
        echo "sonar.sources=."
        echo "sonar.sourceEncoding=UTF-8"
        echo "sonar.language=c"
        echo "sonar.inclusions=${CHANGED_FILES}"
        echo "sonar.scm.provider=git"
        echo "sonar.host.url=https://sonarqube.example.com"
      } > "${PROPS}"

      echo "======================================"
      echo "Generated sonar-project.properties:"
      cat "${CI_PROJECT_DIR}/sonar-project.properties"
      echo "======================================"

      # Step 4: run sonar-scanner with quality gate check
      sonar-scanner -Dsonar.token="${SONAR_AUTH_TOKEN}" -Dsonar.qualitygate.wait=true
  allow_failure: true
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

### Rule 5 — Add include to existing .gitlab-ci.yml

When the repository already has a `.gitlab-ci.yml`, add the include configuration at the top of the file.

**Check items:**

1. If there is already an `include:` section, append one entry:
```yaml
include:
  # ... existing includes ...
  - project: $CI_PROJECT_PATH
    ref: $CI_COMMIT_REF_NAME
    file: ci/sonar-analysis-embed.yml
```

2. If there is no `include:` section, add at the very top of the file:
```yaml
include:
  - project: $CI_PROJECT_PATH
    ref: $CI_COMMIT_REF_NAME
    file: ci/sonar-analysis-embed.yml
```

3. **Do not modify** existing `stages:`, `default:`, other jobs, or any other configuration

### Rule 6 — Notify User After Completion

After generating files, output the following information:

```
Files generated:
  - .gitlab-ci.yml (created / include updated)
  - ci/sonar-analysis-embed.yml
  - .gitignore (sonar-project.properties added)

Before use, please confirm:
  1. SONAR_USER_TOKEN is configured in GitLab project Settings → CI/CD → Variables
  2. Commit these files to the branch; SonarQube scan will auto-trigger when an MR is created
  3. Scan results can be viewed at https://sonarqube.example.com
```

## Examples

### Bad

```
User: "Add a Pipeline to this embedded repo"
AI: Declares stages: [build, test, deploy] in .gitlab-ci.yml, uses include: local to reference files,
    and uses heredoc in the script to generate sonar-project.properties
→ Pipeline creation fails: stages missing test (ci:init requires it), include: local resolves to wrong repo, heredoc causes YAML parse error
```

```
User: "This repo already has .gitlab-ci.yml, help me add SonarQube"
AI: Overwrote the user's original .gitlab-ci.yml, removing existing job configurations
→ The user's existing CI workflow is broken
```

### Good

```
User: "Add a Pipeline to this embedded repo"
AI: Check finds no .gitlab-ci.yml → generates .gitlab-ci.yml (no stages declared, uses defaults)
    + ci/sonar-analysis-embed.yml (uses include: project, specifies image, echo writes properties)
    + .gitignore adds sonar-project.properties
    → Prompts user to check SONAR_USER_TOKEN configuration
```

```
User: "This repo already has .gitlab-ci.yml, help me add SonarQube"
AI: Check finds existing .gitlab-ci.yml, no ci/sonar-analysis-embed.yml
    → Only creates ci/sonar-analysis-embed.yml
    → Appends include at top of existing .gitlab-ci.yml without modifying other content
    → Prompts user to check SONAR_USER_TOKEN configuration
```
