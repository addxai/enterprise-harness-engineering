---
name: dev-workflow
description: Standard R&D process orchestrator — guides the full development lifecycle from User Story to CD. Invoke when user says "start a new feature", "new requirement", "我要开发一个新功能", "开始需求", "next step?", "研发流程", or resumes work on an existing feature. Also invoke proactively when any non-trivial feature work begins, even if the user just says "let's build X". Do NOT invoke for one-off bug fixes, hotpatches, or purely exploratory tasks with no deliverable.
---

# Dev Workflow

## Description

Standard R&D process orchestrator — guides the full development lifecycle from User Story to CD, with human confirmation required before proceeding to each step.

**Collaboration with other skills**: This skill is responsible for "what step are we on, what's next, and which skill to invoke"; `architect` handles "how to write the actual documents."

Every run must walk through the entire 9-step checklist — whether it is a new requirement, a new project, or a project already in progress — to ensure no critical step is missed (especially observability plans and test coverage).

---

## Rules

1. **Mandatory full checklist**: Every run must go from Step 1 to Step 9; no step may be skipped, even if its status is "Completed"
2. **Human confirmation at each step**: After displaying the status of each step, wait for human confirmation (`[y/N]`) before proceeding to the next
3. **Observability is not optional**: Step 5 (observability plan) is a required step and must not be skipped with "not needed for now"
4. **Documentation before code**: Before Step 6 (TDD implementation), all documentation deliverables from Steps 1-5 must exist and be confirmed
5. **First-run initialization**: When the project has no `CLAUDE.md` or no workspace skill, automatically run project initialization
6. **All User Stories must have E2E coverage**: In Step 4's test plan, every User Story must have a corresponding L3 E2E test case

---

## Examples

### Bad — Skipping undiscovered missing steps

```
User: "Code is all done, MR is merged, help me set up CD"
AI: Directly discusses CD configuration...
```

Problem: Skipped the observability plan (Step 5), test plan check (Step 4), etc., jumping directly to the step the user mentioned.

### Good — Enforced full checklist

```
User: "Code is all done, MR is merged, help me set up CD"
AI:
── Step 1 — User Story ──────────────
Status: Completed
Deliverable: docs/product/user-stories/postcard.md

Do you want to update this step? [y/N (default: skip)]

...(Steps 2-4 display status similarly)...

── Step 5 — Observability Plan ──────────────
Status: Missing
Deliverable: docs/architecture/postcard/observability.md — does not exist

Do you want to update this step? [y/N (default: skip)]
```

Even if the user says "code is done," the observability plan must still be checked for existence.

### Bad — Triggering the full workflow for a simple bug fix

```
User: "Fix the login button color bug"
AI: Triggers dev-workflow, starts from Step 1 with User Story writing...
```

Problem: A single-line bug fix does not need the full R&D workflow; over-orchestration disrupts the user.

### Good — Recognizing scope boundaries and avoiding over-triggering

```
User: "Fix the login button color bug"
AI: Directly fixes the bug following the project's Bug Fix TDD rules (write a failing test first, then fix).
Does not trigger dev-workflow.
```

### Bad — Skipping Step 2.5 for UI features

```
User: "I want to build a new Postcard sharing page"
AI: After Step 2 tech design is done, jumps directly to Step 3 dev environment...
```

Problem: There is a UI change but the Paper design mockup is skipped; the visual approach is not aligned before development, risking repeated rework.

### Good — Triggering Step 2.5 when there are UI changes

```
User: "I want to build a new Postcard sharing page"
AI: After Step 2 completes →
── Step 2.5 — UI Design Confirmation ──────────────
Status: Missing (detected that this requirement includes UI changes)
Trigger paper-ui-design skill to complete the design mockup in Paper...
```

---

## First-Time Project Entry (Project Initialization)

### Generate Project-Level Workspace Skill

Generate a project-specific development guide skill at `.agents/skills/{project-name}-workspace/SKILL.md`. This skill enables new Claude instances (or new engineers) to quickly understand all key project information.

**Trigger condition**: First time running `dev-workflow` in the project, or when `.agents/skills/{project-name}-workspace/` does not exist.

**Information sources**: Collect from the following locations:
- `docs/architecture/overview.md` — System architecture
- `docs/architecture/domain-model.md` — Business terminology
- `docs/architecture/tech-stack.md` — Tech stack
- `docs/deployment/local-dev.md` — Local dev environment
- `CLAUDE.md` — Project rules
- `Makefile` or `package.json` — Common commands

**Generated Workspace Skill structure**:

```markdown
---
name: {project-name}-workspace
description: {Project Name} project development guide. Automatically triggered when working in the {project-name} project.
  Contains project architecture, local environment startup, core business terms, common commands, and development conventions.
  New developers or Claude instances entering the project must invoke this skill first.
---

# {Project Name} Development Guide

## Project Overview
[Extracted from docs/architecture/overview.md]

## Quick Start
[Extracted make commands from docs/deployment/local-dev.md]

## Tech Stack
[Extracted from docs/architecture/tech-stack.md]

## Core Business Terms
[Extracted from docs/architecture/domain-model.md]

## Directory Structure
[Auto-scanned and generated]

## Development Standards
[Extracted from CLAUDE.md + dev-workflow rules]

## Common Commands Quick Reference
[Extracted from Makefile / package.json]
```

**Location**: `.agents/skills/{project-name}-workspace/SKILL.md` (project-level, committed to Git)

**Update timing**: After completing major documentation changes in Steps 1-4, update the workspace skill to keep it in sync.

---

Write the following base rules into the project's `CLAUDE.md` (skip if these rules already exist):

```markdown
## Dev Workflow Rules

- All user stories MUST have E2E test coverage (L3 level). No User Story can be marked "implemented" without a corresponding passing E2E test.
- Follow the 9-step dev workflow: User Story → Tech Design → UI Design* → Dev Env* → Test Strategy → Observability → TDD Impl → MR → CI → CD (* conditional)
- Documents must be committed before coding starts (architect rule)
```

---

## Full-Process Checklist (must be executed every time)

**Whether it is a new requirement, a new project, or a project already in progress, every run must walk through Step 1 to Step 9 and confirm each step.**

For each step, first scan the corresponding paths to determine the current status, then display the status and request confirmation:

| Status | Meaning | Action |
|------|------|------|
| Completed | Document/deliverable exists and content is complete | Display summary, ask if update is needed |
| Needs Update | Document exists but does not match current requirements | Trigger the corresponding skill to update |
| Missing | Document/deliverable does not exist | Trigger the corresponding skill to create from scratch |

Each step must receive human confirmation ("continue to next step?") before proceeding, even if the status is "Completed." This ensures every step receives conscious review rather than being automatically skipped.

---

## Step 1 — User Story

**Goal**: Define user experience flows and acceptance criteria (no technical details).

**Actions**:
1. Ask the user if they have a Feishu document link. If so, invoke `lark-mcp` to read the document content as input.
2. Invoke `story-craftsman` for guided requirements discovery and AC definition.
3. If brainstorming is needed, invoke `superpowers:brainstorming`.
4. Write deliverables to `docs/product/user-stories/{service}.md` (following `architect` Step 1 standards).

**Completion criteria**: Each User Story has Background + User Story + AC (Given/When/Then), with **no** technical implementation details.

**Write to CLAUDE.md after completion** (if not already present):
```
- User stories location: docs/product/user-stories/
- Each User Story must have AC in Given/When/Then format
```

**Confirmation**: Display the User Story list and ask "User Stories complete, proceed to Step 2 (Tech Design)?"

---

## Step 2 — Technical Design

**Goal**: Establish architecture boundaries, terminology SSOT, and key design decisions.

**Actions**:
1. Invoke `superpowers:brainstorming` to explore architecture options (2-3 options + recommendation).
2. Invoke `superpowers:writing-plans` to convert the plan into an implementation plan.
3. Write deliverables to `docs/architecture/overview.md` + `docs/architecture/domain-model.md` (following `architect` Step 2 standards).
4. Invoke `doc-writing` to refine documents using the HWPR/AWOR framework.

**Completion criteria**: Architecture diagram (Mermaid) + component responsibilities table + terminology mapping, single file ≤ 400 lines.

**Confirmation**: Ask "Tech design complete, proceed to Step 2.5 (UI Design Confirmation)?"

---

## Step 2.5 — UI Design Confirmation (Conditional Trigger)

**Trigger condition**: This feature includes user interface changes (mobile pages, modals, cards, detail pages, etc.). If there are no UI changes, **skip** this step.

**Goal**: Before technical implementation, complete UI design in Paper based on User Stories and Design System Tokens, and output a component specification document to ensure the visual approach is aligned before development.

**Actions**:
1. Invoke `paper-ui-design` skill, completing the full Phase 1 + Phase 2 workflow:
   - Read relevant User Story documents and tokens from `~/.claude/skills/paper-ui-design/ds_token.md`
   - Guide the user to open the Paper component library (optional skip)
   - Create a new Page in Paper and incrementally build the UI design mockup organized by visual groups
   - Take screenshots every 2-3 steps, evaluate against 7-item Review Checkpoint and fix issues
   - Call `finish_working_on_nodes` for finalization
2. After the user confirms the design in Paper, create or update `docs/ui/ui-implementation-strategy.md` in the project:
   - Add a separate section for this interface
   - List all components and controls, noting for each: UI component mapping, design system token correspondence
   - Follow the existing file format (if the file already exists, append the new interface section at the end; do not overwrite existing content)

**Completion criteria**:
- Paper design mockup is complete and passes all 7 Review Checkpoints
- `docs/ui/ui-implementation-strategy.md` has been created or updated with all component specifications for this UI

**Confirmation**: Ask "UI design confirmed, proceed to Step 3 (Dev Environment)?"

---

## Step 3 — Dev/Test Environment (Conditional Trigger)

**Trigger condition**: The project has no existing dev/test environment, **or** new infrastructure dependencies (database, message queue, new service) or new third-party dependencies have been introduced.

If none of the above applies, **skip** this step.

**Actions**:
1. Invoke `multi-worktree-dev` to design the L1/L2/L3 layered local environment plan.
2. Write deliverables to `docs/deployment/local-dev.md` (following `architect` Step 3 standards).

**Completion criteria**: `make dev-up` / `make dev-down` are functional, and multiple worktree ports do not conflict.

**Confirmation**: Ask "Dev environment design complete, proceed to Step 4 (Test Plan)?"

---

## Step 4 — Test Plan

**Goal**: Generate an L2-L4 layered testing strategy where all User Story acceptance criteria have corresponding test cases.

**Actions**:
1. Invoke `testing-strategy` to generate a complete layered plan based on project type (Backend+APP / Backend+WEB / Backend+APP+Embedded).
2. Confirm that every User Story AC has L3 (E2E) test case coverage (**hard requirement**).
3. Write deliverables to `docs/testing/strategy.md` and `docs/testing/services/{service}/` (following `architect` Step 5 standards).

**Completion criteria**: L1 (unit) + L2 (integration) + L3 (E2E) + L4 (UAT) strategy is complete; User Story count = L3 test case count (1:1 correspondence).

**Write to CLAUDE.md after completion** (if not already present):
```
- L3 E2E tests are mandatory for every user story AC
- Test files location: docs/testing/
```

**Confirmation**: Ask "Test plan complete, proceed to Step 5 (Observability Plan)?"

---

## Step 5 — Observability Plan

**Goal**: Before coding, define a measurement and observation system that is runnable, verifiable, and optimizable. Output a structured, executable, and traceable Observability Plan.

Execute the following 7 sub-steps in order; have the user confirm each sub-step's output before proceeding.

---

### 5.0 Scope & Classification

Read project information from `docs/architecture/overview.md`. If the file does not exist, infer first, then have the user confirm:

| Item | Description |
|------|------|
| Services/modules involved | Which services does this requirement affect |
| Business priority | P0 / P1 / P2 |
| Is it a core conversion path | Affects payment/activation/retention or other core funnels |
| Is A/B experimentation needed | Based on the A/B experiment platform |
| Is it a high-risk chain | Large failure blast radius, irreversible data, etc. |

Output the scope confirmation table and wait for user confirmation before continuing.

---

### 5.1 Measurement Design

Define a `measurement_id` for this requirement. Format: `{feature}_{action}_v{n}`, e.g., `postcard_share_activation_v1`.

Guide the user through the following (provide suggestions based on understanding of the requirement first; user confirms or corrects):

**Business objectives (based on the overall requirement, not individual User Story)**:
- What is the core product/business question?
- What are the key business KPIs?
- Define the critical path (for funnel definition)

**If A/B experimentation is needed (based on the A/B experiment platform)**, additionally define:

| Field | Description |
|------|------|
| `feature_flag` | Feature ID in the A/B experiment platform |
| `experiment_id` | Experiment ID |
| `targeting` | Who enters the experiment |
| `variant` | Experiment groups |
| `exposure` definition | Exposure timing (automatic or manual tracking at key scenarios) |
| `primary_metric` | Primary metric |
| `guardrail_metrics` | Guardrail metrics (optional) |

Proceed after user confirms the Measurement Design.

---

### 5.2 Event Tracking Design

1. Confirm which new user behavior event tracking is needed for this User Story.
2. Present all candidate events in a table for user confirmation:

| event_name | Category | Strategy | Description |
|------------|------|------|------|
| `xxx_viewed` | Impression | reuse / extend / new | ... |
| `xxx_clicked` | Behavior | reuse / extend / new | ... |
| `xxx_completed` | Outcome | reuse / extend / new | ... |

**Each event must be evaluated as**:
- **reuse existing event** — Fully reuse an existing event
- **extend properties** — Reuse the event but add new properties
- **create new event** — Create a new event only when necessary

**Design each new/extended event structure according to the event tracking schema**:

```
event_name:    xxx_yyy
classification: Impression / Behavior / Outcome
properties:
  - key: value_type  # Description
context:
  - user_id
  - session_id
  - feature_flag (if applicable)
ownership: Defaults to the user's team
```

After user confirms the event tracking plan, create a ticket in the event management platform for the review and release process.

---

### 5.3 Logging Strategy

Based on the requirement, define structured logs for critical business paths. Follow these principles:

- Only log **critical business paths** — use "event nodes" as the unit; not every function needs logging
- Use structured fields: `service` / `trace_id` / `user_id` / `action` / `result`
- Log levels: `INFO` (normal flow) / `WARN` (abnormal but recoverable) / `ERROR` (requires intervention)
- Correlation is required: `trace_id` + `user_id`
- **Prohibited**: Logging user privacy information (name, address, personal ID, etc.)

Output the log node list for user confirmation:

| Node | Level | action | result | Notes |
|------|-------|--------|--------|------|
| Create postcard | INFO | postcard_create | success/fail | Includes brand_id |
| ... | ... | ... | ... | ... |

---

### 5.4 Tracing & Metrics

Based on the technical architecture, map the system's critical chains and design OTel instrumentation for key nodes/APIs:

**Technical metrics (is the system running normally)**:

| Metric | Type | Description |
|------|------|------|
| `http_request_duration_seconds` | Histogram | Key API latency |
| `http_requests_total{status}` | Counter | Request volume & error rate |
| `{feature}_operation_total{result}` | Counter | Core operation success/failure |

**Business metrics (are KPIs being met)**:

Map the KPIs from 5.1 to computable metrics:

| KPI | metric_name | Calculation |
|-----|-------------|---------|
| Share completion rate | `postcard_share_completed_total` | success / attempt |
| ... | ... | ... |

Output the plan for user confirmation.

---

### 5.5 Alerts & SLO

Define SLOs (internal targets) based on the system framework and set alert rules:

**Severity levels**:
- **P0 Critical**: Service unavailable / core feature down, immediate intervention
- **P1 High**: Severe impact but not fully unavailable, respond within 30 minutes
- **P2 Medium**: Issues but not urgent, handle during business hours
- **P3 Low**: Informational / observational

1. Invoke `prometheus` to review existing alert rules and confirm whether new PromQL alerts are needed.
2. Output the alert plan for user confirmation:

| Alert Name | PromQL | Threshold | Severity | Description |
|-----------|--------|------|----------|------|
| `HighErrorRate` | `rate(errors[5m]) / rate(total[5m])` | > 1% | P1 | ... |
| ... | ... | ... | ... | ... |

---

### 5.6 Dashboards

Invoke `grafana` to confirm whether new panels need to be added to dashboards:

| Panel | Content | Applicable When |
|-------|------|---------|
| KPI panel | Core business metric trends | Required |
| Funnel panel | Critical path funnel | Required |
| Experiment panel | Experiment group comparison | Only for A/B experiments |
| Service metrics panel | rate / error / latency | Required |

---

### 5.7 Documentation Output

Write all deliverables from 5.0-5.6 to:

```
docs/architecture/{service}/observability.md
```

Document structure:
```markdown
# Observability Plan — {feature} ({measurement_id})

## Scope & Classification
## Measurement Design
## Event Tracking
## Logging Strategy
## Tracing & Metrics
## Alerts & SLO
## Dashboards
```

---

**Completion criteria**:
- Measurement goal is clear; KPIs can be computed from the defined events
- Core funnel definition is complete
- Necessary events are designed (reuse preferred; do not proliferate new events)
- Critical paths have trace + metrics
- Core SLAs have alert coverage
- Support for experiment groups (if applicable)
- `observability.md` has been committed

**Write to CLAUDE.md after completion** (if not already present):
```
- Observability: event tracking + OTel + Prometheus alerts
- Observability docs: docs/architecture/{service}/observability.md
```

**Confirmation**: Ask "Observability plan complete, proceed to Step 6 (TDD Implementation)?"

---

## Step 6 — TDD Implementation

**Goal**: Test-first implementation of all features, preferring Claude Code agent teams for parallel execution.

**Actions**:
1. Display the implementation plan (from Step 2's writing-plans deliverable) and ask the user:
   - Which tasks can run in parallel?
   - Which tasks must run sequentially?
2. Based on user confirmation:
   - **Parallel tasks**: invoke `superpowers:dispatching-parallel-agents`
   - **Sequential / current session**: invoke `superpowers:subagent-driven-development`
3. Each task follows `superpowers:test-driven-development` (write tests first, then implement).

**Completion criteria**: All User Story L3 E2E tests pass; L1/L2 tests pass; no broken tests.

**Confirmation**: Ask "Implementation complete, proceed to Step 7 (MR)?"

---

## Step 7 — MR

**Goal**: Create a Merge Request and drive it to a mergeable state.

**Actions**:
1. Invoke `gitlab-mr` (auto-generates document links, pushes, creates MR, polls CI status, fixes failures).

**Completion criteria**: MR created successfully, CI all green, no merge conflicts.

**Confirmation**: Ask "MR created, proceed to Step 8 (CI Configuration)?"

---

## Step 8 — CI

**Goal**: Configure or update the CI pipeline to ensure complete quality gates.

**Actions**:
1. Invoke `gitlab-ci` to check/create `.gitlab-ci.yml`.
2. Ensure the following CI stages exist: lint → test (including L1/L2) → build → E2E (L3).
3. Write deliverables to `docs/deployment/ci.md` (following `architect` Step 6 standards).

**Completion criteria**: CI pipeline all green; L3 E2E runs in CI.

**Confirmation**: Ask "CI configuration complete, proceed to Step 9 (CD)?"

---

## Step 9 — CD

**Goal**: Configure continuous deployment to ensure automatic deployment to the target environment after MR merge.

**Actions**:
1. Invoke `argocd` to check current application deployment status.
2. Invoke `cicd-developer` to configure K8s/ArgoCD deployment strategy.
3. If a new cluster / full CICD stack is needed, invoke `argocd-deploy`.
4. Write deliverables to `docs/deployment/cd.md` (following `architect` Step 6 standards).

**Completion criteria**: Merge to main automatically triggers deployment; staging environment verification passes.

**Write to CLAUDE.md after completion** (if not already present):
```
- CD via ArgoCD, check docs/deployment/cd.md for deployment guide
```

**Completion**: Congratulations! The entire R&D workflow is complete. Ask the user if there are follow-up needs.

---

## Flow Diagram

```
New feature ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  Step 1       Step 2       Step 2.5*    Step 3*      Step 4         Step 5          Step 6
  User Story → Tech     →  UI Design →  Dev Env   →  Test       →  Observability →  TDD Impl
  (story-      Design      (paper-ui-    (multi-       Strategy       (tracker-        (TDD +
  craftsman +  (brainstorm  design +     worktree-    (testing-       manager +        agents)
  lark-mcp)    + write-     docs/ui/)    dev)          strategy)      prometheus +
               plan +                                                 grafana)
               doc-writing)
                                              │
Re-entering ── status check ─────────────── resume from breakpoint ──────────────────────────────────────────────────────────

  Step 7       Step 8       Step 9
  MR        →  CI        →  CD
  (gitlab-mr)  (gitlab-ci)  (argocd +
                             cicd-developer)

* Step 2.5 only triggered when the feature includes UI changes
* Step 3 only triggered when there are new dependencies or no existing dev environment
```

---

## Per-Step Confirmation Template

At the start of each step, display the current status; after completion, request confirmation. Always use the following format:

**Entering each step:**
```
── Step N/9 — [Step Name] ──────────────────
Status: Completed / Needs Update / Missing
Deliverable: [document path] — [one-line summary or "does not exist"]

Do you want to update this step? [y/N (default: skip)]
```

**After completion or skip:**
```
Step N confirmed → Proceeding to Step N+1 — [Step Name]
```

**After all steps are complete:**
```
══════════════════════════════════════
Full R&D Workflow Checklist Complete

Confirmed steps:
  Step 1   — User Story
  Step 2   — Technical Design
  Step 2.5 — UI Design Confirmation (with docs/ui/ui-implementation-strategy.md) [conditional]
  Step 3   — Dev Environment [conditional]
  Step 4   — Test Plan
  Step 5   — Observability Plan
  Step 6   — TDD Implementation
  Step 7   — MR
  Step 8   — CI
  Step 9   — CD
══════════════════════════════════════
```
