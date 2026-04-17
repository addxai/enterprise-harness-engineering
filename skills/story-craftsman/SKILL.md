---
name: story-craftsman
description: Professional User Story and documentation system construction. Assists in writing high-quality User Story documents through guided interviews to uncover requirements context and acceptance criteria, and places documents precisely in the standardized docs directory structure. Triggers when the user requests writing User Stories, describing feature requirements, or initializing project documentation structure.
---

# Story Craftsman

This skill embodies the "Everything is Code" engineering philosophy, helping you produce high-quality user stories and their supporting documentation alongside your MR submissions.

For the detailed example template, see [examples/TEMPLATE-UserStory.md](examples/TEMPLATE-UserStory.md).

---

## Rules

1. **Never fabricate information**: When information is insufficient, obtain context through guided interviews rather than filling in details yourself
2. **Architecture-aware placement**: Analyze file paths or `git status` to determine the relevant module and place documents in the corresponding `docs/04-user-stories/` directory
3. **Testable acceptance criteria**: Each AC must be a verifiable, checkable condition (Given/When/Then or clear checkbox)
4. **Consolidate questions**: During interviews, combine all missing dimensions into a single round of questions to avoid multi-round fragmented asking that causes user fatigue
5. **Path-first inference**: First attempt to infer the target sub-module from context; only ask the user when uncertain

---

## Execution Flow

### Feature A: Generate User Story

### Trigger Conditions

User requests "help me write a User Story," "describe this feature," "generate user story," etc.

### Step 1: Assess Information Sufficiency

After receiving a request, check whether the following three elements are present:

| Element | Meaning | Sufficiency Criteria |
|------|------|--------------------|
| **Background (Why)** | Current pain points, impact scope | Can articulate "who is affected in what scenario" |
| **Goals (What)** | Verifiable success metrics | Can articulate "what can be quantified after completion" |
| **Acceptance Criteria (AC)** | Key boundary scenarios | At least 2 checkable conditions are listed |

**If information is insufficient, execute Step 2 (interview); if sufficient, proceed directly to Step 3 (generation).**

### Step 2: Guided Interview Protocol

Take on the dual role of "detective" and "poet," asking all missing dimension questions in a single round (avoiding multi-round fragmented questions):

```
To generate a professional user story, I need you to confirm the following (keep it brief, 1-3 sentences per item):

1. **Background/Pain point**: [specific missing background question]
2. **Goal**: [specific missing goal question]
3. **Acceptance criteria**: [specific missing AC question]

You can describe briefly — I will handle converting it into the standard professional document format.
```

### Step 3: Generate User Story File

Strictly follow the structure from [TEMPLATE-UserStory.md](examples/TEMPLATE-UserStory.md) to generate the file.

**File naming convention**: `{feature-name}.md` (lowercase kebab-case)

**Placement path**: `{submodule_root}/docs/04-user-stories/{feature-name}.md`

If the target directory does not exist, first execute Feature B or prompt the user.

---

### Feature B: Initialize Standard Docs Structure

### Trigger Conditions

User explicitly requests "create docs structure," "initialize docs," etc.

### Standard Directory Structure

```
docs/
├── 01-product-research/    # Product research and competitive analysis
├── 02-system-design/       # System design and architecture decisions
├── 03-detailed-design/     # Detailed design documents
├── 04-user-stories/        # User Stories
└── 05-user-guide/          # User manuals and operation guides
```

### Execution Steps

1. Confirm the target root directory (ask the user or infer from context)
2. Create the 5 subdirectories listed above under the target root
3. Create a `.gitkeep` file in each subdirectory to ensure Git tracks empty directories
4. Generate `AGENTS.md` in the `docs/` root directory describing each directory's purpose

### Generated `docs/AGENTS.md` Content Template

```markdown
# docs/

This directory is the project documentation root, organized by R&D lifecycle stages.

## Directory Structure

- `01-product-research/`: Product research, competitive analysis, market insights
- `02-system-design/`: System architecture design, technology selection, ADR (Architecture Decision Records)
- `03-detailed-design/`: Module detailed design, interface specifications, data structures
- `04-user-stories/`: User Story files, naming convention: `{feature-name}.md`
- `05-user-guide/`: End-user operation manuals and usage instructions

## Maintenance Conventions

- User stories are created as individual `.md` files per feature module
- This file should be updated after architectural/directory-level changes
```

---

### Sub-Module Identification Logic

Analyze code changes or user descriptions to determine the target sub-module in the following order:

1. **Infer from file paths**: Top-level directory of changed files (e.g., `device-cloud-server/`, `frontend/`)
2. **Infer from git status**: Path prefixes in `git status` output
3. **Ask when uncertain**: If changes span multiple modules or paths are unclear, **must ask the user**

---

## Examples

### Bad

```markdown
## User Story: Alarm Filtering Feature

**As** a system administrator, **I want** to filter alarms, **so that** I can reduce distractions.

**Acceptance Criteria**:
- [ ] System supports filtering functionality
- [ ] Filtered alarms are not displayed after filtering
```

Problem: Missing background, ACs are too vague, unable to verify "what conditions trigger filtering."

### Good

```markdown
## User Story: Rule-Based Alarm Silence Filtering

**Background**: The monitoring system generates 500+ heartbeat probe alarms daily, causing
operator alert fatigue. Real fault alarms get buried, and average response time has increased
from 2 minutes to 15 minutes.

**As** an operations engineer, **I want** to configure alarm silence rules (by device type + alarm type combination),
**so that** known non-fault alarms are suppressed and real fault alarm response time returns to under 2 minutes.

**Acceptance Criteria**:
- [ ] Given a configured silence rule "device type=heartbeat probe AND alarm type=connection timeout,"
      When such an alarm fires, Then the Grafana dashboard does not display it and the audit log records "silenced"
- [ ] Given the silence rule configuration interface, When the admin saves a rule,
      Then the rule takes effect within 30 seconds without requiring a service restart
- [ ] Given an alarm matches both a silence rule and an escalation rule simultaneously,
      When the alarm fires, Then the silence rule takes priority, but the conflict is noted in the audit log
```

---

## Exemptions

| Scenario | Condition |
|------|------|
| Technical refactoring MR | No visible user-facing functionality change — may simplify to a brief technical note |
| Pure bug fix | Reference the corresponding Issue directly — full User Story format not required |

Exemption method: `/override skill=story-craftsman reason="pure technical refactoring, no user-visible functionality change"`

---

## References

- [User Story Template](examples/TEMPLATE-UserStory.md)
- [INVEST Principles](https://en.wikipedia.org/wiki/INVEST_(mnemonic)) — Independent, Negotiable, Valuable, Estimable, Small, Testable
- [Given-When-Then Acceptance Criteria Writing](https://martinfowler.com/bliki/GivenWhenThen.html)
