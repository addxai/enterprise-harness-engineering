---
name: code-review
description: Use when reviewing code changes — MR/PR review, local commits, or uncommitted changes. Reviews document compliance, content quality (architecture soundness, test completeness, observability coverage), and end-to-end consistency (User Story ↔ design ↔ code ↔ tests ↔ observability). Triggers on "review MR", "review this commit", "review my changes", "code review", "help me review".
---

# Code Review

Reviews code changes across three dimensions per `/architect` standards: document compliance, content quality, and end-to-end consistency.

**Each review step uses a multi-role parallel, multi-round iterative review mechanism** to ensure depth and thoroughness.

**Core principles**:
- Documents exist, code doesn't → Allowed (design-first)
- Code exists, documents don't → Fail (undocumented implementation)

---

## Execution Flow

```
Step 0: Collect change scope → Get the diff, classify by file type
Step 1: Document compliance check → Check against /architect format rules item by item (multi-role parallel, minimum 3 rounds)
Step 2: Content quality review → Understand the content, evaluate against /architect quality standards (multi-role parallel, minimum 3 rounds)
Step 3: End-to-end consistency → Trace User Story ↔ design ↔ code ↔ tests ↔ observability (multi-role parallel, minimum 3 rounds)
Step 4: Summary and scoring → Aggregate all round results, red-line determination + improvement suggestions + pass/fail
```

> **Hard requirement: Steps 1-3 must have at least 3 rounds of review.** Marking `Review complete` in Round 1 or Round 2 and moving to the next step is not allowed. Round 3 is the final confirmation round, ensuring all findings are thorough and free of false positives.

---

### Step 0: Collect Change Scope

Auto-detect the change source and uniformly obtain the diff:

| Trigger Scenario | How to Obtain | Example |
|:---------|:---------|:-----|
| Remote MR | GitLab API `GET /projects/{id}/merge_requests/{iid}/changes` + commits | `review MR !52` |
| Local committed | `git diff main..HEAD` or `git diff HEAD~N` | `review recent commits` |
| Local uncommitted | `git diff` + `git diff --staged` | `review my changes` |

After obtaining the diff, classify by file type to determine review dimensions:

| Category | File Pattern | Review Dimensions |
|:-----|:---------|:---------|
| Product docs | `docs/product/**` | Step 1 + Step 2 (User Story format and quality) |
| Architecture docs | `docs/architecture/**` | Step 1 + Step 2 (design quality) + Step 3 |
| Testing docs | `docs/testing/**` | Step 1 + Step 2 (test completeness) + Step 3 |
| Observability docs | `**/observability.md` | Step 2 (observability coverage) + Step 3 |
| Feature code | `server/**`, `app/**`, etc. | Step 2 (code quality) + Step 3 |
| Test code | `**/*_test.*` | Step 2 (test quality) + Step 3 |
| Deployment config | `k8s/**`, `.gitlab-ci.yml` | Step 2 (configuration correctness) |

---

### Step 1: Document Compliance Check

Only check documents involved in the changes, item by item per `/architect` rules.

**Review rules:**

| Rule | Source |
|:-----|:-----|
| Single file <= 400 lines; must split if exceeded | /architect Core Principle 4 |
| Terminology consistent with `domain-model.md` | /architect Core Principle 5 |
| User Story contains no technical implementation details (no class names, API paths, DB fields) | /architect Step 1 |
| ADR includes complete reasoning chain (Context → Options → Trade-off → Decision → Consequences) | /architect Step 2 |
| Mermaid diagram nodes use `<br/>` for line breaks; `\n` is prohibited | /architect Step 2 |
| Cross-document reference paths are correct (relative paths, files exist) | /architect Cross-document Maintenance Rules |
| New/deleted/renamed documents update `TODO.md` accordingly | /architect Cross-document Maintenance Rules |
| New User Story updates `user-stories/README.md` accordingly | /architect Cross-document Maintenance Rules |
| Design-first is allowed, but implemented code must have documentation | /architect Core Principle 7 |

**Multi-round review:** Reviewed in parallel by the Step 1 role group, minimum 3 rounds (see "Multi-Role Review Process" section).

---

### Step 2: Content Quality Review

After understanding the change content, evaluate quality against `/architect` standards. Review does not define standards; it only evaluates.

#### Architecture Documents — Per /architect Step 2 Architecture Quality Principles

- Are design goals clear with constraints?
- Does the ADR reasoning chain hold up (not just correct format, but sound conclusions)?
- Is the data model design reasonable (primary key strategy, indexes, field type choices with rationale)?
- Is the API design appropriate (RESTful, error classification, idempotency description)?
- **Structural**: High cohesion low coupling, reasonable dependency direction, vertical slices, Core separation
- **Robustness**: Fault isolation strategy, idempotency, transaction boundaries, input validation
- **Evolvability**: Extension points reserved, interface minimization

#### Testing Documents — Per /architect Step 5 + `testing-strategy` Skill Standards

- Does each implemented User Story AC have L3 E2E coverage (API level is insufficient; ACs describe user behavior and must be verified end-to-end)?
- L3 E2E must use real dependencies (real DB, real services), not stubs — stubs are a shift-left strategy (L1/L2); E2E verifies the real path
- Does each implemented API handler have at least an L2 integration test?
- Do external dependencies have built-in Stubs (shift-left testing: L1/L2 should not depend on external services being online; managed via `mock-engine`)?
- Do test scenarios cover all ACs of the User Story (verified through traceability matrix: AC → L2 + L3)?
- Are boundary scenarios considered (null values, concurrency, degradation, error paths)?
- Is the responsibility division across layers (L1-L4) reasonable (don't use higher-level tests to cover lower-level logic)?

#### Observability Documents — Per /architect Step 2/4 Observability Standards

- Do core user behaviors have event tracking (exposure/click/conversion funnel)?
- Is the funnel chain complete (entry → conversion → end/abandon)?
- Are metric definitions quantifiable with alert thresholds?
- Is there cross-reference with existing Tracker Manager events (avoid duplication)?
- Do Prometheus metrics have corresponding backend code (at minimum, annotated with implementation plan)?

#### Feature Code — Per Architecture Documents + Quality Principles

- Does it conform to the design described in architecture documents (fields, types, API paths consistent)?
- Is error handling appropriate (distinguishing retryable vs non-retryable)?
- Are transaction boundaries correct (are cross-table operations within the same transaction)?
- Are degradation strategies implemented (if documentation specifies degradation, does code have corresponding logic)?
- Is input validation in place (at system boundaries)?

**Multi-round review:** Reviewed in parallel by the Step 2 role group, minimum 3 rounds (see "Multi-Role Review Process" section).

---

### Step 3: End-to-End Consistency Review

Trace the chain (only review parts involved in the changes):

```
User Stories (docs/product/user-stories/)
  ↓ Does each AC have corresponding technical design?
Architecture Design (docs/architecture/)
  ↓ Is the implemented design consistent with the code?
Feature Code (server/, app/, etc.)
  ↓ Does the implemented feature have tests?
Test Plan + Test Code (docs/testing/ + *_test.*)
  ↓ Does the implemented feature have observability design?
Observability (observability.md + tracking/metrics code)
```

| Layer Pair | Check | Pass Condition |
|:-------|:-----|:---------|
| User Story → Architecture | Each AC traceable to design | AC-described behavior has a counterpart in architecture documents |
| Architecture → Code | Implemented design consistent with code | Fields/APIs/flows match; **document exists but code doesn't = OK (design-first)** |
| Code → Tests | Implemented features have test coverage | Handlers have at least L2; implemented ACs must have L3 E2E; core flows have boundary coverage |
| Code → Observability | Implemented features are observable | Core flows have tracking design; error paths have logging |

**Multi-round review:** Reviewed in parallel by the Step 3 role group, minimum 3 rounds (see "Multi-Role Review Process" section).

---

### Step 4: Summary and Scoring

Aggregate review results from all rounds across Steps 1-3, and output the final conclusion.

#### Red Lines (fail if found)

- Feature code is implemented but has no corresponding architecture document (undocumented implementation) — treated as a quality issue
- Implemented feature has no E2E test coverage — treated as a defect, not "to be added later"
- Implemented feature has no observability (no tracking, no dashboard, no A/B) — treated as a defect; without measurement, delivery is incomplete
- User Story contains technical implementation details (class names, API paths, database fields)
- Plaintext secrets in code/configuration
- Misleading naming (can mislead AI Agents into generating code based on incorrect semantics)

#### Pre-Release Acceptance Checklist (check when changes involve new feature launches)

- [ ] Analytics metrics and event tracking have been verified for accurate reporting
- [ ] Monitoring dashboards have been created and display correctly
- [ ] A/B experiments have been configured (if applicable)

#### Suggested Improvements (non-blocking)

- Document exceeds 400 lines without splitting
- domain-model.md not updated with new terminology
- ADR format incomplete (missing Options or Trade-off)
- Test coverage could be strengthened for boundary scenarios
- Architecture diagrams do not reflect new components described in documentation

---

## Multi-Role Review Process

Steps 1-3 each use the following multi-round review mechanism:

### Review Round Rules

> **Code Review only reviews and outputs opinions; it does not modify code or documents.** The purpose of multiple rounds is cross-validation, eliminating false positives, and catching omissions.

1. **Round 1 — Independent review**: 2-3 independent Sub-agents from the step's role group **review in parallel per role definition**, each recording discovered issues
2. **Round 2 — Cross-validation**: The same group of Agents review each other's Round 1 findings, verifying whether false positives exist, whether issues were missed, whether findings from different roles contradict each other, and adding new findings
3. **Round 3+ — Final confirmation**: At least a third round of review. Each Agent confirms all findings are thorough, free of false positives, and free of omissions, reaching consensus on issue severity
4. **Consensus**: All Agents mark `Review complete` in the review record before proceeding to the next step

> **Hard requirement: Minimum 3 rounds of review.** Marking `Review complete` in Round 1 or Round 2 and moving to the next step is not allowed. Round 3 is the final confirmation round, ensuring all findings are thorough and free of false positives.

### Impact Scope Assessment (required in every review round)

> **This is one of the most important review responsibilities.** In every round of review, every Agent must perform an impact scope assessment.

In **every** review round, all Agents must additionally perform the following checks:

1. **Document consistency**: Does this change contradict existing PRDs, User Stories, or design documents under `docs/`? If inconsistencies are found, they must be noted in the review opinion and correction must be requested
2. **Contract consistency**: Does this change contradict API contracts or data schemas? Have interface changes been synchronized with contract documents?
3. **Cross-module impact**: Does this change affect code, tests, or documents in other modules? For example:
   - Modified API contract → Have callers been updated accordingly?
   - Modified data structure → Have persistence layer and serialization layer been updated accordingly?
   - Modified state logic → Have all modules depending on that state been updated accordingly?
4. **Test coverage**: Do the features affected by this change have corresponding test cases? Are new features covered in the test plan?

Impact scope assessment result recording format:

```markdown
### Impact Scope Assessment — Round N
- **Document consistency**: No contradictions / Warning: found contradiction: <specific description>
- **Contract consistency**: No contradictions / Warning: found contradiction: <specific description>
- **Cross-module impact**: No cross-module impact / Warning: affects the following modules: <list>
- **Test coverage**: Covered / Warning: missing coverage: <specific description>
```

### Review Role Definitions

Each review step uses different combinations of Sub-agent roles. When launching a Sub-agent, the corresponding role's **identity declaration + review focus areas** must be injected at the beginning of the prompt, so it reviews from that professional perspective.

#### Step 1 Document Compliance Check — Role Group

| Role | Identity Declaration (injected into Sub-agent prompt) | Review Focus |
|------|-------------------------------|-----------|
| **Document Compliance Reviewer** | You are a strict technical documentation compliance reviewer, familiar with documentation system standards (line limits, terminology consistency, reference integrity, cross-document maintenance rules). Your task is to ensure every document is impeccable in format and structure. | File line limits, terminology consistency with domain-model.md, whether User Story contains technical details, Mermaid syntax, cross-document reference path correctness, TODO.md/README.md synchronization |
| **Architect** | You are a senior architect reviewing documents from an architectural perspective for structural completeness and technical accuracy. You focus on whether architecture documents are complete, whether ADR reasoning chains hold up, and whether technical descriptions are consistent across documents. | ADR reasoning chain completeness (Context → Options → Trade-off → Decision → Consequences), consistency of technical descriptions between architecture documents and code/contracts, whether design-first annotations are clear (distinguishing target state vs. implemented), whether document granularity is reasonable |
| **Product Perspective Reviewer** | You are a reviewer who examines documents from a product and user perspective, focusing on whether documents accurately convey product intent and whether they could mislead readers (developers, PMs, AI Agents). | Whether document expression is accurate and unambiguous, whether terminology is friendly to non-technical readers, whether User Story acceptance criteria are measurable, whether design-first annotations are clear (preventing readers from assuming something is already implemented) |

#### Step 2 Content Quality Review — Role Group

| Role | Identity Declaration (injected into Sub-agent prompt) | Review Focus |
|------|-------------------------------|-----------|
| **Architecture Reviewer** | You are a senior backend architect specializing in system design, API design, and data model review. You focus on design's structural soundness, robustness, and evolvability, and can identify over-engineering and under-engineering. | Architectural soundness (high cohesion low coupling, dependency direction), ADR reasoning chain quality, data model design (primary keys/indexes/types), API design (RESTful/idempotency/error classification), fault isolation, transaction boundaries, balance between extensibility and over-engineering |
| **Test and Quality Reviewer** | You are a reviewer focused on test strategy and code quality, familiar with the test pyramid, E2E testing, integration testing, and shift-left testing strategies. You ensure implementations have adequate quality assurance. | Test coverage completeness (AC → L2 + L3 traceability), whether L3 E2E uses real dependencies, test layer responsibility division, boundary scenario coverage (null values/concurrency/degradation/error paths), external dependency stub strategy |
| **Observability Reviewer** | You are a reviewer focused on system observability, specializing in event tracking design, monitoring metric definitions, and alert strategies. You ensure every implemented feature can be measured and monitored. | Core behavior tracking coverage, funnel chain completeness, metrics are quantifiable with alert thresholds, deduplication with existing Tracker Manager events, Prometheus metrics have corresponding backend code |

#### Step 3 End-to-End Consistency Review — Role Group

| Role | Identity Declaration (injected into Sub-agent prompt) | Review Focus |
|------|-------------------------------|-----------|
| **Traceability Chain Reviewer** | You are a reviewer focused on full-chain traceability from requirements to delivery. Your core ability is identifying break points between documents, designs, code, and tests — finding undocumented implementations and missing coverage. | User Story AC → architecture design traceability, architecture design → feature code consistency (distinguishing design-first vs undocumented), feature code → test coverage, feature code → observability coverage |
| **Integration Consistency Reviewer** | You are a reviewer focused on cross-layer integration consistency, specializing in finding mismatches in fields/types/paths between different layers. You compare document definitions with code implementations field by field. | Whether field names/types/paths match exactly between documents and code, whether API contracts match implementations, whether database schemas match ORM definitions, whether configuration files match code references |

### Role Injection Method

When launching a review Sub-agent, the prompt structure is:

```
{Role identity declaration}

You are reviewing the following changes: {change scope description}
Review focus: {this role's review focus areas}
Current round: Round {N}

Please complete the following tasks:

**Task 1: Item-by-item review**
Please review item by item and output your opinions in this format:
- [ ] <specific issue description, with file path and line number references>

If no new issues are found (only allowed in Round 3+), output: Review complete — all findings confirmed

**Task 2: Cross-validation** (required for Round 2+)
Review other roles' findings from the previous round and determine:
- Are there false positives? Mark `[False positive]` with reasoning
- Are there omissions? Add new findings
- Do findings from different roles contradict? Mark and provide judgment

**Task 3: Impact scope assessment**
Please assess the impact scope of this change, check the following areas and output results:
- **Document consistency**: Does it contradict existing documents under docs/?
- **Contract consistency**: Does it contradict API contracts or data schemas?
- **Cross-module impact**: Does it affect code, tests, or documents in other modules?
- **Test coverage**: Do affected features have test case coverage?
```

### Review Record Format

Multi-round review results for each Step are recorded in the output in this format:

```markdown
## Step N: <Step Name> Review

### Round 1 — Independent Review

#### Role A
- [ ] <Issue 1, with file path and line number>
- [ ] <Issue 2>

#### Role B
- [ ] <Issue 1>

#### Impact Scope Assessment — Round 1
- **Document consistency**: No contradictions
- **Contract consistency**: Warning: found contradiction: <specific description>
- **Cross-module impact**: Warning: affects the following modules: <list>
- **Test coverage**: Covered

### Round 2 — Cross-Validation

#### Role A
- **Cross-validation**: Role B's Issue 1 confirmed valid / [False positive] <reasoning>
- [ ] <Newly discovered issue (if any)>

#### Role B
- **Cross-validation**: Role A's Issue 1 confirmed valid; Issue 2 [False positive] — <reasoning>
- [ ] <Newly discovered issue (if any)>

#### Impact Scope Assessment — Round 2
- **Document consistency**: No contradictions
- **Contract consistency**: Warning: confirmed contradiction exists (Round 1 finding stands)
- **Cross-module impact**: Supplementary confirmation that impact scope is complete
- **Test coverage**: Covered

### Round 3 — Final Confirmation

#### Role A
Review complete — all findings confirmed, no omissions

#### Role B
Review complete — all findings confirmed, no omissions

#### Impact Scope Assessment — Round 3
- **Document consistency**: No contradictions
- **Contract consistency**: Warning: maintaining Round 1 finding (awaiting code author's fix)
- **Cross-module impact**: No omissions
- **Test coverage**: Covered

### Final Conclusion
- Role A: Review complete (Round 3 confirmed)
- Role B: Review complete (Round 3 confirmed)
- **Confirmed issues: N, false positives excluded: N**
```

---

## Output Structure

After multi-round review is completed within Sub-agents, final results must be output in the following 6-section structure.

### Output Destination

| Change Source | Full Review Results | Conversation Output |
|:---------|:----------------|:---------|
| Remote MR | **Automatically written to MR notes** (via GitLab API, no user confirmation needed) | Only output concise summary |
| Local committed / uncommitted | Output directly to conversation | Full 6-section structure |

For MR scenarios, submit via GitLab API:

```bash
curl -s --request POST --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  --header "Content-Type: application/json" \
  --data '{"body": "<full 6-section review results>"}' \
  "https://gitlab.example.com/api/v4/projects/{project_id}/merge_requests/{iid}/notes"
```

MR scenario conversation summary:

```markdown
- **Conclusion**: Pass / Conditional pass / Fail
- **Score**: X/10
- **Red-line issues**: List (if any)
- **Key findings**: List top 3-5 issues
- **Detailed review written to MR notes**: <MR link>
```

### 6-Section Output Structure

#### 1. Scope

```markdown
- **Change source**: MR !XX / local N commits / local uncommitted
- **Changed files**: N files
- **Modules involved**: List product modules/services
```

#### 2. Document Compliance

Final conclusion from multi-round review, listed item by item per rule:

| Rule | Status | Notes |
|:-----|:-----|:-----|
| <= 400 lines | Pass/Fail | filename:line count |
| domain-model sync | Pass/Fail | Specific missing items |
| User Story no technical details | Pass/Fail | Specific file and line number |
| ADR reasoning chain complete | Pass/Fail | Missing sections |
| Cross-document references correct | Pass/Fail | Broken link paths |
| ... | ... | ... |

Attach multi-round review records (per Review Record Format, including each round's role opinions, cross-validation, and impact scope assessments).

#### 3. Content Quality

Evaluate item by item per file types involved in the changes. Provide specific suggestions, referencing file paths and line numbers.

- **Architecture documents**: Design goals, ADR quality, data model, API design, structural/robust/evolvability
- **Testing documents**: AC coverage, L3 E2E real dependencies, test layer division, boundary scenarios
- **Observability**: Tracking coverage, funnel completeness, quantifiable metrics, alert thresholds
- **Feature code**: Consistency with architecture documents, error handling, transaction boundaries, degradation strategy, input validation

Attach multi-round review records.

#### 4. End-to-End Consistency

Traceability matrix (final conclusion from multi-round review):

| Change | User Story | Architecture Design | Feature Code | Tests | Observability | Status |
|:-----|:---|:--------|:--------|:-----|:------|:-----|
| Specific change item | US-XX-NN | doc section N.N | file.go | test.go | obs.md | Pass/Warning/Fail |

Attach multi-round review records.

#### 5. Summary

```markdown
- **Conclusion**: Pass / Conditional pass / Fail
- **Score**: X/10
- **Should pass**: Yes/No, with reasoning
- **Red-line issues**: List (if any)
- **Suggested improvements**: Prioritized (P1/P2)
- **Review round statistics**: Step 1: N rounds / Step 2: N rounds / Step 3: N rounds
```

#### 6. Multi-Round Review Process Summary

Summary of review rounds, role participation, key cross-validation conclusions, and false positive exclusion statistics for each Step.

---

## Examples

### Bad — Only checks format, not content

```
overview.md <= 400 lines
domain-model updated
→ "Pass"
```

Problem: Format is compliant but content was not read. overview.md describes 3 new tables, none implemented in code and none annotated as "to be implemented," leading readers to believe everything is already in place.

### Bad — Single-round pass, skipping multi-round verification

```
Step 1 Round 1:
  Document Compliance Reviewer: No issues
  Product Perspective Reviewer: No issues
→ Proceed to Step 2
```

Problem: Violates the minimum 3-round rule. Even if Round 1 has no issues, Round 2 and Round 3 confirmation rounds must still be executed.

### Good — Three-dimensional review that reads and understands content before judging (final output)

```
1. Document compliance: overview.md 436 lines → Fail, exceeds 400-line limit
2. Content quality: species_content uses 300KB JSON blob storage, ADR did not document trade-off → Warning, add ADR
3. End-to-end consistency:
   - species_content in doc but not in code → Allowed (design-first)
   - handleSpeciesDetail() still SELECTs description but doc says it was deleted → Fail, implemented portion inconsistent with documentation
→ "Conditional pass, 7/10"
```

### Good — Multi-round cross-validation process (review process record)

```
Step 2 Round 1 (independent review):
  Architecture Reviewer:
  - [ ] overview.md:136 — species_content uses 300KB JSON blob, ADR missing trade-off
  - [ ] api.md:52 — DELETE /species/{id} missing idempotency description
  Test and Quality Reviewer:
  - [ ] test-plan.md — species_content CRUD missing L3 E2E test cases
  Observability Reviewer:
  - [ ] observability.md — species_content write success rate has no monitoring metric

Round 2 (cross-validation):
  Architecture Reviewer:
  - Cross-validation: Test reviewer's L3 E2E gap confirmed valid; observability reviewer's metric gap confirmed valid
  - [ ] overview.md:142 — Supplementary finding: ADR also missing "Consequences" section
  Test and Quality Reviewer:
  - Cross-validation: Architecture reviewer's ADR trade-off gap confirmed valid; idempotency issue confirmed valid
  Observability Reviewer:
  - Cross-validation: All Round 1 findings confirmed valid, no false positives

Round 3 (final confirmation):
  Architecture Reviewer: Review complete — 5 issues confirmed, no omissions
  Test and Quality Reviewer: Review complete — all findings confirmed
  Observability Reviewer: Review complete — all findings confirmed
  Confirmed issues: 5, false positives excluded: 0

→ "Conditional pass, 7/10"
```

### Bad — Treating design-first as an error

```
species_content table: Document has DDL, code not implemented → "Design and implementation inconsistent"
```

Problem: Design-first is allowed. Documents describe the target state; code catching up incrementally is normal.

### Good — Distinguishing design-first from undocumented code

```
species_content table: In doc but not in code → Allowed (design-first)
handleDeleteEvent(): Code has soft-delete logic, not mentioned in documentation → Undocumented implementation
```

---

## Relationship with Other Review Skills

| Skill | Responsibility | When to Use |
|:------|:-----|:-------|
| **code-review** (this skill) | Document compliance + content quality + end-to-end consistency (multi-role, multi-round review) | Day-to-day MR/commit review |
| **security-compliance-review** | Security and compliance: secrets, PII, access control, red lines | When MR involves security-sensitive changes |
| **/architect** | Defines standards (documentation system + architecture quality principles) | Design phase, not review |
