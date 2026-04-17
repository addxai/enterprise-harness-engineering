# Credential Verification

For type identification and validity confirmation after a suspected credential has been found.

## Applicable Scenarios

- "Is this token still active?"
- "Did the old credential become invalid after rotation?"
- "What type of secret is this string?"

## Identification Order

From lowest to highest cost:

1. First, use `DetectorName` from existing scan results
2. Then use [credential-types.md](credential-types.md) for prefix/format identification
3. When human interaction is needed, use `trufflehog analyze`
4. Finally, perform a read-only API verification against the target platform

## TruffleHog Analyze

Only use when an interactive terminal session is available:

```bash
trufflehog analyze --no-update
trufflehog analyze github --no-update
```

Do not assume an AI shell can drive the interactive TUI.

## Scriptable Read-Only Verification

### GitHub PAT

```bash
export CHECK_TOKEN="<token>"
curl -s -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: Bearer $CHECK_TOKEN" \
  https://api.github.com/user
unset CHECK_TOKEN
```

### GitLab PAT

```bash
export CHECK_TOKEN="<token>"
curl -s -o /dev/null -w "%{http_code}\n" \
  -H "PRIVATE-TOKEN: $CHECK_TOKEN" \
  https://gitlab.example.com/api/v4/personal_access_tokens/self
unset CHECK_TOKEN
```

Only use this endpoint when the token has API scope.

### AWS Access Key

```bash
AWS_ACCESS_KEY_ID="<key_id>" AWS_SECRET_ACCESS_KEY="<secret>" \
  aws sts get-caller-identity
```

## Result Interpretation

- `2xx`: typically active
- `401`: typically revoked/inactive
- `403`: semantics vary by platform; usually requires further judgment
- Network error: `unknown`

Reports should only show masked prefix, status, evidence, and recommended action.
