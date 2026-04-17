# Diagnosis Mode (Direct Invocation)

Enter this mode when a user directly provides alert details. For diagnostic methodology and investigation dimensions, see `role-diagnosis.md`.

Core behavior: Diagnose autonomously without asking the user questions. After diagnosis completes, output the incident_report directly; do not ask "Need further investigation?"

## Routing

- **Simple alerts** (certificate expiry, disk full, known issues) → Main agent handles directly, no parallelism needed
- **Complex alerts** (service unavailable, performance degradation, cross-service cascading) → Create Agent Team for parallel investigation

## Processing Flow

All alerts go through Diagnosis uniformly, without distinguishing "simple/complex":

1. Match against `known-issues.md`
   - Match found and expected_evidence meets the standard → Create standard Diagnosis Team + Diagnosis-verify (parallel)
   - Match found but expected_evidence does not meet the standard → Create standard Diagnosis Team only
   - No match → Create standard Diagnosis Team only
2. `TeamCreate(team_name="diagnosis")`
3. Select dimension combinations based on alert type (refer to the data source recommendation matrix in `role-diagnosis.md`)
4. Create a Teammate for each dimension (read `role-diagnosis.md` to construct prompt)
5. Teammates share findings with each other via SendMessage
6. Aggregate all results → output incident_report
7. Send notification using `capability-feishu.md`
8. Shutdown all Diagnosis Teammates

## Teammate Creation Guide

| Teammate | When to Create | Role File |
|----------|---------|-----------|
| Diagnosis-preceding-{N} | **All alerts (mandatory)** | `role-diagnosis.md` (checks PD alerts from 10-60min ago + deployment records) |
| Diagnosis-{dim}-{N} | All alerts | `role-diagnosis.md` |
| Diagnosis-verify-{ki_id}-{N} | When KI match and evidence meets the standard | `role-diagnosis.md` (verify_task input) |
