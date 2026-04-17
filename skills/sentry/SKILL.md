---
name: sentry
description: Query Sentry errors, triage issues, and check release health via REST API. Use when debugging exceptions, investigating crash reports, triaging error issues, checking release stability, or any error monitoring and issue tracking task. Also triggers on mentions of Sentry, errors, exceptions, crashes, stack traces, or error rates.
---

# sentry

Query errors, investigate exceptions, track issues, and monitor release health via the Sentry REST API. API usage is referenced through Context7 MCP; only company-specific rules are documented here.

## Description

Applicable scenarios: production error investigation, issue triage, release health checks, crash analysis.

- **Internal URL**: `https://sentry-us.example.com` (self-hosted Sentry, API base path `/api/0/`)
- **Organization slug**: `sentry`

| Variable | Description | Required |
|------|------|------|
| `SENTRY_AUTH_TOKEN` | Organization Token (Settings -> Organization Tokens -> Create) | Yes |

Authentication: `-H "Authorization: Bearer $SENTRY_AUTH_TOKEN"`

> The current Organization Token only has Release-related permissions by default. To query Issues/Events, create an Internal Integration in Developer Settings and enable `Issue & Event: Read`, `Project: Read`, `Organization: Read`.

## Rules

### Project Structure (7 projects)

| Project slug | Product | Platform | Description |
|-----------|------|------|------|
| `app-android` | Main App | Android | Primary consumer app (most frequent releases) |
| `app-ios` | Main App | iOS | Primary consumer app |
| `backend-service` | Backend | Java | Backend service (shares releases with consumer-service) |
| `consumer-service` | Backend | Java | Backend consumer service |
| `app2-android` | Sub-brand App | Android | Sub-brand app |
| `app2-ios` | Sub-brand App | iOS | Sub-brand app |
| `app3-ios` | Security App | iOS | Security app |

### Release Version Naming Convention

**Three formats**, distinguished by platform:

| Platform | Format | Example |
|------|------|------|
| **Android** | `{major}.{minor}.{patch}({commit_hash})` | `2.85.0(b4f16c)` |
| **iOS** | `{bundle_id}@{version}+{build_number}` | `com.example.app@3.91.0+30713` |
| **Backend** | `{YYYYMMDD}@{COMMIT_HASH}` | `20260212@3A5AE26` |

**iOS Bundle ID Reference**:

| Bundle ID | Product |
|-----------|------|
| `com.example.app` | Main App |
| `com.example.guard` | Guard App |
| `com.example.app2` | Sub-brand App |
| `com.example.app3` | Security App |

### Release Frequency

- **app-android**: Multiple builds per day (CI auto-reports)
- **app-ios**: Several times per week
- **backend-service / consumer-service**: Approximately daily deployments, version numbers include date (`YYYYMMDD@HASH`), both projects share the same release
- **app2-***: Lower frequency

### Hard Rules

1. **Look before you act**: Write operations (resolve / ignore / assign) must be preceded by reviewing the stack trace and impact scope
2. **PII protection**: Error context may contain user data; never share raw stack traces externally or expose user information

### Common Workflows

1. **Investigate production errors**: Query unresolved issues for a project -> sort by time -> view latest event stack trace -> locate code line -> provide fix suggestions
2. **Post-deployment health check**: Query latest release -> check for new issues -> confirm Crash Free Rate -> continue monitoring for 30min
3. **Batch triage**: Filter by project + environment -> review stack traces one by one -> resolve / ignore / assign
4. **Release tracking**: `/api/0/organizations/sentry/releases/?per_page=20&sort=date` -> check latest releases

## Examples

### Bad

```
# Resolving without investigation
User: Help me handle the errors on Sentry
AI: I've resolved all unresolved issues for you.  <- Did not review stack traces and impact scope

# PII leakage
AI: The stack trace shows user email user@example.com triggered the exception...  <- Should not expose user information
```

### Good

```
# Post-deployment check
User: Backend just released a new version, check if there are new errors on Sentry
AI: Querying latest Release...
  1. Found 20260303@A1B2C3D, linked to backend-service and consumer-service
  2. Checking issues associated with this Release...
  3. No new issues found, recommend continuing to monitor for 30min

# Client crash investigation
User: app-android latest version 2.85.0 has user reports of crashes
AI: Querying app-android project Release 2.85.0 related issues...
  1. Found latest build 2.85.0(b4f16c)
  2. Viewing unresolved issues, sorted by affected user count
  3. Viewing top issue stack trace -> locating code
```
