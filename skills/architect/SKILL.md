---
name: architect
description: Use when designing a new feature or system, making architecture decisions, writing technical design docs, or structuring project documentation. Triggers on "design", "architecture", "technical design", "ADR", "system decomposition", "how should I structure this", "设计方案", "架构设计", "技术方案", "文档体系", "写 User Story", "写文档". Also use when reviewing existing architecture docs or asking "where should I put this doc?"
---

# Architect

Architect Skill — drives design decisions through Socratic questioning and produces a complete technical documentation system.

The architect's deliverables are the documentation system itself. Writing `overview.md` is the act of system decomposition; writing `domain-model.md` is the act of establishing ubiquitous language. Documentation is not a by-product of design — documentation IS the design.

## Core Principles

1. **Documentation before code**: Each step's documentation output serves as input for the next step — no skipping, no reordering
2. **Socratic questioning drives design**: Do not propose solutions directly — first identify architectural concerns from User Stories, then converge design decisions through questioning
3. **User Stories are purely user-perspective**: User Stories should contain only user experience and acceptance criteria — never mix in technical details
4. **Single file ≤ 400 lines**: If exceeded, use overview.md as the entry point and split downward with layered navigation
5. **Terminology unification**: `domain-model.md` implements DDD Ubiquitous Language — the single source of truth (SSOT) for business term <-> technical term mapping
6. **Superpowers outputs must be consolidated**: Plans generated during a session must be written into `docs/` before coding begins
7. **Design-first approach**: Documentation may describe the target state (design ahead of code is normal); however, implemented features must have corresponding documentation

---

## Overall Workflow (must be executed in order)

```
1. User Story          → Define user experience flows and acceptance criteria (no technical details)
2. Architecture Design → User Story pattern recognition → Socratic questioning → brainstorming divergence
                         → Converge using methodology references → Output overview.md + domain-model.md + ADR
3. Dev/Test Env Design → Build feedback loops for AI Agent TDD
4. Module Detail Design→ Module-level pattern recognition → questioning → output ≤400 line module docs
5. Layered Test Plan   → Generate L2-L4 plans based on User Stories + tech design + env design
   (L2-L4)
6. Parallel TDD Dev    → Implement in parallel using agent teams + superpowers
```

---

## Documentation Directory Structure

> **All documentation must reside under `docs/` in the project root.** In the tree below, `docs/` is the root, and all subdirectories (`product/`, `architecture/`, etc.) are children of `docs/`. Absolute paths look like `<project-root>/docs/product/prd.md`. Do not create standalone `product/` or `architecture/` directories at the project root.

```
docs/                                # <-- The single root directory for all documentation
├── TODO.md                          # Documentation review tracking checklist (SSOT)
├── product/                         # docs/product/ — Product layer: user perspective
│   ├── prd.md                       # docs/product/prd.md
│   └── user-stories/
│       ├── README.md                # docs/product/user-stories/README.md
│       └── {service-or-module}.md   # docs/product/user-stories/{service}.md
├── architecture/                    # docs/architecture/ — Architecture layer: system design decisions
│   ├── overview.md                  # docs/architecture/overview.md (≤400 lines)
│   ├── domain-model.md              # docs/architecture/domain-model.md — Ubiquitous Language SSOT
│   ├── tech-stack.md                # docs/architecture/tech-stack.md
│   └── {service}/                   # docs/architecture/{service}/
│       ├── overview.md              # docs/architecture/{service}/overview.md (≤400 lines)
│       └── {topic}.md               # docs/architecture/{service}/{topic}.md (≤400 lines)
├── testing/                         # docs/testing/ — Testing layer: strategy and test cases
│   ├── strategy.md                  # docs/testing/strategy.md
│   └── services/{service}/          # docs/testing/services/{service}/
└── deployment/                      # docs/deployment/ — Deployment layer: environment operations manual
    ├── local-dev.md
    ├── ci.md
    └── cd.md
```

---

## Rules

### Step 1 — User Stories (`docs/product/user-stories/{service}.md`)

**What to write**: User experience flows, Epic breakdown, verifiable acceptance criteria (AC). May include NFRs (non-functional requirements).

**Strictly forbidden**: Technical implementation details (no class names, API paths, database fields, or protocol details). User Stories are the user's perspective, not a technical specification.

**Document structure**:
- Split files by **service or module** (e.g., `gateway.md`, `sandbox.md`) — one file per service domain
- Organize each file by **Epic** — an Epic is a business-meaningful feature cluster
- ID format: `US-{module-abbreviation}-{number}` (e.g., `US-FI-01`)
- Each User Story: Background (Why) + User Story (Who/What/Goal) + AC (Given/When/Then format)
- NFRs in a separate section with quantifiable metrics (e.g., "p95 response < 2s") — no implementation approach
- Progress markers: `✅ Implemented` / `⚙️ In Progress` / `Not Started`
- After adding new User Story, update the index table in `user-stories/README.md`

**Companion Skill**: `story-craftsman` (guided interviews to uncover context + standard template generation)

---

### Step 2 — Architecture Design (`docs/architecture/`)

Step 2 is the architect's core work. **Do not jump straight to drawing architecture diagrams after reading the User Stories** — first identify the architectural concerns implied in the User Stories, converge design decisions through questioning, then commit them to documentation.

#### 2a. User Story Pattern Recognition

After reading Step 1's User Stories, identify the implicit architectural concerns. Common User Story patterns and their architectural signals:

| Appears in User Stories... | Architecture Signal | Questioning Direction |
|-------------|---------|-------------|
| Multiple tenants / OEM customers / white-label | Multi-tenancy isolation | Data isolation level, configuration variance, failure blast radius |
| Real-time / push / streaming / online status | Real-time communication | Latency tolerance, push failure strategy, concurrent connection scale |
| Scheduled / periodic / auto-execution | Scheduling system | Failure compensation vs skip, concurrent trigger mutual exclusion, timezone handling |
| Distributed update / remote management / software upgrade | Offline + eventual consistency | Offline node catch-up, interrupted upgrade recovery, canary + rollback |
| Third-party payment / external API integration | External integration | Failure isolation, retry idempotency, reconciliation mechanism |
| Audit / compliance / operation records | Audit trail | Immutability, retention period, access control |
| Orders / tickets / entity lifecycle | State machine | State definitions, transition rules, concurrent transitions, invalid transition handling |
| Cross-service coordination / multi-step process | Distributed transactions | Eventual vs strong consistency, compensation mechanism, timeout handling |
| Search / reports / data analytics | Read-write separation | Query model vs write model, data sync latency tolerance |
| Any new feature / user behavior change | **Observability** | How to measure success? What metrics are needed? Event tracking needed? A/B experiment validation needed? |

**Not all User Stories will trigger every signal.** A simple CRUD feature does not need to be questioned about distributed consistency. Only question what is relevant to the current User Story.

#### 2b. Socratic Questioning

For each identified architectural concern, converge design decisions through questioning rather than giving direct answers. The goal is to have the user (or yourself) explicitly answer the following:

**Boundary definition** (corresponding to DDD Bounded Context):
- Do these two pieces of logic change at different frequencies?
- Do their failures need to be isolated? (A going down should not affect B)
- Do they have clear data ownership? (Who is the source of truth?)

**Integration patterns**:
- Does the caller need the result immediately? → Sync vs async
- If the downstream is down, should the upstream fail or continue? → Coupling level
- Does this operation need to be idempotent? (What happens on repeat calls?)

**Observability** (must question for every feature):
- After this feature launches, how do we know it's successful? → Define core metrics (conversion rate, retention, p95 latency, etc.)
- Are new tracking events needed? → User behavior events (impression/click/conversion funnel)
- Is A/B experiment validation needed? → When the approach is uncertain, use experiment data instead of guessing
- What are the SLA targets? → Quantified targets for availability, response time, error rate
- How do we detect problems? → Alert rules, dashboards, log keywords

**Design constraints**:
- What is the most critical non-functional requirement? (Latency? Throughput? Consistency? Availability?)
- Which are hard constraints (non-negotiable) and which are soft constraints (trade-offable)?
- What technologies is the team most experienced with? (Tech selection should consider team capability)

#### 2c. Architecture Quality Principles

Designs must be checked against the following principles. These are also the criteria used by `code-review` to evaluate design quality.

**Structural principles**:
- **High cohesion, low coupling**: Clear module boundaries, each module does one thing, changes do not propagate
- **Dependency direction**: Stable modules do not depend on unstable modules, dependencies flow in one direction
- **Vertical slicing**: Organized by business domain rather than technical stack layers
- **Core module separation**: Core business logic is independent of frameworks and infrastructure, reusable across environments
- **Ports & Adapters**: Business logic is strictly isolated from external dependencies; all I/O is defined through Port interfaces, no direct dependency on concrete implementations

**Robustness principles**:
- **Failure isolation**: External dependencies going down have degradation/circuit-breaker/timeout strategies
- **Idempotency**: Write operations are safe for repeated calls
- **Data consistency**: Transaction boundaries for cross-table/cross-service operations are correct
- **Input validation**: User input is validated at system boundaries
- **Built-in stubs**: Every external dependency has a corresponding Stub/Mock; test environments do not require external services to be online

**Evolvability principles**:
- **Extension points**: Interfaces are pre-designed for known future changes
- **Interface minimization**: APIs expose only necessary information without leaking internal implementation
- **Naming is design**: Variable, function, and interface names must accurately convey intent; naming is not just about readability — it determines whether an AI Agent can correctly understand semantics
- **Every rule has a Why**: Documentation, comments, and commit messages explain "why," not just "what"; ADR, AC, and config items all need rationale

#### 2d. Solution Divergence and Convergence

After gathering sufficient information through questioning:

1. **Invoke `superpowers:brainstorming`** to diverge and explore possible approaches
2. **Reference methodology decision cards in `references/`** to evaluate approaches (see this skill's references/ directory)
3. **Converge**: Select an approach, record it as an ADR

**ADR reasoning chain** (must be included — conclusions alone are insufficient):
- **Context**: What problem is being faced + what constraints exist
- **Options**: What approaches were considered (at least 2)
- **Trade-off**: Pros and cons of each approach (not just the pros)
- **Decision**: What was chosen (or **Pending** — see below)
- **Consequences**: What costs were accepted

**Pending ADR**: When questions remain unanswered or information is insufficient for a decision, a **Pending ADR must be created** (Decision marked as `Pending`) rather than skipping it. A Pending ADR records the known Context and Options, and explicitly states "which questions must be answered before a decision can be made." This ensures uncertain decision points are explicitly tracked and not forgotten during subsequent design.

#### 2e. Documentation Output

**Output files**:
- `overview.md` — Architecture overview (design goals table → Mermaid architecture diagram → component responsibilities table → sub-document navigation table)
- `domain-model.md` — Ubiquitous Language SSOT (business term <-> technical term mapping, essentially implementing DDD Ubiquitous Language)
- ADR records in overview.md or separate files

**Documentation standards**:
- **Single file ≤ 400 lines** — when exceeded, split into sub-documents; overview.md retains only the overview and sub-document navigation table
- Record review time using `|Document Status` at the beginning of the file
- **All terminology must align with `domain-model.md`** — consult it before writing; do not invent new concepts
- Use relative paths for cross-document references; add a three-column navigation table at the top of subsystem documents (submodule | document | description)
- Use `<br/>` for line breaks in Mermaid diagram nodes — **`\n` is prohibited**

**Companion Skills**: `doc-writing` (HWPR to mark human design decisions, AWOR for expanded detail), `superpowers:brainstorming` (solution divergence)

---

### Step 3 — Dev/Test Environment Design (`docs/deployment/local-dev.md`)

**What to write**: L1/L2/L3 layered environment architecture, multi-worktree port isolation strategy, shared channel switching mechanism, hot-reload configuration. The goal is to build a fast-feedback TDD loop for AI Agents.

**Documentation standards**:
- `local-dev.md` has two sections: **User Guide** (commands and results, for developers) + **Implementation Details** (design rationale, for maintainers)
- Use `make` targets as the entry point for operations; bare commands are prohibited in documentation

**Companion Skills**:
- `multi-worktree-dev` (L1/L2/L3 layered design, port hash offset, shared channel exclusive switching, health probing)
- `mock-engine` (Mock infrastructure: start/stop mock services, load test data, create test scenarios)

---

### Step 4 — Module Detail Design (`docs/architecture/{service}/*.md`)

**What to write**: Internal design of a single service/module — interface contracts, data flows, state machines, key algorithms.

Like Step 2, Step 4 also requires first identifying module-level design concerns, then converging through questioning.

#### 4a. Module-Level Pattern Recognition

| Module Characteristic | Questioning Direction |
|---------|-------------|
| Exposes external APIs | Error classification (which are retryable / which are not), idempotency, versioning strategy |
| Entities with lifecycles | State definitions, transition guard conditions, concurrent transitions, invalid transition handling |
| Depends on external services | Timeout strategy, circuit-breaker thresholds, degradation plan, anti-corruption layer design |
| High-concurrency reads/writes | Lock granularity, optimistic vs pessimistic, cache consistency |
| Complex business rules | Will rules change? Configuration-driven vs hard-coded? How to handle rule conflicts? |
| User-behavior-related features | What tracking events are needed? How is the funnel defined? Is A/B experimentation needed? |

#### 4b. Output After Questioning

After converging through questioning, produce a module design document that must include:

- **Interface contract**: Not just API path + request/response, but also error classification and idempotency description
- **State machine** (if applicable): State diagram + guard conditions + concurrency handling strategy
- **Dependency direction**: Who this module depends on, who depends on it, and whether the direction is correct (stable modules should not depend on unstable modules)
- **Data flow**: Source → transform → sink, including error/retry paths
- **Observability design**: Core metric definitions (SLA), new tracking events needed (event tracking), A/B experiment plan (if applicable), alert rules, dashboards

**Documentation standards**:
- **Each file strictly ≤ 400 lines** — this is a hard limit, not a suggestion
- When exceeding 400 lines, split: keep the overview in `{service}/overview.md`, move details to `{service}/{topic}.md`
- Layered nesting: system overview → service overview → module details; each layer is responsible only for its own granularity
- Each detail document references its parent service overview at the top, forming a navigable document tree

**Companion Skill**: `doc-writing` (HWPR/AWOR framework)

---

### Step 5 — Layered Test Plan (`docs/testing/`)

**What to write**: A layered testing strategy generated from Step 1 (User Story acceptance criteria) + Step 2 (technical design) + Step 3 (environment design).

**Document structure**:
```
docs/testing/
├── strategy.md                 # Overview (≤400 lines): layer table, layering logic, mock architecture, traceability matrix, CI/CD
└── scenarios/                  # AC-level scenario matrices (strategy.md should not contain individual test cases)
    ├── ep1-<epic>.md           # By Epic (product/QA perspective)
    ├── tech-<module>.md        # By technical module (developer perspective)
    └── tech-nfr.md             # NFR degradation/fault tolerance
```

**strategy.md must include**:
1. **10-column test layer overview table** (layer / case count / test goal / real dependencies / mock dependencies / real infra / mock infra / execution timing / duration / code location)
2. **Layering logic table** (what problem each layer solves + why the layer above is insufficient)
3. **Mock infrastructure SSOT** (directory structure + mock/real switching strategy per layer)
4. **Requirements traceability matrix** (User Story → test case IDs per layer)
5. **Quality gate table** (gate / checkpoint / criteria)

**Scenario file AC-level traceability table**: Fixed 8-column format `AC Scenario | Smoke | L1 | L2-1 | L2-2 | L3-1 | L3-2 | L4`, each cell filled with specific test case IDs.

**Key principles**:
- L3/L4 are **black-box tests** — test clients interact directly with the user interface; **intercepting or mocking internal components at intermediate layers is prohibited**
- Test scenario data is switched via `make mock-scenario` for controlled, repeatable execution

**Quality standards** (also the criteria used by `code-review` for evaluating tests; see `testing-strategy` skill for detailed layered strategy):
- **Code without E2E tests must not merge to trunk** — treated as a defect, not a "to-do"
- Each implemented User Story AC must have L3 E2E test coverage (AC describes user behavior and must be verified end-to-end; **L3 uses real dependencies**, not stubs)
- Each implemented API handler must have at least L2 integration tests (verifying interface contracts and data correctness)
- State changes, deletions, corrections, and other core flows must have boundary scenario coverage
- Test scenarios must cover all ACs in the User Stories (verified via traceability matrix: AC → L2 case ID + L3 scenario ID)
- **Built-in stubs are a shift-left strategy**: Every external dependency has a corresponding stub; L1/L2 do not require external services to be online. However, L3 E2E must use real dependencies to verify the complete chain

**Companion Skills**:
- `testing-strategy` (generate complete layered strategy by project type, includes `references/engagement-example.md` real-world example)
- `mock-engine` (mock infrastructure management: L1/L2 stub/mock service startup, test scenario data loading)
- `multi-worktree-dev` (test parallel safety design — multiple worktrees do not contend for shared channels)

---

### Step 6 — CI/CD Deployment Documentation (`docs/deployment/ci.md` + `cd.md`)

**What to write**: CI pipeline quality gates, CD deployment strategy, K8s resource configuration, Ingress routing, secrets management.

**Companion Skills**:

| Task | Skill |
|------|-------|
| Write/review `.gitlab-ci.yml` | `gitlab-ci` |
| Full deployment workflow for new apps (CI + K8s + Ingress + Vault + Crossplane) | `cicd-developer` |
| ArgoCD GitOps sync/rollback/troubleshooting | `argocd` |
| Set up CICD component stack for new clusters | `argocd-deploy` |
| View/troubleshoot K8s cluster resources | `k8s-ops` |
| Image registry Robot Account | `harbor` |
| Vault secrets management | `vault-kv-manager` |
| Runner selection and troubleshooting | `gitlab-instance-runners` |
| Embedded repo CI Pipeline | `embed-ci-setup` |
| Jenkins pipeline management | `jenkins` |

---

## Cross-Document Maintenance Rules

| Operation | Must Also Update |
|------|------------------|
| Add/delete/rename document | `docs/TODO.md` |
| Add User Story | `user-stories/README.md` index table |
| Change architecture component responsibilities | `architecture/overview.md` mapping table |
| Add domain terminology | `architecture/domain-model.md` |
| Document + code changed together | Put in the same MR (use `gitlab-mr` skill) |

### Superpowers Output Consolidation Rules

`superpowers:writing-plans`, `superpowers:brainstorming`, and other skills generate design documents or plans during a session. These documents **must be consolidated into the `docs/` system** — they cannot exist only in session context or temporary files:

| Superpowers Output | Consolidation Target |
|----------------|---------|
| Feature plan / brainstorm conclusions | Corresponding Epic in `docs/product/user-stories/{service}.md` |
| Overall technical plan / writing-plans output | `docs/architecture/overview.md` or corresponding service overview |
| Module implementation plan | `docs/architecture/{service}/{topic}.md` |
| Test plan | `docs/testing/strategy.md` or `services/{service}/` |
| Dev environment design | `docs/deployment/local-dev.md` |

**Consolidation timing**: After superpowers plan is confirmed and before coding starts — consolidate documents first, then begin coding.

---

## Documentation Review (`docs/TODO.md`)

`TODO.md` tracks all items pending review using three states: `[ ]` To Do / `[/]` In Progress / `[x]` Done

Review focus areas:
- Whether any file exceeds 400 lines (split if so)
- Whether terminology is consistent with `domain-model.md` (business term <-> technical term mapping)
- Whether User Stories contain technical details
- Whether cross-document reference paths are correct
- Whether User Story status is synchronized with code implementation
- Whether Product / Architecture interpretations of Phase breakdown are aligned
- **Whether ADR includes a complete reasoning chain** (Context → Options → Trade-off → Decision → Consequences)

---

## Skill Toolchain Quick Reference

| Step | Task | Skill to Use |
|------|------|-----------|
| Step 1 | Write User Stories | `story-craftsman` |
| Step 2 | Architecture design: solution divergence | `superpowers:brainstorming` |
| Step 2 | Architecture design: write documentation | `doc-writing` |
| Step 3 | Design dev/test environment layering | `multi-worktree-dev` |
| Step 4 | Module detail design | `doc-writing` |
| Step 5 | Generate layered test plan | `testing-strategy` + `multi-worktree-dev` |
| Step 6 | CI Pipeline configuration | `gitlab-ci` / `embed-ci-setup` / `jenkins` |
| Step 6 | CD full deployment workflow | `cicd-developer`   |
| Step 6 | K8s / images / secrets | `k8s-ops` +  `vault-kv-manager` |
| Throughout | Event tracking definition and management | event tracking platform |
| Throughout | A/B experiments / Feature Flags | A/B experiment platform |
| Throughout | SLA metric configuration | `sla-metric` |
| Throughout | Monitoring dashboards / alerts | `grafana` + `prometheus` |
| Throughout | Error monitoring | `sentry` + `sentry-onboarding` |
| Throughout | Submit documentation + code together as MR | `gitlab-mr` |
| Throughout | R&D process orchestration | `dev-workflow` |
| Throughout | Create or update the Skill itself | `superpowers:writing-skills` |

---

## Methodology References (`references/`)

The questioning and solution evaluation in Steps 2/4 can reference the following methodology decision cards. Each card answers only three questions: when to use it, core concepts quick reference, and when NOT to use it.

**The AI agent already has sufficient knowledge of these methodologies — the value of the decision cards is helping determine "should I use this for the current scenario."**

| Decision Card | Applicable Signals |
|-------|---------|
| `references/ddd.md` | Confused business terminology, unclear service boundaries, multi-team collaboration |
| `references/event-driven.md` | Async processing, cross-service coordination, state change notifications |
| `references/hexagonal.md` | Multiple external integrations, need for testability, preventing framework lock-in |
| `references/state-machine.md` | Entities with lifecycles, complex state transition rules |
| `references/integration-patterns.md` | Third-party API integration, unreliable external systems |
| `references/multi-tenant.md` | OEM / white-label / multi-tenant scenarios |

---

## Example Comparisons

### Bad — Jumping to architecture diagram immediately after reading User Stories

```
Read User Stories → Directly write overview.md and draw Mermaid diagrams
→ No questioning, service boundaries drawn by intuition, ADR has no reasoning chain
```

### Good — Pattern recognition → questioning → brainstorming → convergence

```
Read User Story → Identify "multi-tenant + distributed update" signals
→ Question: What level of data isolation between tenants? What's the catch-up strategy for offline nodes?
→ Brainstorm 3 approaches
→ Reference DDD + multi-tenant decision cards to evaluate
→ Select approach, write ADR (with complete reasoning chain)
→ Output overview.md + domain-model.md
```

---

### Bad — User Story contains technical details

```markdown
## US-GW-01 Message Routing
After a user sends a message, the Gateway calls the `resolve_intent()` method through
IntentResolveMiddleware, queries the PostgreSQL workspace table to get the agent_id,
then distributes it to the corresponding Sandbox Pod via Redis Pub/Sub.
```

Problem: AC should describe the results the user sees, not class names, databases, or middleware.

### Good — User Story from purely user perspective

```markdown
## US-GW-01 Message Routing
**Background**: Users need to maintain independent Agent context across different group chats.

**User Story**: As a team member, I want each group chat to have its own Agent context
so that the Agent remembers each group's context independently without cross-contamination.

**AC**:
- Given the user has had conversations in both Group A and Group B
- When the user asks a question in Group A
- Then the Agent responds based only on Group A's history, without mixing in Group B's content
```

---

### Bad — Single file exceeds 400 lines with no splitting

```
docs/architecture/gateway.md  (800 lines, containing all subsystem details)
```

### Good — Overview with navigation + layered sub-documents

```
docs/architecture/gateway/
├── overview.md          (≤400 lines, architecture diagram + sub-document navigation table)
├── intent-resolve.md    (≤400 lines)
├── thread-lane.md       (≤400 lines)
└── feishu-card.md       (≤400 lines)
```

---

### Bad — Superpowers output stays in the session

```
After brainstorming is complete, directly say "ok, let's start coding"
→ Plan exists only in session context, lost in next session, cannot serve as test baseline
```

### Good — Consolidate plan into docs/ before coding

```
Brainstorming complete → Write into docs/architecture/overview.md → commit → start coding
```
