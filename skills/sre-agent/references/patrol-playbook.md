# Patrol Experience Reference Library

This file contains patrol experience distilled from historical incidents, for Patrol Teammates to reference.

**Positioning: Experience library, not a mandatory checklist.** The AI should independently think about what to check based on the five problem domains. This file provides "what went wrong in the past, and what check would have caught it earlier" as experience references. The AI can (and should) check areas not covered by this file.

**Maintenance rules:**
- Each entry must have an `origin` field indicating which incident or problem domain it came from
- PromQL / commands have been validated in practice
- Thresholds come from real incident data, not arbitrary settings
- As the environment changes (scaling, architecture adjustments), thresholds need updating

---

## PB-001 -- Long-Lived Connection Service Cluster Fault Tolerance Assessment

**Problem domain:** Fault tolerance verification
**Source incident:** Long-lived connection service CPU cascade failure
**Applicable services:** Gateway services or any service maintaining large numbers of long-lived connections

### Failure Mode

A single node carries too many connections with no redundancy headroom. If any one node goes down, connection redistribution overloads the remaining nodes → OOM → cascading avalanche.

### Reference Check Method

```promql
# Per-node connection count (adjust metric name to your environment)
service_connection_count{job=~"prod-gateway"}

# Cluster total connections
sum(service_connection_count{job=~"prod-gateway"})

# Node count
count(up{job=~"prod-gateway"} == 1)
```

### Reference Thresholds

| Parameter | Value | Source |
|------|-----|------|
| Known OOM threshold | ~185K connections/node | Historical incident data |
| Safe limit (85%) | ~157K | 185K x 0.85 |
| Warning line (70%) | ~130K | 185K x 0.70 |

---

## PB-002 -- JVM Old Gen Memory Leak Detection

**Problem domain:** Shift-left fault detection
**Source incident:** JVM service CPU cascade due to GC storm
**Applicable services:** All JVM-based services (especially long-connection services)

### Failure Mode

Old Gen keeps growing without being collected, eventually triggering a Full GC storm → CPU 100% STW → OOM Kill.

### Reference Check Method

```promql
# Old Gen usage ratio
jvm_memory_used_bytes{area="heap", id=~".*Old.*"}
  / jvm_memory_max_bytes{area="heap", id=~".*Old.*"}

# Old Gen 24h growth rate (bytes/hour)
(jvm_memory_used_bytes{area="heap", id=~".*Old.*"}
  - jvm_memory_used_bytes{area="heap", id=~".*Old.*"} offset 24h) / 24

# Major GC pause rate (should be near 0 normally)
rate(jvm_gc_pause_seconds_sum{action=~".*major.*|.*old.*"}[1h])
```

### Reference Thresholds

| Parameter | Value | Source |
|------|-----|------|
| Old Gen usage alert | > 85% | Historical: Full GC triggered ~2h after crossing 85% |
| Growth rate abnormal | > 200MB/24h | Normal should be near 0 (steady state) |
| GC pause rate abnormal | > 0.1 s/s | Normal is 0 |

---

## PB-003 -- Disk Space Prediction

**Problem domain:** Shift-left fault detection
**Source incident:** Common operational experience

### Reference Check Method

```promql
# Predict available space 24h from now (< 0 means will be full)
predict_linear(node_filesystem_avail_bytes{mountpoint="/", fstype!="tmpfs"}[24h], 86400)

# Current usage ratio
1 - (node_filesystem_avail_bytes{mountpoint="/", fstype!="tmpfs"}
  / node_filesystem_size_bytes{mountpoint="/", fstype!="tmpfs"})
```

---

## PB-004 -- Certificate Expiration Check

**Problem domain:** Expiration and decay
**Source incident:** Multiple certificate expiration alerts

### Reference Check Method

```promql
# Certificate remaining days
(probe_ssl_earliest_cert_expiry - time()) / 86400
```

### Reference Thresholds

| Parameter | Value |
|------|-----|
| < 7 days | critical |
| < 30 days | warning |
| < 60 days | info |

---

## PB-005 -- Kafka Consumer Lag Trend

**Problem domain:** Shift-left fault detection
**Source incident:** Kafka lag >60000 observed as cascade symptom

### Reference Check Method

```promql
# Consumer group lag
kafka_consumergroup_lag{job=~".*kafka.*"}

# Lag 1h growth
kafka_consumergroup_lag - kafka_consumergroup_lag offset 1h
```

---

## PB-006 -- Unresolved Alert Aging

**Problem domain:** Expiration and decay
**Source incident:** Operational experience -- acknowledged alerts left unresolved may mask worsening issues

### Reference Check Method

```
PagerDuty API: GET /incidents?statuses[]=triggered&statuses[]=acknowledged
```

### Reference Thresholds

| Parameter | Value |
|------|-----|
| triggered > 4h | critical |
| acknowledged > 24h | warning |

---

## PB-007 -- Node-Level Resource Saturation

**Problem domain:** Shift-left fault detection
**Source incident:** Node memory at 82.6% normal state triggered OOM under GC pressure

### Reference Check Method

```promql
# Memory usage ratio
1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)

# CPU usage ratio
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# TCP connection count
node_netstat_Tcp_CurrEstab

# Memory usage 24h prediction
predict_linear((1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)[24h:5m], 86400)
```

### Reference Thresholds

| Parameter | Value | Source |
|------|-----|------|
| Memory > 80% | warning | Historical: OOM at 82.6% under GC pressure |
| Memory > 90% | critical | |
| CPU predicted > 80% in 24h | warning | |

---

> **How to add new entries:**
>
> 1. After an incident retrospective, identify "if patrol had checked X in advance, it could have been caught earlier"
> 2. Distill the failure mode, reference check method, and thresholds
> 3. Thresholds must come from real data with source annotated
> 4. Annotate the corresponding problem domain
> 5. New entry numbering is incremental: PB-008, PB-009, ...
