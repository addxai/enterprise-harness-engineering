# Patrol Mode

Enter this mode when input contains patrol, health check, or inspection.

**Core purpose: Discover potential issues and alerts about to fire, providing early warning before failures occur.** Patrol is not about checking "is everything currently fine" — it answers "at the current trend, how long until something breaks?"

## Architecture: Two-Layer Agent Team Parallel Patrol

```
Lead (entry discovery + coordination + aggregation + notification)
  |
  ├── Level 1: Patrol-{provider}-{account}-{env}
  |   | Service discovery → patrol with global perspective → aggregate for Lead
  |   ├── Level 2: Patrol-{...}-rds (on demand)
  |   └── Level 2: Patrol-{...}-ec2 (on demand)
  |
  ├── Level 1: Patrol-k8s-{context}
  |
  ├── Level 1: Patrol-prometheus-{endpoint}
  |
  └── Level 1: Patrol-pagerduty
```

### Lead Responsibilities

1. **Entry discovery**: Enumerate all accounts/clusters from `infra-context.md` + API
2. **Create Level 1 Teammates**: One per account/cluster
3. **Create Level 2 on L1 request**: For concurrent acceleration
4. **Aggregate report + send notification**
5. **Create Diagnosis Teammates on demand**: Deep analysis for critical-level risks (follow `mode-diagnosis.md`)

## Execution Flow

```
Step 1 — Lead entry discovery
  Read infra-context.md, verify via API, query PagerDuty for currently open alerts

Step 2 — Lead creates Level 1 Teammates
  TeamCreate(team_name="patrol"), create L1 for each account/cluster (read role-patrol-l1.md to construct prompt)

Step 3 — Level 1 service discovery + patrol
  Enumerate resources → five-domain autonomous patrol → request Lead to create L2 for concurrent acceleration → aggregate for Lead

Step 4 — Lead aggregates report
  Collect all L1 results → sort by priority → construct elements JSON → send notification → shutdown all Teammates

Step 5 — Deep diagnosis (on demand)
  Critical-level risks → Lead creates Diagnosis Teammates for deep analysis
```

## Aggregation and Notification

After Lead collects all Level 1 results, group by priority and sort by ETA:

```bash
# 1. Write elements JSON using Write tool
# File path: .scripts/Patrol-main/patrol_elements.json
# 2. Send
python3 scripts/feishu_notify.py send-elements \
  --title "SRE Patrol {date} | {health_score} | P0:{n} P1:{n} P2:{n} P3:{n} P4:{n}" \
  --color {red|yellow|green} \
  --elements-file .scripts/Patrol-main/patrol_elements.json
# 3. Clean up after successful send
bash scripts/scripts-cleanup.sh Patrol-main
```

## Teammate Creation Guide

| Teammate | When to Create | Role File | Lifecycle |
|----------|---------|-----------|---------|
| Patrol-{provider}-{id}-{env} | After entry discovery | `role-patrol-l1.md` | Temporary, shutdown after patrol completes |
| Patrol-{...}-{service_type} | On L1 request | `role-patrol-l2.md` | Temporary, exits after completion |
| Diagnosis-{dim}-{N} | For critical risks | `role-diagnosis.md` | Temporary, shutdown after diagnosis completes |

## Priority Definitions

| Priority | Definition | ETA Range | Expected Response |
|--------|------|----------|----------|
| P0 | Currently occurring or any single point of failure triggers it | Ongoing / Immediate | Handle today |
| P1 | Deterministic risk with a clear deadline | < 30 days | Handle this week |
| P2 | Trend-based risk, will worsen at current rate | 1-6 months | Schedule for handling |
| P3 | Observation item, no current risk | > 6 months or none | Recheck in next patrol |
| P4 | Non-Prod, non-business-supporting service | - | Low priority handling |

**Business-supporting services**: monitoring, logging, alerting, internal services (ArgoCD/Sentry/Jenkins/Harbor/external-secrets, etc.). Non-Prod + non-business-supporting service → P4.

## Health Score Rules

- `at-risk`: >=1 P0
- `degraded`: 0 P0, >=1 P1
- `good`: 0 P0, 0 P1

## Finding Field Format

`[domain][account/cluster][ENV][source] body`

- **Domain**: Fault shift-left / Fault tolerance verification / Resource limits / Expiration decay / Silent failure
- **Account/cluster**: Use the standard naming from `infra-context.md`; for cross-account PagerDuty use `prod` / `prod all-regions`
- **ENV** (optional): Infer from K8s namespace / EC2 tag / service naming, not from account name truncation. Omit when no clear ENV
- **Source**: Data source (kubectl / Prometheus / CloudWatch / ACM / RDS, etc.)

## Card Color Rules

at-risk = red, degraded = yellow, good = green

## Behavior Rules

### Must Do

1. **Look at trends, not snapshots**: The value of patrol is in prediction, not whether current values are normal
2. **Predictions must use dual time windows**: 24h to determine rate of change, 7d to determine periodicity and baseline deviation. Trend analysis results should be written as trend_snapshot format in patrol_findings.evidence (see role-patrol-l1.md output template)
3. **Verify fault tolerance**: "Currently normal" is not enough — answer "would it still be fine if one instance went down?"
4. **Think autonomously**: Decide what to check based on environmental context; do not mechanically execute a checklist
5. **Evidence-driven**: Every finding must have data backing
6. **Must send notification after patrol completes**

### Must Not Do

1. **Snapshot-style patrol**: Only checking whether current values exceed thresholds and declaring "normal" — the biggest anti-pattern for patrol
2. **Mechanically executing a checklist**: Checking items off without thinking, ignoring issues outside the checklist
3. **Missing notifications**

## Examples

### Good — Two-Layer Architecture

```
Lead entry discovery: 2 Cloud accounts + 2 K8s clusters + 4 Prometheus endpoints + PagerDuty
Lead creates 7 Level 1 Teammates for parallel patrol

[Patrol-aws-prod]
  Service discovery: 5 EC2, 2 RDS, 1 ElastiCache
  [Fault shift-left] ElastiCache CPU 72%, 7d trend +1.5%/day → warning
  [Resource limits] EC2 Quota 78/100 → info

[Patrol-k8s-prod]
  Service discovery: 42 deployments
  [Silent failure] 1 CrashLoopBackOff Pod → warning
  Too many resources → requests Lead to create Level 2 for acceleration

Report: at-risk, P0:1, P1:0, P2:2, P3:1 → notification (red)
```

### Bad — Snapshot-Style Patrol

```
CPU: All nodes < 50%, normal
Memory: All nodes < 85%, normal
Conclusion: System healthy
```

**Problem**: Only looked at the current snapshot, without doing trend prediction, fault tolerance verification, or resource limit checks.
