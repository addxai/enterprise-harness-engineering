# Shared Capability: Notifications (Webhook)

All modes (oncall, patrol, and future new modes) use this capability when sending notifications.

## Script Location

`scripts/feishu_notify.py` (relative to the skill base directory `~/.claude/skills/sre-agent/`)

When calling, concatenate the skill base directory to get the full path. The relative path `scripts/feishu_notify.py` only works when the working directory happens to be the skill base directory; in oncall/patrol and other modes, the working directory is typically different, which would cause FileNotFoundError.

## Environment Variables

| Environment Variable | Description |
|---------|------|
| `ONCALL_FEISHU_WEBHOOK_URL` | Webhook URL for notifications |
| `ONCALL_FEISHU_WEBHOOK_SECRET` | Webhook signing secret |

## CLI Usage

The script supports two CLI invocation methods:

### 1. Mixed-Element Card (recommended, supports table + markdown)

First write elements to a JSON file, then send via the `send-elements` subcommand. Suitable for patrol reports and other table-containing scenarios.

```bash
# 1. Use the Write tool to create elements JSON file (containing markdown + table + hr elements)
# 2. Call send-elements to send
python3 scripts/feishu_notify.py send-elements \
  --title "SRE Patrol 2026-03-19 | at-risk" \
  --color red \
  --elements-file .scripts/Lead/patrol_elements.json
```

`--no-wide-screen` disables wide-screen mode (enabled by default).

Elements JSON file format example:

```json
[
  {"tag": "markdown", "content": "**P0 -- Action Required (2)**"},
  {
    "tag": "table", "page_size": 10, "row_height": "high",
    "header_style": {"text_align": "left", "text_size": "normal", "background_style": "grey", "text_color": "default", "bold": true, "lines": 1},
    "columns": [
      {"name": "eta", "display_name": "ETA", "data_type": "text", "width": "80px"},
      {"name": "finding", "display_name": "Finding", "data_type": "text", "width": "295px"},
      {"name": "action", "display_name": "Action", "data_type": "text", "width": "200px"}
    ],
    "rows": [
      {"eta": "Ongoing", "finding": "[fault-shift][prod][kubectl] Thanos OOMKilled 15x", "action": "Increase memory to 8-10Gi"}
    ]
  },
  {"tag": "hr"},
  {"tag": "markdown", "content": "**Patrol Scope**\n- prod cluster"}
]
```

### 2. Markdown Card (oncall diagnosis reports, etc.)

Pass `--title` + `--content` directly, no subcommand needed:

```bash
python3 scripts/feishu_notify.py \
  --title "[Diagnosis] #443137 High Error Rate" \
  --content "**Root Cause:** Error rate exceeded threshold\n**Action:** Contact team to confirm" \
  --color red \
  --button-text "View Details" \
  --button-url "https://your-org.pagerduty.com/incidents/443137"
```

You can also explicitly use the `send-markdown` subcommand; the effect is identical:

```bash
python3 scripts/feishu_notify.py send-markdown \
  --title "Card Title" \
  --content "**Markdown** content" \
  --color red
```

## Python Usage

When calling from Python code (e.g., oncall Triage scripts), import directly:

```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/sre-agent"))
from scripts.feishu_notify import send_card, send_multi_section_card, send_elements_card, make_table

webhook_url = os.environ["ONCALL_FEISHU_WEBHOOK_URL"]
secret = os.environ["ONCALL_FEISHU_WEBHOOK_SECRET"]

# Simple markdown card
send_card(webhook_url, secret, title="...", content="...", color="red")

# Multi-section markdown card
send_multi_section_card(webhook_url, secret, title="...", color="red",
    sections=[{"content": "**Section 1**..."}, {"content": "**Section 2**..."}])

# Mixed-element card (table + markdown)
elements = [
    {"tag": "markdown", "content": "**P0**"},
    make_table(columns=[...], rows=[...], row_height="high", page_size=10),
]
send_elements_card(webhook_url, secret, title="...", elements=elements, color="red")
```

## Table Component Specification

### make_table Parameters

| Parameter | Type | Description |
|------|------|------|
| columns | list[dict] | Column definitions, see below |
| rows | list[dict] | Row data, keys correspond to column names |
| row_height | str | `"low"` or `"high"` (only these two values are valid) |
| page_size | int | Rows per page, default 20 |

### Column Definition Format

```python
{"name": "col_key", "display_name": "Display Name", "data_type": "text", "width": "295px"}
```

### Column Width Constraints

| Format | Valid | Description |
|------|------|------|
| `"auto"` | Valid | Automatic width |
| `"NNpx"` (>=80) | Valid | Pixel width, minimum 80px |
| `"NNpx"` (<80) | Invalid | Below minimum, causes error |
| `"weighted"` | Invalid | Not supported in webhook cards |
| `"compact"` / `"fill"` | Invalid | Not supported in webhook cards |
| Integer / Object | Invalid | Format error |

**Important: All columns within the same table must use a consistent width format** (all auto or all px); mixing is not allowed.

### Patrol Report Standard Column Widths

| Table | Column | Width |
|------|-----|------|
| P0/P1 (with ETA) | ETA | 80px |
| P0/P1 (with ETA) | Finding | 295px |
| P0/P1 (with ETA) | Action | 200px |
| P2/P3/P4 (no ETA) | Finding | 375px |
| P2/P3/P4 (no ETA) | Action | 200px |

## Card Color Rules

| Scenario | Color | Description |
|------|------|------|
| High urgency alert diagnosis | `red` | oncall mode |
| Low urgency alert diagnosis | `yellow` | oncall mode |
| Matched known issue | `blue` | oncall mode |
| Patrol at-risk | `red` | patrol mode |
| Patrol degraded | `yellow` | patrol mode |
| Patrol good | `green` | patrol mode |
| General information | `grey` | any mode |

## Important Notes

- Webhook card markdown **does not support standard markdown table syntax**; tables must use the native table component
- `row_height` only supports `"low"` and `"high"`; `"medium"` and other values are not supported
- **Do not include full logs in notifications** — only summarize key information
- **Do not expose sensitive information** (passwords, tokens, connection strings)
- In CLI mode, literal `\n` is automatically converted to real newlines by the script
