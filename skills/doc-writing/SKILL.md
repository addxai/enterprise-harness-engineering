---
name: doc-writing
description: Write documents using the HWPR/AWOR framework -- separating human value judgments from AI-expanded content so critical information is not buried. Triggers when the user requests writing, rewriting, or reviewing document quality.
---

# Doc Writing (HWPR/AWOR)

In the AI era, human **value judgments** get buried in AI-expanded long documents. This skill uses HWPR/AWOR markers so readers (human or AI) can quickly locate what the human actually thought.

For the detailed template, see [examples/TEMPLATE-HWPR.md](examples/TEMPLATE-HWPR.md).

---

## Core Concepts

- **[HWPR]** (Human Wrote, Please Read): Unknown context + value judgments written by a human. **Must be short** (3-5 sentences).
- **[AWOR]** (AI Wrote, Optional Read): Detailed content expanded by AI. Can be deleted, modified, or replaced.

---

## Rules

1. **Never modify [HWPR] content** — AI may only read HWPR paragraphs; it must not rewrite, rephrase, merge, or "polish" them
2. **HWPR must be short** — Each HWPR paragraph must not exceed 3-5 sentences; write only: unknown context + value judgments
3. **Value judgments with humility** — Use phrasing like "I believe" / "current judgment" / "possibly" in HWPR, acknowledging potential error
4. **[AWOR] can be freely modified** — AI-expanded content may be replaced, deleted, or rewritten at any time
5. **Consistent marker format** — Use bold markers `**[HWPR]**` and `**[AWOR]**` as headers, followed by paragraph titles
6. **HWPR uses blockquote** — HWPR body text uses `>` block quotes for visual distinction

---

## Execution Flow

### Mode A: Write a New Document

#### Trigger Conditions

User requests "help me write a document," "write a proposal," "draft a PRD," etc.

#### Step 1: Guide HWPR Extraction

Ask the user questions to extract core value judgments:

```
To write an effective document, I need you to provide the following HWPR content (keep it brief, 1-3 sentences per item):

1. **Background**: Why are we doing this? What is the core problem?
2. **Judgment**: What do you think we should do? Why this direction?
3. **Trade-offs**: What was deliberately given up? What are the known risks?
```

#### Step 2: Confirm HWPR

Organize the user's answers into HWPR paragraphs and display them for user confirmation. Once confirmed, HWPR is never modified afterwards.

#### Step 3: Generate Complete Document

Following the [TEMPLATE-HWPR.md](examples/TEMPLATE-HWPR.md) structure, expand corresponding AWOR paragraphs after each HWPR paragraph.

---

### Mode B: Rewrite an Existing Document

#### Trigger Conditions

User provides an existing document and requests "restructure using HWPR/AWOR," "split and label," etc.

#### Step 1: Identify Potential HWPR

Read the full text and mark sentences/paragraphs that appear to contain human value judgments (identification criteria: contains subjective decisions, trade-offs, "we chose" / "gave up" language, etc.).

#### Step 2: Confirm with User

List the identified results and ask the user to confirm each one:

```
I identified the following as potentially your value judgments (HWPR) in the document. Please confirm:

1. yes/no "We chose option B because..." (paragraph X)
2. yes/no "Abandoned real-time push, switched to polling..." (paragraph Y)
3. yes/no ...
```

#### Step 3: Split, Label + Expand

Extract confirmed HWPR into `**[HWPR]**` paragraphs, mark remaining content as `**[AWOR]**`, and expand where necessary.

---

### Mode C: Review a Document

#### Trigger Conditions

User requests "review the document," "check HWPR formatting," etc.

#### Review Checklist

Check and report the following issues:

| Check Item | Issue Description |
|--------|---------|
| Missing markers | Paragraph has no [HWPR] or [AWOR] marker |
| HWPR too long | HWPR paragraph exceeds 5 sentences |
| HWPR contains AI style | HWPR has obvious AI-expansion artifacts (boilerplate, "in summary," etc.) |
| AWOR contains value judgments | AWOR contains "we decided" / "gave up" etc. that should be HWPR content |
| Incorrect marker format | Not using the standard `**[HWPR]**` / `**[AWOR]**` format |

Output format: List each issue + suggested fix.

---

## Examples

### Bad — HWPR too long, mixed with AI style

```markdown
**[HWPR]** Background and Judgment
> After in-depth analysis of user behavior data and multi-dimensional competitive market research,
> our team discovered that the core problem lies in the new user onboarding experience not being smooth enough,
> which has led to a first-day retention rate of only 35%, significantly below the industry average of 50%.
> Based on the above analysis, we believe we should start by simplifying the onboarding flow,
> improving user experience through reducing step count and optimizing interaction design... (200 words)
```

Problem: HWPR is too long; contains AI boilerplate ("after in-depth analysis," "multi-dimensional," "significantly below").

### Good — HWPR is concise, focused on judgments

```markdown
**[HWPR]** Background
> New user first-day retention is 35%. I believe the main cause is onboarding being too complex (5 steps).
> Plan to simplify to 2 steps first, targeting 45% retention.

**[AWOR]** Detailed Analysis
User growth data over the past three quarters: Q1 retention 38%, Q2 35%, Q3 33%, showing a continuous decline.
Competitor comparison: Product A's onboarding has only 2 steps with 52% first-day retention...
```

---

## Exemptions

| Scenario | Condition |
|------|------|
| Pure record documents | Meeting minutes and other pure records without value judgments — HWPR may be omitted |
| Existing mature templates | Weekly reports and other documents with fixed formats — only add HWPR to "judgment/decision" sections |

---

## References

- [HWPR/AWOR Document Template](examples/TEMPLATE-HWPR.md)
- Inspiration: Pu Li's HWPR/AWOR documentation methodology
