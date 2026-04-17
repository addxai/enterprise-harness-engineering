# Unified Report Standard

This file is the **single authoritative definition** of the incident_report YAML structure and notification content mapping.
Both Diagnosis and Triage reference this file; inline definitions in individual role files are no longer used.

---

## Part 1: incident_report YAML Structure

### YAML Template

```yaml
type: "incident_report"

# 1. Alert Summary
alert_summary:
  incidents:
    - incident_id: "INCIDENT_ID"
      incident_number: 443146
      title: "[Region][Env][critical] service-name alert-type"
      status: "triggered"
  entity: "service-name"
  service: "service-name"
  cloud_account: "provider-account-id"
  cluster: null
  environment: "region-env"
  region: "cloud-region"
  severity: "P1"
  triggered_at: "2026-03-20T08:10:00Z"
  diagnosed_at: "2026-03-20T08:18:00Z"
  pagerduty_url: "https://your-org.pagerduty.com/incidents/INCIDENT_ID"

# 2. Diagnosis Process
diagnosis_process:
  dimensions_investigated:
    - dimension: "cloud-monitoring"
      what: "Service CPU, connections, memory"
      result: "Found CPU 85%, single node, connections stable"
    - dimension: "prometheus"
      what: "7d metric trends"
      result: "Confirmed +1.5%/day growth, not sudden"
  dimensions_not_available:
    - dimension: "application-logs"
      reason: "No log integration, cannot confirm application-layer state"
  cross_validation: "Two data sources show consistent trends"

# 2.5 Trend Data (required when metric trends are involved)
trend_data:
  - metric: "CPUUtilization"
    unit: "%"
    current: 85
    change_pattern: "gradual"    # spike | gradual | step | periodic | recovery
    scope: "prod service-name"
    source: "prometheus + cloudwatch"
    window_24h:
      start: 82
      end: 85
      delta: "+3"
      rate: "+0.125%/h"
      trend: "rising"
    window_7d:
      start: 74
      end: 85
      delta: "+11"
      rate: "+1.57%/d"
      trend: "rising"
      periodicity: "daily peak 88%"
    prediction:
      method: "linear_extrapolation"
      threshold: 90
      eta: "~7d"
      query: "predict_linear(cpu_utilization[24h], 604800)"

# 3. Timeline (required)
timeline:
  - time: "2026-03-13T00:00:00Z"
    event: "CPU daily average started rising from 74%"
    source: "prometheus"
  - time: "2026-03-20T08:10:00Z"
    event: "PagerDuty alert triggered: high-cpu"
    source: "pagerduty"

# 4. Root Cause
root_cause:
  summary: "Single-node capacity insufficient, trending to threshold within 7 days"
  detail: "Detailed analysis..."
  confidence: "medium"
  reasoning: "Cross-validated with two data sources..."

# 5. Impact Scope (required)
impact:
  affected_services:
    - name: "service-name"
      type: "service-type"
      environment: "prod"
      status: "degraded"
  affected_users: "Users of the affected service"
  blast_radius: "Single service instance, no cross-service impact"
  data_loss_risk: false

# 6. Risk Assessment (required)
risk_assessment:
  current_risk: "medium"
  trend: "worsening"
  eta_to_critical: "~7d"
  eta_source: "trend_data[0].prediction"
  single_point_of_failure: true
  auto_recovery_possible: false

# 7. Solutions
solutions:
  short_term:
    - action: "Scale up service"
      prompt: |
        Use cloud-cli to scale the service...
        1. Query current configuration
        2. Scale to target size
        3. Verify new capacity
  long_term:
    - "Add capacity prediction alerting"
```

### Field Completion Guide

- `alert_summary`: The `incidents` list is carried back from diagnosis_task input; supplement cloud_account/region (look up from infra-context.md); severity is assessed post-diagnosis
- `trend_data`: Required when trend analysis is involved. Both `window_24h` and `window_7d` must be filled. `change_pattern` is required
- `diagnosis_process`: Record which dimensions were actually investigated and conclusions
- `timeline`: Required; list key events in chronological order
- `root_cause`: summary in one sentence, detail expands; confidence assessed against confidence standards
- `impact`: Required; list affected services and their status
- `risk_assessment`: Required; `eta_source` is required when `eta_to_critical` has a value
- `solutions.short_term`: Object list; each item contains `action` and `prompt` (both required)
- `solutions.long_term`: Plain string list

### cloud_account / environment Naming Convention

Use cloud provider prefix + account ID standard format (e.g., `aws-123456`, `gcp-project-name`).
Environment uses region-environment format (e.g., `us-prod`, `eu-staging`).

---

## Part 2: Notification Content Mapping Rules

Diagnosis reports are sent using `send-elements` format. Section mapping:

```
elements structure               <- incident_report field
----------------------------------------------
[markdown] Alert Summary
[table] Key-Value                <- alert_summary
[hr]
[markdown] Timeline
[table] Time / Source / Event    <- timeline[]
[hr]
[markdown] Trend Data (optional)
[table] Metric / Current / 24h / 7d <- trend_data[]
[hr]
[markdown] Root Cause [confidence] <- root_cause
[hr]
[markdown] Impact
[table] Service / Status / Detail <- impact
[hr]
[markdown] Risk Assessment
[table] Key-Value                <- risk_assessment
[hr]
[markdown] Short-term Actions    <- solutions.short_term[].action (not prompt)
[hr]
[markdown] Long-term Actions     <- solutions.long_term[]
```

### Format Standards

- Tables use native table components, not markdown table syntax
- All column widths use `px` format (minimum 80px), no mixing `auto` and `px`
- Multi-item content must use line breaks, not single-line compact format
- `prompt` is NOT displayed in notifications -- kept in YAML for execution

---

## Part 3: Required Fields Summary

| Section | Field | Required | Notes |
|---------|-------|----------|-------|
| alert_summary | incidents, entity, service, cloud_account, environment, region, severity, triggered_at, diagnosed_at, pagerduty_url | Yes | |
| diagnosis_process | dimensions_investigated, cross_validation | Yes | |
| trend_data | (entire section) | Conditional | Required when trend analysis involved |
| timeline | (entire section) | Yes | |
| root_cause | summary, detail, confidence, reasoning | Yes | |
| impact | affected_services, affected_users, blast_radius, data_loss_risk | Yes | |
| risk_assessment | current_risk, trend, eta_to_critical, single_point_of_failure, auto_recovery_possible | Yes | |
| solutions | short_term (action + prompt per item) | Yes | At least one item |
