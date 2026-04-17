---
name: security-compliance-review
description: Perform a structured security and compliance review using evidence from code/config/docs. Use for MR/PR review, architecture review, and periodic full scans. Detects secrets exposure, PII leakage, access control gaps, and compliance violations.
---

# Security & Compliance Review

A comprehensive security and compliance review framework. Based on input materials and baseline policies, intelligently determines the risk surface and provides actionable remediation recommendations.

For detailed rules and examples, see [references/REFERENCE.md](references/REFERENCE.md).

## Execution Flow

### Step 0: Pre-Gate — System Type Determination (Blocking)

- Must first determine the system type: `Consumer-facing` / `Internal product` / `Mixed`
- If unable to determine: output a "clarification question" first (blocking conclusion); do not proceed to subsequent checks until the answer is received

### Step 1: Relevance Assessment

1. **Define scope first**: Prioritize MR/diff/specified directory; fall back to scanning the repository
2. **Find evidence next**: Code/configuration/CI/Helm/dependencies
3. **Then draw conclusions**: `Relevant` / `Not Relevant (N/A)` / `Unknown`
4. `Unknown` triggers clarification/blocking only for "must-clarify items"

### Step 2: Risk Map Check

Must output a table: `Risk Category | Relevance | Trigger Clues | Handling | Evidence/Recommendations`

Required risk categories to cover:
- `R0 System Type`
- `R4 Bulk Capability/Export`
- `R5 Observation Leakage (Logs/Tracking/Error Reporting)`
- `R6 Secrets/Credentials`
- `R7 Third-Party Boundary`
- `R11 Zero Human Access to High-Sensitivity Data (Video/Address/Phone)`
- `R12 Retention & Deletion/DSAR`
- `R14 Agent Skills Supply Chain`
- `R15 Location Permissions`

### Step 3: Categorized Handling by Rules

#### Company Standard Items (enforced by default, no clarification needed)

If evidence is insufficient: handling = `Default standard + recommendation`, with the gap marked as "evidence needed (not clarification)":

- Unified Observability SDK + masking/export restrictions/audit (R5)
- Secrets/credentials: Secret Zero, no plaintext/hard-coded, rotation and audit (R6)
- CI/Helm/IaC must use Vault injection and controlled references
- Ops/support access boundary: restricted platform, default masking, default no-export, ticket-bound, full audit

#### Agent Skills Supply Chain (R14, triggered when Skills files detected)

If the MR/repository contains `SKILL.md`, `.cursor/skills/`, `.cursor/rules/`, `AGENTS.md`:
- Check for prompt injection patterns (`ignore previous instructions`, `bypass safety`, etc.)
- Check for hard-coded credentials (API Keys, Tokens, connection strings)
- Check for executable scripts (`scripts/` directory; risk is 2.12x that of instruction-only Skills)
- Check for hidden HTML comments (`<!-- -->`, invisible to humans but readable by LLMs)
- Check for internal information leakage (internal domains, IP addresses)
- If none of the above files exist: mark `Not Relevant (N/A)`

#### Must-Clarify Items (blocking when missing)

- System type
- Whether new/relaxed export/bulk capability is added (export/download/csv/xlsx/report/bulk/batch clues)
- Third-party boundary (new/modified third-party SDK/Webhook/external API, visible field mappings)
- Encryption and key management (involving PIN/password/OTP/token/key/Private Key, etc.)
- New PII fields and masking approach (beyond user_id/SN/email)

#### Location Permissions (R15, company-level privacy red line)

**Absolutely prohibited** to request user geolocation permissions on any platform, including but not limited to:
- Android: `ACCESS_FINE_LOCATION`, `ACCESS_COARSE_LOCATION`, `ACCESS_BACKGROUND_LOCATION`
- iOS: `NSLocationWhenInUseUsageDescription`, `NSLocationAlwaysUsageDescription`
- Web: `navigator.geolocation`, Permissions API `geolocation`
- Flutter: `geolocator`, `location` and other location plugins

City/region information may **only** be obtained through user's active selection. The selection result must be persisted and not re-asked.

#### Red Lines (finding triggers failure)

- Employee (including ops/support) can directly access/export raw video: immediate `Remediation Required / Fail`
- Plaintext storage/transmission/logging of passwords, tokens, keys, or other credential elements: high-risk blocking
- Human-viewable entry points for high-sensitivity data (address/phone): immediate `Remediation Required / Fail`
- Requesting any form of geolocation permission: immediate `Remediation Required / Fail` (R15)

## Output Structure

Must strictly follow this Markdown structure:

### 2.0 Scope & Gates

```markdown
- **scope**: Modules/directories/PR scope covered by this review
- **System type and adopted strategy**: Consumer-facing / Internal product / Mixed
- **Blocking items (if any)**: List blocking items (reference R#/G#/E#)
- **Clarification questions and unknowns**: Cover only the must-clarify checklist
```

### 2.1 Summary

```markdown
- **Conclusion**: Pass / Conditional Pass / Fail
- **Risk level**: Low / Medium / High
- **Risk item summary**: Reference R#
- **Key evidence index**: List E# only
```

### 2.2 Risk Map

| Risk ID | Risk Category | Relevance | Trigger Clues | Handling | Evidence/Recommendations |
|--------|----------|--------|----------|----------|-----------|
| R0 | System Type | Relevant/N/A/Unknown | Clues | Clarify/Default standard+recommendation/Block | E#/Recommendations |

### 2.3 Gap List

| Gap ID | Gap Description | Risk Level | Related Risk Item | Evidence Reference | Recommended Remediation |
|--------|----------|----------|------------|----------|----------|
| G1 | Description | High/Medium/Low | R# | E# | A# |

### 2.4 Recommendations & Checklist (Actions)

| Priority | Action ID | Recommendation | Related Gap | Evidence Reference |
|--------|-----------|----------|----------|----------|
| Fix Now | A1 | Specific recommendation | G# | E# |

### 2.5 Evidence Appendix

| Evidence ID | Evidence Type | Reference | Excerpt |
|-------------|----------|------|------|
| E1 | Doc/Code/Config | [path:Lx-Ly](path) | Excerpt |

## Examples

### Bad - Hard-coded Secret

```python
API_KEY = "sk-<account-id>abcdef"  # Violates R6
```

### Good - Using Vault

```python
API_KEY = vault.read('myapp/api-key')
```

For more examples, see [references/REFERENCE.md](references/REFERENCE.md#complete-examples).

## Exemptions

| Scenario | Condition |
|------|------|
| Local dev environment | Configuration used only for local testing (must not be committed to repository) |
| Legacy system migration | Legacy system undergoing compliance remediation (migration plan must be provided) |

Exemption method: `/override skill=security-compliance-review reason="..." evidence="..."`

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Detailed Reference Document](references/REFERENCE.md)
