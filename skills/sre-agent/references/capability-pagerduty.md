# Shared Capability: PagerDuty API

All modes (oncall, diagnosis, patrol) use this capability when querying or operating PagerDuty.

## Script

**Prefer using `scripts/pagerduty_api.py`** (relative to the skill base directory `~/.claude/skills/sre-agent/`); avoid hand-writing inline curl/python code.

When calling, concatenate the skill base directory to get the full path. The relative path `scripts/pagerduty_api.py` only works when the working directory happens to be the skill base directory; in oncall/patrol and other modes, the working directory is typically different, which would cause FileNotFoundError.

### CLI Usage

```bash
# Query alerts
python3 scripts/pagerduty_api.py list-incidents --status triggered --urgency high --my-teams
python3 scripts/pagerduty_api.py list-incidents --status triggered --status acknowledged --since 2026-03-15T21:00:00Z --until 2026-03-16T08:00:00Z --sort created_at:asc --limit 100
python3 scripts/pagerduty_api.py list-incidents --status triggered --status acknowledged --all-pages  # Auto-paginate

# Incident details / Alerts / Logs
python3 scripts/pagerduty_api.py get-incident <INCIDENT_ID>
python3 scripts/pagerduty_api.py get-alerts <INCIDENT_ID>
python3 scripts/pagerduty_api.py get-log-entries <INCIDENT_ID>

# Service list
python3 scripts/pagerduty_api.py list-services
python3 scripts/pagerduty_api.py list-services --query payment

# oncall single-round pull (stateless; deduplication is handled by Triage)
python3 scripts/pagerduty_api.py oncall-poll
python3 scripts/pagerduty_api.py oncall-poll --since 2026-03-20T07:00:00Z  # Only pull alerts after specified time
python3 scripts/pagerduty_api.py oncall-poll --json  # JSON output

# All commands support --json for raw JSON output
python3 scripts/pagerduty_api.py list-incidents --status triggered --json
```

### Python Usage

```python
import sys; sys.path.insert(0, "scripts")
from pagerduty_api import list_incidents, get_incident, oncall_poll, _get_token

token = _get_token()
data = list_incidents(token, statuses=["triggered"], urgencies=["high"], my_teams=True)
result = oncall_poll(token)  # oncall single-round (stateless; deduplication handled by Triage)
```

### Change Operations (acknowledge / resolve / note)

Change operations require Python calls (CLI does not expose change commands to prevent accidental operations):

```python
from pagerduty_api import acknowledge_incidents, resolve_incidents, add_note, _get_token
token = _get_token()
acknowledge_incidents(token, ["INCIDENT_ID"], from_email="user@example.com")
resolve_incidents(token, ["INCIDENT_ID"], from_email="user@example.com")
add_note(token, "INCIDENT_ID", "Diagnosis result...", from_email="user@example.com")
```

## Environment Information

| Item | Value |
|------|-----|
| Base URL | `https://api.pagerduty.com` |
| Web URL | `https://<your-org>.pagerduty.com` (set `PAGERDUTY_WEB_URL` env var) |
| API Version | v2 |
| Authentication | `Authorization: Token token=$PAGERDUTY_API_TOKEN` |
| Content-Type | `application/json` |
| Accept | `application/vnd.pagerduty+json;version=2` |
| Rate Limit | 960 requests/min per API key |

### Authentication

| Environment Variable | Description |
|---------|------|
| `PAGERDUTY_API_TOKEN` | PagerDuty API v2 Access Key |

All requests must include the following headers:

```bash
-H "Authorization: Token token=$PAGERDUTY_API_TOKEN" \
-H "Accept: application/vnd.pagerduty+json;version=2" \
-H "Content-Type: application/json"
```

## Known Resources

Configure your PagerDuty services and teams here:

### Services

| Service | ID | Description |
|---------|-----|------|
| *(your-service-1)* | `<SERVICE_ID>` | Description |
| *(your-service-2)* | `<SERVICE_ID>` | Description |

### Teams

| Team | ID |
|------|-----|
| *(your-team)* | `<TEAM_ID>` |

## Incident Status Model

```
triggered → acknowledged → resolved
    │                          ↑
    └──────────────────────────┘
```

## Security Rules

1. **All change operations (acknowledge / resolve) must display Incident details first; execute only after user confirmation**
2. **Batch resolve must list each Incident title and ID individually; execute after confirmation**
3. **Notes must not contain sensitive information (passwords, Tokens, etc.)**
4. **Observe rate limits (960/min); control concurrency for batch queries**

## Typical Usage Per Mode

| Mode | Typical Operations |
|------|---------|
| **oncall** | Pull triggered alerts, query alert time windows for correlation |
| **diagnosis** | Query alerts within +/-30min window for correlation analysis, get incident details and alerts |
| **patrol** | Query triggered+acknowledged open alerts, check for aging alerts |
| **Direct use** | User says "check current alerts", "ack 443111", "resolve these alerts" |

## Exemptions

| Scenario | Condition |
|------|------|
| Emergency incident recovery | User explicitly states an emergency; confirmation steps may be skipped |
| Low-priority alert bulk cleanup | User explicitly requests batch resolve of urgency=low alerts |
