---
name: grafana
description: Query and manage Grafana dashboards, alert rules, and data sources via HTTP API. Use when viewing dashboards, troubleshooting alerts, checking service metrics, finding data sources, or when Grafana, monitoring, alerts, dashboards, or observability is mentioned.
---

# Grafana

Query and manage Grafana monitoring dashboards, alert rules, and data sources via HTTP API.

## Setup

Configure your Grafana instance:

| Variable | Description | Required |
|----------|-------------|----------|
| `GRAFANA_URL` | Your Grafana server URL (e.g., `https://grafana.example.com`) | Yes |
| `GRAFANA_TOKEN` | API Key (Settings → API Keys, viewer or editor role) | Yes |

Authentication: `curl -s -H "Authorization: Bearer $GRAFANA_TOKEN" "$GRAFANA_URL/api/..."`

Customize the following for your organization:
- **Folder structure**: How dashboards are organized (by team, region, service, etc.)
- **Tag conventions**: What tags are used for filtering (region, environment, service type)
- **Alert naming**: Your alert naming pattern (e.g., `{Service} {Metric} {Condition} [{env}]`)
- **Key dashboards**: Which dashboards to check after deployments

## Rules

### Dashboard Operations

- **Search first, then detail**: Use search API with tags/query to narrow scope, then fetch by uid
- **Never delete production dashboards** — archive by moving to an Archive folder
- **Write operations require user confirmation** before execution (create/modify dashboards, alert rules)

### Common Workflows

**Find a Dashboard:**
```bash
curl -s -H "Authorization: Bearer $GRAFANA_TOKEN" \
  "$GRAFANA_URL/api/search?query=<keyword>&tag=<tag>&type=dash-db" \
  | jq '.[] | {uid, title, folderTitle}'
```

**Get Dashboard Details:**
```bash
curl -s -H "Authorization: Bearer $GRAFANA_TOKEN" \
  "$GRAFANA_URL/api/dashboards/uid/<uid>" \
  | jq '.dashboard.panels[] | {title, type}'
```

**Check Active Alerts:**
```bash
curl -s -H "Authorization: Bearer $GRAFANA_TOKEN" \
  "$GRAFANA_URL/api/alerts?state=alerting"
```

**List Data Sources:**
```bash
curl -s -H "Authorization: Bearer $GRAFANA_TOKEN" \
  "$GRAFANA_URL/api/datasources" \
  | jq '.[] | {id, name, type, url}'
```

**Search by Folder:**
```bash
curl -s -H "Authorization: Bearer $GRAFANA_TOKEN" \
  "$GRAFANA_URL/api/search?folderIds=<folder_id>&type=dash-db"
```

### Post-Deployment Checks

After each deployment, check key dashboards for:
- Error rate changes (before vs after deployment)
- Latency P95/P99 trends
- Consumer lag (if using message queues)
- Connection counts (TCP/WebSocket)
- Log level distribution (error/warn spikes)

### Alert Troubleshooting

1. `GET /api/alerts?state=alerting` — list all firing alerts
2. Identify the dashboard and panel from the alert
3. Read the PromQL expression from the panel
4. Query Prometheus directly to understand the data
5. Check recent deployments or config changes as potential cause

## Examples

### Bad

```bash
# Delete a production dashboard (never delete, archive instead)
curl -X DELETE "$GRAFANA_URL/api/dashboards/uid/abc123"

# Fetch all dashboards without filtering (use search first)
for uid in $(curl ... /api/search | jq -r '.[].uid'); do
  curl ... /api/dashboards/uid/$uid
done
```

### Good

```bash
# Search dashboards by tag
curl -s -H "Authorization: Bearer $GRAFANA_TOKEN" \
  "$GRAFANA_URL/api/search?tag=production&type=dash-db" \
  | jq '.[] | {uid, title, folderTitle}'

# Check active alerts
curl -s -H "Authorization: Bearer $GRAFANA_TOKEN" \
  "$GRAFANA_URL/api/alerts?state=alerting"

# Get alert details for troubleshooting
curl -s -H "Authorization: Bearer $GRAFANA_TOKEN" \
  "$GRAFANA_URL/api/alerts/<alert_id>"
```
