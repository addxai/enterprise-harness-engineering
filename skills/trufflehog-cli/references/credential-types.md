# Common Credential Types Quick Reference

For rapid initial identification when no `DetectorName` is available.

TruffleHog has 1,000+ built-in detectors (`DetectorName`) covering Git platforms, cloud services, SaaS, databases, payment systems, monitoring, and other mainstream services. Full list:
[proto/detectors.proto (v3.94.0)](https://github.com/trufflesecurity/trufflehog/blob/v3.94.0/proto/detectors.proto)

| Pattern | Possible Type | DetectorName | Read-Only Verification Suggestion |
|---|---|---|---|
| `glpat-` | GitLab PAT | `GitlabV2` | `GET /api/v4/personal_access_tokens/self` |
| `ghp_`, `gho_`, `ghs_`, `github_pat_` | GitHub Token | `GitHub` | `GET https://api.github.com/user` |
| `AKIA` + 20 chars | AWS Access Key ID | `AWS` | `aws sts get-caller-identity` |
| `ASIA` + 20 chars | AWS STS Temporary Key ID | `AWSSessionKey` | `aws sts get-caller-identity` |
| `xoxb-`, `xoxp-`, `xoxa-` | Slack Token | `Slack` | `POST https://slack.com/api/auth.test` |
| `sk-` | OpenAI API Key | `OpenAI` | `GET /v1/models` |
| `sk-ant-` | Anthropic API Key | `Anthropic` | Use the platform's minimal read-only probe |
| `sk_live_`, `rk_live_` | Stripe Key | `Stripe` | `GET /v1/balance` |
| `SG.` | SendGrid API Key | `SendGrid` | `GET /v3/scopes` |
| `-----BEGIN ... PRIVATE KEY-----` | Private Key Material | `PrivateKey` | Do not perform "usage-based verification"; treat as high-risk |

## Rules

- When scan metadata is available, use it first
- When unsure, do not blindly probe across platforms
- Use "minimal read-only probes" to determine whether a credential is active
- Credentials must not be persisted to disk or written to shell history
