---
name: sentry-onboarding
description: Create and configure Sentry projects across staging/production environments via REST API. Use when user needs to onboard a new service to Sentry, create Sentry projects, or set up error monitoring for a new application.
---

# Sentry Onboarding

Create and configure Sentry projects across multiple environments via REST API.

## Setup

Before using this skill, configure your Sentry instances:

```
# Add your Sentry instances here
SENTRY_INSTANCES:
  - name: staging
    url: https://sentry-staging.example.com
    token_env: SENTRY_STAGING_TOKEN
    org: your-org
  - name: prod
    url: https://sentry.example.com
    token_env: SENTRY_PROD_TOKEN
    org: your-org
```

## Workflow

### Step 1: Collect Information

Ask the user for:
1. **Service name** (e.g., `payment-service`)
2. **Platform** — must be framework-level, not language-level:
   - Java → `java-spring-boot`
   - Python → `python-django` / `python-fastapi`
   - JavaScript → `javascript-nextjs` / `javascript-react`
   - Go → `go`
   - Android → `android`
   - iOS → `apple-ios`
3. **Team** — which team should own this project
4. **Environments** — which instances to create in (staging, prod, or both)

### Step 2: Verify Token

```bash
curl -s -H "Authorization: Bearer $TOKEN" "$SENTRY_URL/api/0/organizations/$ORG/teams/" | jq '.[].slug'
```

If 401 → token expired, guide user to regenerate.

### Step 3: List Available Teams

```bash
curl -s -H "Authorization: Bearer $TOKEN" "$SENTRY_URL/api/0/organizations/$ORG/teams/" | jq '.[] | {slug, name}'
```

### Step 4: Create Project

```bash
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "<service-name>", "platform": "<platform>"}' \
  "$SENTRY_URL/api/0/teams/$ORG/<team-slug>/projects/"
```

### Step 5: Extract DSN

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "$SENTRY_URL/api/0/projects/$ORG/<project-slug>/keys/" | jq '.[0].dsn.public'
```

### Step 6: Generate SDK Snippet

Based on platform, generate the SDK initialization code with the DSN.

## Rules

- Production operations require explicit user confirmation
- Create staging first, verify, then create prod
- Platform must be framework-level (e.g., `java-spring-boot` not `java`)
- Project slug is auto-generated from name
