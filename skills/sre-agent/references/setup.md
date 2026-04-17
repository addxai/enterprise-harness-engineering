# sre-agent Installation and Configuration

## Required Environment Variables

The following environment variables must be configured before running sre-agent; otherwise, the corresponding features will be unavailable. Scripts will report errors and exit when environment variables are missing — refer to this document to complete the configuration.

### PagerDuty (required for oncall / diagnosis / patrol modes)

| Environment Variable | Description | How to Obtain |
|---------|------|---------|
| `PAGERDUTY_API_TOKEN` | PagerDuty API v2 Access Key | PagerDuty -> Integrations -> API Access Keys -> Create New API Key |

Verify:
```bash
python3 scripts/pagerduty_api.py list-services
```

### Notification Webhook (required for oncall / patrol notification features)

| Environment Variable | Description | How to Obtain |
|---------|------|---------|
| `ONCALL_FEISHU_WEBHOOK_URL` | Webhook URL for notifications | Configure in your messaging platform (Feishu/Slack/Teams) |
| `ONCALL_FEISHU_WEBHOOK_SECRET` | Webhook signing secret | Configure in your messaging platform |

Verify:
```bash
python3 scripts/feishu_notify.py --title "Test" --content "setup verification" --color grey
```

## Required Tools

### Python 3 (required)

sre-agent's scripts (pagerduty_api.py, feishu_notify.py) all require Python 3, with no additional pip dependencies (standard library only).

| Platform | Installation |
|------|---------|
| macOS | `brew install python3` or use system-provided |
| Windows | `winget install Python.Python.3` |
| Linux | `apt install python3` / `yum install python3` |

### kubectl (used in diagnosis / patrol modes)

| Platform | Installation |
|------|---------|
| macOS | `brew install kubectl` |
| Windows | `winget install Kubernetes.kubectl` |
| Linux | See kubernetes.io official documentation |

Requires kubeconfig configured with access to target clusters (see the K8s Context list in `infra-context.md`).

### Cloud CLI (as needed)

Diagnosis/patrol may need to query cloud resources. Install the corresponding CLI for your cloud platform:
- AWS: `aws-cli`
- GCP: `gcloud`
- Azure: `az`

## Common Error Troubleshooting

| Error Message | Cause | Solution |
|---------|------|---------|
| `PAGERDUTY_API_TOKEN not set` | PagerDuty environment variable not configured | Set environment variable; see "PagerDuty" section above |
| `ONCALL_FEISHU_WEBHOOK_URL and ... must be set` | Notification environment variables not configured | Set environment variables; see "Notification Webhook" section above |
| `FileNotFoundError: scripts/pagerduty_api.py` | Working directory is not the skill base directory | Call the script using the absolute path of the skill base directory |
| `command not found: kubectl` | kubectl not installed | See "kubectl" installation above |
| `error: context "xxx" does not exist` | Target cluster context missing from kubeconfig | Configure the corresponding K8s context as described in `infra-context.md` |
