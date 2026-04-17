# [Template] <Topic Name> - User Story

> Reference document (optional): <link or relative path 1> | <link or relative path 2>

```mermaid
flowchart TB
  %% Suggestion: split into "Core Flow + Involved Objects/Platforms" for better readability
  subgraph "Core Flow"
    A[Trigger / Input] --> B[Guidance / Preparation (optional)]
    B --> C[System / Flow Check (or Key Processing)]
    C -->|Pass| D[Continue Flow / Produce Output]
    C -->|Fail| E[Block / Prompt / Fallback Strategy]
  end

  subgraph "Involved Objects / Platforms (optional)"
    F[Role / User]
    G[System A]
    H[System B]
  end

  %% Optional: draw associations between platforms and core flow (remove unused lines)
  F -.-> A
  G -.-> C
```

## 1. Background (Why)

- <Pain point / Problem 1: what cost or risk does the current situation cause>
- <Pain point / Problem 2: who is affected and in what scenario>

## 2. Goals (What)

- <Goal 1: what outcome to achieve (verifiable)>
- <Goal 2: what metric/experience to improve (quantifiable is better)>

## 3. Roles (Who)

| Role | Responsibility |
|------|------|
| **<Role A>** | <What they do / what they care about> |
| **<Role B>** | <What they do / what they care about> |
| **<System/Platform> (optional)** | <What it does automatically> |

## 4. User Stories

> Writing tips: each User Story is one sentence + 3-6 acceptance criteria; aim for INVEST (especially Small/Testable).

### 4.1 US-<MODULE>-01: <User Story Title> [P0/P1/P2]

**As a** <role>, **I want to** <capability/need>, **so that** <value/purpose>.

**Acceptance Criteria (AC):**
- [ ] <Given/When/Then or checkable condition 1>
- [ ] <Condition 2>
- [ ] <Condition 3>

<!-- Optional: Notes
- Constraints: <permissions/network/platform limitations>
- Dependencies: <dependent systems/prerequisites>
- Risks: <false positives/false negatives/compatibility issues>
-->

### 4.2 US-<MODULE>-02: <User Story Title> [P0/P1/P2]

**As a** <role>, **I want to** <capability/need>, **so that** <value/purpose>.

**Acceptance Criteria (AC):**
- [ ] <Condition 1>
- [ ] <Condition 2>

<!-- If more User Stories, continue with 4.3/4.4... -->

## 5. Progress (optional)

| User Story | Status | Notes |
|---|---|---|
| US-<MODULE>-01 | Not started / In progress / Completed | <optional> |
| US-<MODULE>-02 | Not started / In progress / Completed | <optional> |

## 6. Change Log (optional)

| Date | Description |
|------|------|
| <YYYY-MM-DD> | Initial version |
