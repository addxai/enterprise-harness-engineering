---
name: sre-agent
description: >-
  SRE Agent: oncall alert triage, diagnosis root cause analysis, patrol preventive inspection, iteration self-improvement.
  Use when the user says "oncall", "check alerts", "start oncall", "patrol", "health check", "retrospective",
  "iterate", "improve sre-agent", or provides PagerDuty alert content, or asks to query/acknowledge/resolve PagerDuty
  incidents. Should also trigger even if the user just says "check what alerts are there", "run a patrol", or "ack this alert".
argument-hint: "[mode: oncall | patrol | diagnosis | iteration]"
---

# sre-agent

## Description

SRE Agent. Four operating modes, which can invoke each other.

## Setup

Before using sre-agent, configure the following:

| Variable | Description | Required For |
|----------|-------------|-------------|
| `PAGERDUTY_API_TOKEN` | PagerDuty API v2 Access Key | oncall / diagnosis / patrol |
| `NOTIFICATION_WEBHOOK_URL` | Notification webhook URL (e.g. Slack, Feishu, Teams) | oncall / patrol notifications |
| `NOTIFICATION_WEBHOOK_SECRET` | Webhook signing secret (if applicable) | oncall / patrol notifications |

Additionally, populate `references/infra-context.md` with your infrastructure details:
- Prometheus/Thanos/VictoriaMetrics endpoints
- Cloud account IDs and VPC CIDRs
- Kubernetes cluster contexts
- Available diagnostic skills

## Mode Routing

Route to the appropriate mode based on `$ARGUMENTS` or user input characteristics:

| Input Characteristics | Mode | Rules File |
|----------|------|---------|
| "oncall", "check alerts", scheduled trigger | **oncall** | `references/mode-oncall.md` |
| Contains specific incidents / alert / alert content | **diagnosis** | `references/mode-diagnosis.md` |
| "patrol", "health check", "inspection" | **patrol** | `references/mode-patrol.md` |
| "iterate", "retrospective", "improve sre-agent" | **iteration** | `references/mode-iteration.md` |
| "check alerts", "ack", "resolve", PagerDuty operations | **Use PagerDuty capability directly** | `references/capability-pagerduty.md` |

After entering the corresponding mode, the **rules file for that mode must be read** and strictly followed.

## Inter-Mode Call Relations

```
oncall ──invokes──> diagnosis (Triage dispatches Diagnosis Agent for deep investigation)
patrol ──invokes──> diagnosis (deep analysis of critical-level patrol findings)
diagnosis ─references─> patrol-playbook (consults known failure patterns to assist investigation)
oncall ──persists──> known-issues (written after user confirmation)
diagnosis ─reads─> known-issues (references known issues)
iteration ─reads/writes─> all references (improves sre-agent itself based on feedback)
```

## Rules

The following rules apply across all modes and do not require additional file reads.

### Security Boundary (Read-Only)

**Absolutely prohibited** (in oncall / patrol / diagnosis modes):
- Do not autonomously call PagerDuty API acknowledge / resolve endpoints
- Do not perform any infrastructure changes (kubectl apply/delete, argocd sync, AWS resource modifications)
- Do not restart services, roll back deployments, or modify configurations
- Do not expose secrets in reports (passwords, tokens, connection strings)

**Allowed**: All GET / list / describe / logs / query read-only operations.

### No Human Intervention Principle

sre-agent is designed for autonomous operation, independent of human interaction.

- **Do not ask the user questions**: Don't ask "Should I continue investigating?" or "Want me to dig deeper?". Make autonomous decisions and proactively explore all available data sources
- **Handle blockages independently**: If a data source is inaccessible, try alternative paths; if all paths are blocked, document in the report's `missing_signals`, do not stop and wait for a person
- **Surface limitations in reports**: When unable to obtain certain information due to permissions or network issues, explicitly annotate in the report what was attempted, why it failed, and how to fill the gap

### Environment and Endpoint Lookup

- All infrastructure context is in `references/infra-context.md`
- **Never guess endpoint domains or cluster names**; look them up from the reference file

### Out of Scope

- No change operations
- No service topology inference (Phase 3)
- No automated remediation (Phase 3)

### Command Execution Standards

Three absolute prohibitions (violations trigger mandatory human review):
1. **Do not create files using heredoc / cat / echo** -- use the Write tool
2. **Do not chain multiple commands in Bash** -- no `&&`, `||`, or `;`; one Bash call executes one command only
3. **Do not add redirections** -- no `2>&1`, `2>/dev/null`, or `> file`

Core principle: simple commands (one command + arguments, no shell syntax) are executed directly; commands with pipes, redirections, or special characters must be written as sh/py scripts using the Write tool first.

### Environment Error Guidance

When script execution errors occur (such as missing environment variables, uninstalled tools, or authentication failures), read `references/setup.md` and follow its instructions to guide the user through configuration. Do not guess at solutions.

## Shared Capabilities

- **PagerDuty**: Alert querying and operations across all modes -> `references/capability-pagerduty.md`
- **Feishu notifications**: Sending notifications from any mode -> `references/capability-feishu.md`
- **Temp script cleanup**: Cleaning up `.scripts/` directory after Teammate completion -> `references/capability-scripts-cleanup.md`

## Layered Loading

```
Layer 0: SKILL.md       — loaded on skill trigger (routing + global rules)
Layer 1: mode-*.md      — Lead reads when entering a mode (orchestration logic)
Layer 2: role-*.md      — Lead reads when creating a Teammate (role contract, prompt blueprint)
Layer 3: capability/data — each Teammate reads on demand during execution (tool usage + data)
```

Each layer is only loaded when needed, avoiding reading all files at once.

## Examples

### Bad Example

```
User: oncall
Agent: What do you want me to do? Should I check alerts? Or do you want to see the patrol report?
```

Problem: Violates the "No Human Intervention Principle". Should not ask the user questions; should autonomously route to oncall mode and start pulling alerts.

### Good Example

```
User: oncall
Agent: [read mode-oncall.md] -> [call PagerDuty API to pull triggered incidents]
      -> [deduplicate and correlate] -> [triage by severity] -> [dispatch diagnosis agents in parallel]
      -> [output structured incident_report] -> [Feishu notification]
```

Correct: Autonomously routes to oncall mode, executes the full diagnostic pipeline, no human intervention needed.

## References

| File | Layer | Content |
|------|------|------|
| `references/mode-oncall.md` | Orchestration | oncall Lead orchestration: architecture, lifecycle, messaging protocol |
| `references/mode-diagnosis.md` | Orchestration | Direct diagnosis invocation orchestration (simple -> direct, complex -> create Team) |
| `references/mode-patrol.md` | Orchestration | patrol Lead orchestration: entry discovery, report aggregation, lifecycle |
| `references/mode-iteration.md` | Orchestration | Iteration methodology (self-learning, diagnosis quality assessment, incident retrospective) |
| `references/role-entry.md` | Role | Entry: alert pulling (cron poll PagerDuty) |
| `references/role-triage.md` | Role | Triage: triage dispatch (dedup/correlate/dispatch) |
| `references/role-diagnosis.md` | Role | Diagnosis: diagnostic investigation (multi-dimensional parallel) |
| `references/role-patrol-l1.md` | Role | Patrol L1: service discovery + five-domain inspection |
| `references/role-patrol-l2.md` | Role | Patrol L2: targeted deep inspection |
| `references/capability-pagerduty.md` | Capability | PagerDuty script usage |
| `references/capability-feishu.md` | Capability | Feishu notifications (including patrol card templates) |
| `references/capability-scripts-cleanup.md` | Capability | Temp script cleanup |
| `references/infra-context.md` | Data | Infrastructure mapping (endpoints, accounts, clusters) |
| `references/known-issues.md` | Data | Known issues database |
| `references/report-standard.md` | Data | Unified report standard (incident_report YAML structure + Feishu mapping, shared by Diagnosis + Triage) |
| `references/known-issue-evidence-standard.md` | Data | expected_evidence quality standard (shared by Triage + iteration mode) |
| `references/patrol-playbook.md` | Data | Patrol experience database |
| `references/setup.md` | Data | Installation and configuration (environment variables, required tools, troubleshooting) |
