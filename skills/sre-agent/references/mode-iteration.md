# Iteration Mode

Enter this mode when input contains "iterate", "improve sre-agent", "retrospective", "optimize skill", or the user requests a review of diagnosis quality.

## Core Principles

### Don't Write Runbooks for AI — Reduce the Information Gap Instead

AI already possesses diagnostic reasoning capabilities; it doesn't need prescriptive "step 1: check kubectl, step 2: check Prometheus" instructions. The improvement direction for sre-agent is:

- **Expand information accessibility**: Add available data sources and Skills so AI can obtain more information
- **Improve information quality**: Optimize endpoint mappings, metric naming, and alert descriptions so AI understands context faster
- **Reduce the information gap**: Fill in information that AI needs but currently lacks (e.g., new Prometheus endpoints, new K8s contexts)
- **Don't prescribe flows**: Don't dictate "must check A before B" — let AI judge the best path based on the problem

### Don't Limit AI Capabilities

When iterating, the philosophy is to expand AI's toolbox and information surface, not restrict AI's behavior:

- **Add, don't restrict**: When AI lacks a data source during diagnosis → add a new capability/skill, don't write more detailed Runbooks
- **Guide, don't command**: The data source matrix is a "recommended starting point", not "mandatory steps"
- **Rules stem from lessons**: Every rule in diagnostic discipline traces back to a real failure, not arbitrary prescriptions

## Iteration Sources

### 1. Diagnosis Quality Feedback

Issues discovered by users during oncall/diagnosis:

- "AI didn't check data source X" → Does a capability or infra-context need to be added?
- "AI got the causal direction wrong" → Does diagnostic discipline need a new rule?
- "AI guessed the endpoint name and failed" → Does infra-context.md need to be supplemented?
- "AI diagnosis conclusion was correct" → Is it worth saving to known-issues?

### 2. Incident Retrospectives

Lessons extracted after each real incident:

- **Diagnostic discipline**: What went wrong during this diagnosis? What new rules are needed?
- **Patrol Playbook**: If patrol had run earlier, could it have detected this issue? Extract new check items.
- **Known issues**: Are the root cause and solution from this incident worth saving to known-issues?
- **Infrastructure context**: Were new endpoints, clusters, or IP mappings discovered that need to be added?

### 3. Patrol Findings

Findings from patrol mode runs:

- Do thresholds in the patrol Playbook need adjustment?
- Were new failure patterns discovered that should be added to the Playbook?
- Are the PromQL queries in the patrol effective in the real environment?

## Execution Flow

### Step 1: Collect Feedback Input

Input can be:
- Improvement suggestions directly described by the user
- A conversation log from an oncall/diagnosis session (retrospective)
- A specific diagnosis failure case

### Step 2: Analyze Root Cause

Compare against sre-agent's current rules and resources to locate which layer the problem belongs to:

| Problem Layer | Typical Manifestation | Target File for Improvement |
|--------|---------|------------|
| Information gap | AI doesn't know a certain endpoint/cluster/IP mapping | `infra-context.md` |
| Capability gap | AI has no available data source to check certain information | `capability-*.md` or create new |
| Diagnostic discipline | AI made an avoidable reasoning error | `mode-diagnosis.md` |
| Triage logic | Alert correlation/deduplication inaccurate | `mode-oncall.md` |
| Patrol coverage | Failure could have been detected earlier by patrol | `patrol-playbook.md` |
| Known issues | Recurring failures should accelerate diagnosis | `known-issues.md` |
| Notification format | Notification has too little or too much information | `capability-feishu.md` |

### Step 3: Implement Improvements

Read the corresponding file, propose specific modifications (add/modify/delete), and execute after user confirmation.

**Improvement principles:**
- Every improvement must trace back to a specific problem instance
- New rules must have Bad/Good Examples
- New patrol items must have an origin (source incident)
- Thresholds come from real data, not arbitrary values

### Known-Issue Writing Rules

When adding or modifying entries in `known-issues.md`, the quality standards in `known-issue-evidence-standard.md` must be followed:

1. **expected_evidence is required**: Each piece of evidence must simultaneously satisfy quantifiable, data-driven, and judgeable criteria
2. **At least 2 pieces of evidence**: `total_evidence >= 2`, otherwise Triage cannot create Diagnosis-verify
3. **verification_threshold is required**: `min_verified >= 2`
4. **query_hint must be executable**: Referenced data sources/skills must be within sre-agent's available scope
5. **Validate each item**: Iteration mode checks each item before writing; if standards are not met, reject the write and require supplementation

### Step 4: Verify Improvements

After improvements are implemented, it is recommended to:
- If diagnostic discipline was changed → Re-diagnose with the same alert input to confirm behavior changed
- If patrol Playbook was changed → Run a patrol to confirm the new check items are executable
- If infra-context was changed → Confirm the new endpoints are accessible

## Diagnosis Quality Assessment Framework

Iteration mode can proactively assess past diagnosis quality:

```yaml
diagnosis_review:
  incident_id: string

  accuracy:
    root_cause_correct: boolean
    confidence_calibrated: boolean

  completeness:
    data_sources_used: number
    correlated_alerts_found: boolean
    timeline_verified: boolean

  efficiency:
    unnecessary_queries: number
    missed_shortcuts: [string]

  learnings:
    new_rule_needed: string
    new_playbook_item: string
    infra_context_gap: string
    known_issue_candidate: string
```

## Examples

### Good — Extracting improvements from a retrospective

```
User: Let's do a retrospective on this gateway CPU alert investigation

[Iteration mode]

Analyzing issues from this investigation:

1. Issue: Inferred "restart caused high CPU" based solely on SSH snapshot
   Root cause: Missing "causal direction verification" rule
   Improvement: Add diagnostic discipline to mode-diagnosis.md
   → Implemented

2. Issue: Guessed wrong Prometheus endpoint name
   Root cause: infra-context.md was missing this endpoint
   Improvement: Add endpoint to infra-context.md
   → Implemented

3. Issue: Did not first check PagerDuty correlated alerts
   Root cause: Correlated alert check was not a mandatory step
   Improvement: Add diagnostic discipline to mode-diagnosis.md
   → Implemented

4. Issue: If patrol had run earlier, it could have detected the cluster lacked fault tolerance
   Improvement: Add patrol-playbook.md check item (long-connection cluster fault tolerance assessment)
   → Implemented
```

### Bad — Runbook-style improvement

```
User: Improve the CPU alert diagnosis flow

Improvement plan:
1. After receiving a CPU alert, step 1 must check Prometheus CPU history
2. Step 2: check SSH top 10 processes
3. Step 3: check JVM heap usage
4. Step 4: check recent deployments...
```

**Problem**: This is writing a Runbook, which restricts AI's diagnostic path. The correct approach is to reduce the information gap (ensure AI can access Prometheus, SSH, JVM metrics) and let AI determine the best path on its own.
