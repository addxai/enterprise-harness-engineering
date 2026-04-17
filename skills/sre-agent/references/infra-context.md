# Infrastructure Context

Environment mapping information required by sre-agent at runtime. This file is maintained by the ops team and must be kept in sync with the actual environment.

## Setup

Before using sre-agent, populate this file with your actual infrastructure details. Replace all placeholder entries below with your real endpoints, accounts, and clusters.

## 1. Prometheus / Thanos / VictoriaMetrics Endpoints

| Account/Project | Environment | Endpoint | Type |
|-----------------|-------------|----------|------|
| `your-account-1` | prod | `http://thanos-prod.internal:9090` | Thanos |
| `your-account-2` | eu-prod | `http://thanos-eu.internal:9090` | Thanos |
| `your-account-3` | data | `http://prometheus-data.internal:9090` | Prometheus |
| *(add your own)* | | | |

### Endpoint Selection Rules

Determine the environment from the `prometheus_group` or `job` prefix in alert labels:
- `prod-*` -> your production Thanos/Prometheus endpoint
- `eu-prod-*` -> your EU production Thanos/Prometheus endpoint
- `staging-*` -> your staging endpoint

> Configure the mapping between job label prefixes and Prometheus endpoints for your environment.

### Reverse-Lookup Metrics by IP/Label Value

When you need to find which metrics are associated with a given IP address (or any label value), follow these steps:

**Step 1: Locate the Prometheus instance and label name for the IP**

`label/__name__/values?match[]=` is **unreliable** on Thanos for federated data (Store Gateway limitation). The correct approach is to search the `up` metric by iterating all label values:

```bash
# Search for labels containing the target IP in the up metric (iterate all endpoints)
curl -s "$PROMETHEUS_URL/api/v1/query?query=up" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for r in data['data']['result']:
    for k, v in r['metric'].items():
        if 'TARGET_IP' in v:
            print(json.dumps(r['metric'], indent=2))
"
```

> The IP is usually in the `instance` label (format `IP:Port`), but may also be in `node`, `host`, `__address__`, or other labels.

**Step 2: Get all metric names for that IP**

Use the `series` API (**must be POST**); `label/__name__/values` is unreliable on Thanos:

```bash
START=$(date -v-1H +%s)  # macOS; on Linux use date -d '1 hour ago' +%s
END=$(date +%s)
curl -s "$PROMETHEUS_URL/api/v1/series" \
  --data-urlencode 'match[]={instance="TARGET_IP:PORT"}' \
  --data-urlencode "start=$START" --data-urlencode "end=$END" \
  | jq '[.data[].__name__] | unique'
```

**Key points**:
- Must iterate all Prometheus/Thanos endpoints listed above
- A single IP may have multiple ports (e.g., `:9100` Node Exporter, `:18002` JVM); query each separately
- The Thanos `targets` API response can be very large (hundreds of MB); avoid downloading and parsing in full

## 2. Cloud Accounts

### Cloud Accounts Table

| Provider | Account/Project ID | Environment | Region | VPC CIDR | CLI Profile |
|----------|-------------------|-------------|--------|----------|-------------|
| AWS | `your-account-id` | prod | <your-region> | `10.x.x.x/16` | `your-profile-name` |
| GCP | `your-project-id` | prod | <your-region> | `10.x.x.x/16` | *(use gcloud)* |
| Azure | `your-subscription` | prod | eastus | `10.x.x.x/16` | *(use az cli)* |
| *(add your own)* | | | | | |

### IP -> Environment Mapping

Configure your VPC CIDR to environment mapping here for quick IP-based lookups:
- `10.x.x.x` -> your-prod-environment (account-id)
- `10.y.y.y` -> your-staging-environment (account-id)

> Note: Some services may run in a different account's VPC than expected based on naming. Use IP ranges as the source of truth.

## 3. K8s Context

### Kubernetes Contexts

| Context | Provider | Account/Project | Environment |
|---------|----------|----------------|-------------|
| `your-eks-context` | AWS EKS | your-account-id | prod |
| `your-gke-context` | GCP GKE | your-project-id | prod |
| *(add your own)* | | | |

## 4. Available Diagnostic Skills

The following are currently available data source skills and their capabilities:

| Skill | Capability | Network Access | Typical Usage |
|-------|------|----------|----------|
| `/prometheus` | PromQL instant/range queries | Internal endpoints accessible | Metric trends, alert rule queries |
| `k8s-ops` | kubectl read-only operations | Cluster internal network | Pod/Node status, logs |
| `ssh-host` | SSH remote commands | Internal/public IPs | Processes, system logs, dmesg |
| `/grafana` | Dashboard queries | Internal network | Metric visualization |
| `argocd` | Deployment history queries | Internal network | Recent deployments, sync status |
| `sentry` | Error tracking queries | Public network | Application errors, stack traces |
| `aws-cli` | AWS API read-only | Public network | EC2/RDS/MSK and other resource status |
| `gcp-cli` | GCP gcloud API read-only | Public network | GCE/GKE/Cloud SQL and other resource status |

> This is a list of known skills, not a limitation. If new tools or methods are discovered during diagnosis, they should be proactively used. Add your own diagnostic skills as needed.
