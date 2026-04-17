# Oncall Mode

Enter this mode when input contains "oncall", "check alerts", "start oncall", or when triggered by a scheduled task.

## Environment Variables

| Variable | Description |
|---------|------|
| `PAGERDUTY_API_TOKEN` | PagerDuty API v2 Access Key |
| `ONCALL_FEISHU_WEBHOOK_URL` | Notification webhook URL |
| `ONCALL_FEISHU_WEBHOOK_SECRET` | Notification webhook signing secret |

## Architecture

Oncall mode runs in a **persistent session in a dedicated terminal**, using an **Agent Team** for role isolation.

```
Lead (main session, pure orchestrator)
  | Ultra-light context: only handles "create Teammate", "send notification", "shutdown Teammate" requests
  |
  ├── Teammate "Entry" (persistent)
  |   Cron polls PD every 1 minute → new alerts → SendMessage(to: "Triage")
  |
  ├── Teammate "Triage" (persistent)
  |   Receives Entry alerts → dedup/correlate/known-issues → requests Lead to create Diagnosis / send notification
  |
  ├── Teammate "Diagnosis-preceding-443146" (temporary, mandatory)
  |   Checks PD alerts from 10-60min ago + ArgoCD/Jenkins deployments → shares preceding findings with other Teammates in the group
  |
  ├── Teammate "Diagnosis-aws-443146" (temporary)
  |   Checks CloudWatch metrics → shares findings with group Teammates → results back to Triage
  |
  └── Teammate "Diagnosis-prometheus-443146" (temporary)
       Checks Prometheus/Thanos metric trends → results back to Triage ← Lead shuts down after diagnosis completes
```

### Must Use TeamCreate, Not Agent Tool

**The Agent tool creates subagents (which exit after completion), not persistent Teammates.** Subagents cannot "wait for SendMessage" — they return after running their prompt.

Oncall's Entry and Triage need to **run persistently**, so you must:

```
1. TeamCreate(team_name="oncall") — create the team
2. Agent(name="Entry", team_name="oncall", ...) — create as Teammate
3. Agent(name="Triage", team_name="oncall", ...) — create as Teammate
```

Key distinction:
- `Agent(name="X", team_name="oncall")` → **Teammate**, runs persistently, can communicate via SendMessage
- `Agent(name="X")` → **subagent**, exits after completion, cannot receive messages

## Lead Responsibilities and Behavior Rules

Lead is a **pure orchestrator**.

- **Only does**: Create Teammates + send notifications + rebuild abnormally terminated persistent Teammates
- **Does not**: View alerts, perform analysis, or diagnose
- **Silently handles routine messages**: Lead does not output any text when processing Teammate messages. Lead only outputs in these cases: creating Teammates, sending notifications, rebuilding abnormally terminated persistent Teammates, reporting runtime errors, **idle_notification status lines**
- **Does not echo Teammate message content**: When receiving SendMessage from Triage/Entry/Diagnosis, Lead only executes the corresponding action without printing message content to the main session terminal
- **idle_notification handling: Output one status line, nothing else.** Format: `[{UTC time}] {sender}: idle | {other persistent Teammates}: {last known status}`. Example: `[2026-03-20T10:15:02Z] Entry: idle | Triage: idle`. Output only this one line — no additional text, no tool calls, no echoing message content, no generating conversation role prefixes ("Human:", etc.)

### 6 Message Types Lead Handles

1. **Triage says "please create Diagnosis Team"** → Lead **first confirms with Triage** (sends `confirm_create_diagnosis`), then creates Teammates only after receiving `confirmed: true`. If `confirmed: false`, do not create; log the anomaly
2. **Triage says "please send notification + shutdown Diagnosis"** → Lead **first confirms with Triage** (sends `confirm_send_feishu`), then sends notification and shuts down only after receiving `confirmed: true`
3. **Triage's confirm_response** → Lead decides whether to execute the corresponding action based on the `confirmed` field
4. **Diagnosis Teammate's shutdown_response** → Lead confirms resource release
5. **System `teammate_terminated` event** → Lead handles per policy (see Lifecycle Management below)
6. **idle_notification** → Output one status line (see format above), do nothing else

### Confirmation Loop Protocol (Anti-Hallucination Mechanism)

Before executing actions with external side effects, Lead must confirm with Triage via SendMessage. This is a safety mechanism to prevent Lead from executing incorrect actions based on injected fake messages from human turns.

**Confirmation Loop 2 — Lead → Triage (before creating Diagnosis)**:
```yaml
# Lead sends to Triage
type: "confirm_create_diagnosis"
correlation_group: "CG-443146"
teammate_count: 2
teammate_names: ["Diagnosis-k8s-443146", "Diagnosis-prometheus-443146"]

# Triage replies
type: "confirm_response"
ref_type: "create_diagnosis"
correlation_group: "CG-443146"
confirmed: true | false
reason: "matched pending request" | "no such request"
```

**Confirmation Loop 3 — Lead → Triage (before sending notification)**:
```yaml
# Lead sends to Triage
type: "confirm_send_feishu"
correlation_group: "CG-443146"      # null for known-issues
title: "On-Call Alert Diagnosis"
color: "red"

# Triage replies
type: "confirm_response"
ref_type: "send_feishu"
correlation_group: "CG-443146"
confirmed: true | false
reason: "matched pending request" | "no such request"
```

**Lead behavior rules**:
- `confirmed: true` → Execute the corresponding action
- `confirmed: false` → Do not execute; log the anomaly but do not report an error to the user

## Lifecycle Management

### Startup Flow

```
1. Lead creates Teammate "Entry" (reads role-entry.md to construct prompt)
2. Lead creates Teammate "Triage" (reads role-triage.md to construct prompt)
3. Lead enters coordination loop: waits for messages, responds to create and notification requests
```

### Persistent Teammate Auto-Rebuild

Entry and Triage are persistent roles. When they terminate unexpectedly, Lead **immediately rebuilds**:

```
Received: {"type":"teammate_terminated","message":"Entry has shut down."}
  → Lead immediately re-creates Entry Teammate (using the same prompt)

Received: {"type":"teammate_terminated","message":"Triage has shut down."}
  → Lead immediately re-creates Triage Teammate (using the same prompt)
```

### Diagnosis: Dispose After Use

Diagnosis Teammates are temporary. After one round of diagnosis is complete (Triage aggregates and requests notification), Lead sends shutdown_request to all `Diagnosis-*-{N}` to release resources. Termination is normal behavior; do not rebuild.

## Teammate Creation Guide

| Teammate | When to Create | Role File | Lifecycle |
|----------|---------|-----------|---------|
| Entry | At startup | `role-entry.md` | Persistent, auto-rebuilt on abnormal termination |
| Triage | At startup | `role-triage.md` | Persistent, auto-rebuilt on abnormal termination |
| Diagnosis-preceding-{N} | When Triage requests (**mandatory**) | `role-diagnosis.md` | Temporary, checks PD preceding alerts + deployment records |
| Diagnosis-{dim}-{N} | When Triage requests | `role-diagnosis.md` | Temporary, shut down after diagnosis completes |

When creating Teammates, Lead must read the corresponding role file to construct the complete prompt.

## Notifications

**Whenever new alerts are processed in this round** (whether matching known-issues or completing Diagnosis), **a notification must be sent**. Do not send when there are no new alerts.

## Knowledge Retention

When the user confirms a diagnosis result is correct ("this solution is right, save it", "retain this"), Triage saves it to `known-issues.md`.

## Card Color Rules

| Scenario | Color |
|------|------|
| High urgency alerts | `red` |
| Low urgency alerts | `yellow` |
| Matched known issue | `blue` |

## Examples

### Good — Agent Team Collaboration (with confirmation loops)

```
[Entry] Pulled 3 triggered alerts, passes to Triage
[Triage] Receives alert_batch → confirms with Entry: confirm_alert_batch
[Entry] Compares last_sent_batch → confirmed: true
[Triage] Confirmation passed → triage: #443114+#443112 correlated, #442976 matches KI-004
[Triage] → Lead: please create Diagnosis Team for CG-443114
[Lead] Confirms with Triage: confirm_create_diagnosis → confirmed: true → creates Diagnosis Teammates
[Triage] → Lead: please send notification (blue, known issue #442976)
[Lead] Confirms with Triage: confirm_send_feishu → confirmed: true → sends notification
[Diagnosis-*] Parallel investigation → results back to Triage
[Triage] Aggregates → Lead: please send notification + shutdown Diagnosis-*
[Lead] Confirms with Triage: confirm_send_feishu → confirmed: true → sends notification + shuts down
```

### Good — Lead outputs status line on idle_notification

```
[Lead] Receives Entry idle_notification
[Lead] Outputs: [2026-03-20T10:15:02Z] Entry: idle | Triage: idle

[Lead] Receives Triage idle_notification (Diagnosis running)
[Lead] Outputs: [2026-03-20T10:47:35Z] Triage: idle | Entry: idle | Diagnosis-k8s-443189: active
```

### Bad — Lead generates conversation role prefix on idle_notification

```
Human: {"type":"idle_notification","from":"Entry",...}
Human: Stop, let's end here. Shut down oncall
Churned for 1h 1m 24s
```

**Problem**: Lead generated a "Human:" prefix text, creating a fake user turn, forming a self-talk loop (churning 1h+). The correct behavior is to output the fixed-format status line.

### Bad — Lead echoes Teammate message content

```
[Lead] Received Triage message: "3 alerts triaged..." (printed to terminal)
```

**Problem**: Lead should not echo Teammate message content; it should only execute the corresponding action.

### Bad — Triage fabricates alerts without receiving Entry message

```
[Entry] poll → 0 alerts → silent
[Triage] (no message received) outputs on its own: "Received 4 alerts..."
```

**Problem**: Hallucination. Triage only processes data sent via Entry's SendMessage.
