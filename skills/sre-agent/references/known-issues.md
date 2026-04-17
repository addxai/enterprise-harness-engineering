# Known Issues and Solutions

Common issues confirmed by users after AI diagnosis are documented here. After Triage matches, they are passed as hypotheses to Diagnosis-verify for validation, rather than directly outputting a solution.

**Quality standard**: When adding/modifying entries, you must follow the expected_evidence quality standard in `known-issue-evidence-standard.md`.

## Format Description

Each record contains: matching keywords, root cause, solution, **expected_evidence (verification conditions)**, verification_threshold, and documented date.

New entries are written via iteration mode, which is responsible for validating expected_evidence quality.

---

## Template

### KI-NNN [Title]

- **Matching keywords:** `keyword1`, `keyword2`, `service-name`
- **Alert example:** Original alert title
- **Root cause:** Brief root cause description
- **Solution:**
  1. Step one
  2. Step two
  3. Step three
- **expected_evidence:**
  - description: "Evidence description (quantifiable)"
    data_source: "Data source/skill name (data-backed)"
    query_hint: "Query method hint"
    condition: "Clear true/false condition (deterministic)"
- **verification_threshold:**
  - min_verified: N (minimum evidence items that must pass, >=2)
  - total_evidence: N (total expected_evidence count, >=2)
- **Documented date:** YYYY-MM-DD
- **Notes:** Additional information (optional)

---

<!-- Add your known issues below using the template above -->
<!-- Example entries are provided as reference for the format -->

### KI-001 TLS/SSL Certificate Expiring

- **Matching keywords:** `ssl-expiring`, `ssl`, `certificate`, `tls`, `cert-expiring`
- **Alert example:** [Region][Env][critical][ssl] ssl-expiring
- **Root cause:** SSL/TLS certificate approaching expiration date
- **Solution:**
  1. Identify the certificate and domain from the alert
  2. Obtain/renew the certificate from your certificate provider
  3. Update the certificate in the appropriate location (K8s Secret, load balancer, etc.)
  4. Verify: `openssl s_client -connect <domain>:443 -showcerts`
- **expected_evidence：**
  - description: "Alert title contains certificate expiration keywords"
    data_source: "pagerduty"
    query_hint: "Check alert title for ssl-expiring, certificate, cert"
    condition: "Alert title matches regex `(?i)(ssl-expir|certificate.*expir|cert.*expir)`"
  - description: "Target domain certificate NotAfter within 30 days"
    data_source: "ssh-host skill"
    query_hint: "openssl s_client -connect {domain}:443 to check certificate expiration"
    condition: "Certificate NotAfter date is within 30 days of current time"
- **verification_threshold：**
  - min_verified: 2
  - total_evidence: 2
- **Documented date:** (configure)
- **Notes:** Recommend renewing certificates 7-14 days before expiration

---

### KI-002 Kafka Maintenance Alert Storm

- **Matching keywords:** `kafka`, `msk`, `zookeeper`, `broker`, `high-cpu`, `consumer-lag`, `kafka-port`, `tcpport-unavailable`, `kafka-scheduled-change`
- **Alert example:** [Region][Env][critical] kafka-related alerts during maintenance window
- **Root cause:** Managed Kafka (e.g. AWS MSK) or self-hosted Kafka performs periodic maintenance (rolling broker restart), triggering cascading alerts. All alerts are normal during maintenance and auto-recover within 10-20 minutes.
- **Solution:**
  1. Confirm maintenance is in progress (check cloud provider console or API)
  2. If in maintenance window: observe, all alerts should auto-recover
  3. Monitor consumer lag -- should return to normal within 30 minutes after maintenance
  4. If alerts persist 1 hour after maintenance ends, escalate to manual investigation
- **expected_evidence：**
  - description: "Managed Kafka cluster has active maintenance operation"
    data_source: "cloud-cli skill"
    query_hint: "Check cloud provider API for active maintenance operations"
    condition: "Active maintenance operation found with state PENDING or IN_PROGRESS"
  - description: "Alert trigger time falls within maintenance window"
    data_source: "pagerduty + cloud-cli skill"
    query_hint: "Compare alert triggered_at with maintenance operation time window"
    condition: "triggered_at within [operation.start - 30min, operation.end + 30min]"
  - description: "Alert pattern matches historical maintenance cascade"
    data_source: "pagerduty"
    query_hint: "Query all Kafka-related alerts within +/-2h window"
    condition: "At least 3 known cascade alert types present"
- **verification_threshold：**
  - min_verified: 2
  - total_evidence: 3
- **Documented date:** (configure)

---
