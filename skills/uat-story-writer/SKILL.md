---
name: uat-story-writer
description: Discover missing UAT test scenarios from the user's perspective, confirm requirements through guided interviews, and output user story files in story-craftsman template + Gherkin Given/When/Then format. Use when the user mentions "add test cases", "missing tests for XX scenario", "write UAT cases", "write test scenarios", "brainstorm test cases", or discovers test coverage gaps. Should also trigger even if the user just mentions a feature "hasn't been tested for XX situation".
---

# UAT Story Writer

Discover missing UAT test scenarios from real user usage contexts and output structured user story documents.

**Core philosophy**: UAT tests start from user stories, not from technical implementation. "Checking order status while on the go" reveals real needs better than "HTTP API test."

## Rules

1. **User perspective first**: Each scenario must correspond to a real user behavior or usage context, not a technical condition. Technical conditions are the scenario's background, not the scenario itself
2. **Do not fabricate when information is lacking**: Key constraints like test environment capabilities and actual topology must be obtained through interviews, not assumed
3. **Acceptance criteria must be executable**: Each AC uses Gherkin Given/When/Then format, ensuring automation tools can directly consume them
4. **Output to cases/ directory**: User stories go in the project's `cases/` directory; `features/` directory is reserved for AI-generated executable automation cases
5. **Follow story-craftsman template**: File structure strictly follows the story-craftsman template format (background, goals, roles, user stories, progress, update log)

---

## Execution Flow

### Step 1: Explore Existing Test Coverage

First understand the project's existing test cases and find coverage gaps:

- Read related `.feature` files under `features/scenarios/` to understand existing scenarios
- Read existing user story files under `cases/` to avoid duplication
- List the currently covered scenario inventory and clearly indicate the missing dimensions

### Step 2: Guided Interview (one question at a time, multiple-choice preferred)

Confirm key constraints through questioning — ask only one question at a time, preferring multiple-choice options:

| Dimension | Purpose | Example Question |
|------|------|---------|
| **Test environment capability** | Determine scenario granularity | "Can your test environment simulate network conditions? A) Router/firewall control B) Physical switching only C) Both" |
| **Actual usage topology** | Determine coverage scope | "Which of the following do you actually encounter? A) Local network B) Mobile remote C) Cross-network D) All of the above" |
| **Focus dimension** | Determine acceptance depth | "Are you focused on functionality only or also on experience metrics? A) Functionality only B) Also experience C) Both" |
| **Variable control** | Determine what is under test | "Which end is the variable you can control? Phone side? Device side? Or both?" |

Interview principles:
- **One question at a time**: Do not ask multiple questions simultaneously — avoid information overload
- **Multiple-choice preferred**: Provide options whenever possible to reduce the user's answering cost
- **Stop promptly**: Stop asking when sufficient information is gathered — do not over-interview. Usually 2-4 questions suffice
- **UAT course correction**: If the user's description leans toward technical perspective (e.g., "test mobile network"), guide back to user perspective (e.g., "user operating remotely while away from home")

### Step 3: Scenario Brainstorming (User Story Perspective)

Based on interview results, brainstorm scenarios starting from the user's real daily usage contexts.

Key thinking framework — imagine a user's daily usage journey:
- **Where is the user?** (home, office, on the go, at a friend's house...)
- **What is the user doing?** (actively checking, checking after receiving a notification, glancing while doing something else...)
- **What changed in the environment?** (went outside, entered an elevator, switched networks...)
- **What went wrong unexpectedly?** (lost connectivity, poor signal, service unavailable...)

Present brainstorming results in table form, including: scenario number, user scenario description, corresponding environment/technical conditions.

After presenting, ask the user: "Is this coverage sufficient? Anything to add or remove?"

### Step 4: Generate User Story Files

After confirmation, generate files following the story-craftsman template and save to the `cases/` directory.

**File naming**: `{feature}-{dimension}.md` (lowercase kebab-case), e.g., `live-view-network-environments.md`

**File structure**:

```markdown
# <Topic> - User Stories

> Reference document: [related feature file](../features/scenarios/xxx.feature)

(mermaid flow diagram: core flow + variable dimensions)

## 1. Background (Why)
## 2. Goals (What)
## 3. Roles (Who)
## 4. User Stories

### 4.1 US-<MODULE>-<DIM>-01: <User Scenario Title> [P0/P1/P2]

**As** <role>, **I want** <capability/need>, **so that** <value/purpose>.

**Acceptance Criteria (AC):**
- [ ] Given <precondition>, When <user action>, Then <expected result>
- [ ] Given <precondition>, When <user action>, Then <expected result>

## 5. Progress
## 6. Update Log
```

**Key points for writing acceptance criteria**:
- Given describes the user's situational context and environment state, not technical configuration
- When describes the user's actual action
- Then describes the user-observable result (UI feedback, status change)
- Each User Story includes 2-4 ACs covering the core path and key exceptions

**Priority criteria**:
- **P0**: The most common core scenarios users encounter (e.g., placing an order online, remotely checking status while away)
- **P1**: Scenarios users encounter fairly often but not every time (e.g., network switching, connectivity restoration)
- **P2**: Extreme or low-frequency scenarios

---

## Examples

### Bad — Writing UAT cases from a technical perspective

```
Scenario: Order submission test under mobile network
  Given phone connected to mobile network
  When order submission request is initiated
  Then request successfully reaches backend service through CDN gateway
```

### Good — Writing UAT cases from a user perspective

```
### US-ORDER-NET-02: Placing an order while away from home using mobile data [P0]

**As** a MyApp user, **I want** to complete an order while away from home using mobile data,
**so that** I can purchase what I need anytime, anywhere.

**Acceptance Criteria (AC):**
- [ ] Given the phone has WiFi turned off and is using mobile cellular network,
      When the user taps the "Submit Order" button,
      Then the order is submitted successfully and the confirmation page is displayed
- [ ] Given an order has already been submitted on mobile network,
      When the user views order details, cancels the order, and performs other actions,
      Then all functions respond normally
```

### Good — Resource sharing permission scenario

```
### US-SHARE-PERM-01: Invited team member viewing a shared project [P0]

**As** an invited team member, **I want** to view shared project content after joining via share link/invitation,
**so that** team members can stay updated on project progress at any time.

**Acceptance Criteria (AC):**
- [ ] Given the project owner has shared the project with a team member's account,
      When the team member logs into the App and enters the project list,
      Then they can see the shared project and successfully view its details
- [ ] Given a team member is viewing the content of a shared project,
      When the owner revokes sharing permissions for that project,
      Then the team member's access is interrupted with a no-permission prompt
```

---

## Relationship with Other Skills

- **story-craftsman**: This skill uses its template format but focuses on UAT scenario brainstorming and Gherkin AC writing
- **testing-strategy**: This skill's outputs are L4 (UAT) layer user stories, aligned with the overall layered testing strategy
- **Test automation tools**: This skill's outputs (user stories under `cases/`) serve as input for test automation tools to generate executable automation cases (`.feature` files under `features/`)
