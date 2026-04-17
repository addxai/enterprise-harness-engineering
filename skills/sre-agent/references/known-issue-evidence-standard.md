# expected_evidence Quality Standard

This file defines the quality standard for `expected_evidence` in known-issues entries. Triage and iteration mode share this standard:

- **Triage**: Determines whether a known-issue's expected_evidence meets the standard to decide whether to create a Diagnosis-verify
- **Iteration mode**: Validates expected_evidence quality when adding/modifying known-issues

## Three Required Properties Per Evidence Item

Each expected_evidence item must simultaneously satisfy all three properties; none may be missing:

| Property | Definition | Qualifying Example | Non-qualifying Example |
|------|------|---------|-----------|
| **Quantifiable** | Has clear numerical values, thresholds, or enumerable states | "Maintenance event state is PENDING or IN_PROGRESS" | "Kafka looks like it is in maintenance" |
| **Data-backed** | Can be obtained through specific data sources and query methods | "Query via cloud CLI API" | "Ask the ops team" |
| **Deterministic** | Has clear true/false determination criteria | "Maintenance window covers alert trigger time +/-2h" | "Timing roughly matches" |

## Single Evidence Item Format

```yaml
expected_evidence:
  - description: "Managed service has active maintenance operation"
    data_source: "cloud-cli"
    query_hint: "Query maintenance operations via cloud provider CLI/API"
    condition: "Active maintenance operation found with state PENDING or IN_PROGRESS"
  - description: "Alert trigger time falls within maintenance window"
    data_source: "pagerduty + cloud-cli"
    query_hint: "Compare alert triggered_at with operation time window"
    condition: "triggered_at within [operation.start - 30min, operation.end + 30min]"
```

## verification_threshold

```yaml
verification_threshold:
  min_verified: 2
  total_evidence: 3
```

- `min_verified >= 2`: At least 2 evidence items must pass to be considered verified
- If `total_evidence < 2`, the known-issue does not meet the criteria for creating a verify task

## Triage Decision Flow

```
Match known-issue
  → Read that KI's expected_evidence
  → Check each item against the three properties:
      All satisfied + total_evidence >= 2
        → Create Diagnosis-verify + regular Diagnosis (in parallel)
      Any item fails OR total_evidence < 2
        → Only create regular Diagnosis
        → Annotate in create_diagnosis_request:
            ki_match: {ki_id: "KI-XXX", reason: "expected_evidence does not meet verification standard: {specific reason}"}
```

## Iteration Mode Validation Flow

When adding or modifying a known-issue, expected_evidence must be validated item by item:

1. Whether each evidence item simultaneously satisfies quantifiable, data-backed, and deterministic
2. `total_evidence >= 2`
3. `verification_threshold.min_verified >= 2`
4. Whether data sources/skills referenced in `query_hint` are available

When criteria are not met, reject the write and request the user to provide additional information.
