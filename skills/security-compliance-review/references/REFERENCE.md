# Security & Compliance Review — Detailed Reference Document

> This document supplements SKILL.md with detailed content for human reading or on-demand AI loading.

## Table of Contents

- [Review Targets and Evidence Types](#review-targets-and-evidence-types)
- [System Type Determination](#system-type-determination)
- [Input Material Checklist](#input-material-checklist)
- [Risk Category Definitions](#risk-category-definitions)
- [Company Standard Items — Detailed](#company-standard-items--detailed)
- [Must-Clarify Items — Detailed](#must-clarify-items--detailed)
- [Red Line Rules — Detailed](#red-line-rules--detailed)
- [Sensitive Clue Triggered Blocking Clarification](#sensitive-clue-triggered-blocking-clarification)
- [Compliance Framework Auto-Inference](#compliance-framework-auto-inference)
- [Control Point Library](#control-point-library)
- [Complete Examples](#complete-examples)

---

## Review Targets and Evidence Types

The review target may be **documentation** or **code/configuration** (or both). For each key control point, "where the evidence comes from" must be explicit:

- **Code/configuration evidence**: Implementation, default configs, permission checks, encryption/masking/audit implementation points
- **Documentation evidence**: Policy/design/process (e.g., data classification criteria, access boundary, audit and retention, exception procedures, third-party boundary)

---

## System Type Determination

The change's system type must be determined first. **If it cannot be determined, a "clarification question" must be output first; do not proceed to subsequent checks and conclusions until an answer is received**:

| System Type | Description | Inspection Focus |
|----------|------|----------|
| **Consumer-facing** | Targets end users; external API/client directly reachable; third parties/channels reach users | External exposure surface, third-party boundaries, user-reachable capabilities, log/tracking leakage, credential and high-sensitivity data handling |
| **Internal product** | Targets employees/internal users; internal tools/admin/operations systems | Platform requirements (masking+audit), permission and export controls, production data bypass (direct DB/K8s/VPC, debug/exec, scripts) and audit evidence |
| **Mixed** | Contains both external user chains and internal operations/admin chains | Check independently against both strategies, then merge conclusions in the summary |

**If system type is unknown, clarification is mandatory (blocking conclusion)**:

- [ ] Who are the affected users of this change (end users/employees/both)?
- [ ] Does it add/modify external APIs, SDKs, client field display, or third-party visible fields?
- [ ] Does it add/modify internal admin capabilities (queries, exports, bulk operations, debugging, scripts)?

---

## Input Material Checklist

Extract from input first; auto-scan the repository to fill gaps if not provided:

| Check Item | Description | Status |
|--------|------|------|
| **Review target** | Document / Code / Configuration / Mixed | |
| **Evidence location** | Code file paths / Config items / Document links | |
| **System type** | Consumer-facing / Internal product / Mixed | |
| **Users/regions** | US only / Global / Other | |
| **Operators and entities** | US Entity / CN Entity / Other (state only when deviating from default assumption) | |
| **Data fields** | email / user id / SN / address+phone / video / log tracking / error events / other | |
| **Authentication and secrets** | PIN code / password / OTP / token / session / key (where generated, stored, transmitted) | |
| **Encryption and key management** | Transport encryption, storage encryption, KMS/Vault, rotation policy, access audit | |
| **Data flow** | Where data comes from → which services/queues/storage → where it goes (including third parties) | |
| **Access paths** | Through restricted platform? Direct DB/K8s/VPC connection, debug/exec, bypass scripts? | |
| **New export/bulk capability** | Yes/No (thresholds/rate limits/approval/audit/alerts) | |
| **Third parties and platforms** | Zendesk / Sentry / Grafana / Superset / NineData / Dittofeed / Noonlight / channel partners / Other | |
| **Deviates from company R&D standards** | Non-unified tracking/logging SDK, self-built reporting chain, plaintext secrets, non-Vault/KMS management | |
| **Identifier strategy** | temporary id / email alias / other pseudonymization approach | |
| **Ops/support personnel access scope** | Can they bypass restricted platform, view plaintext, export/bulk-pull? | |
| **Human access to high-sensitivity data** | Do address/phone have human-viewable entry points? Is zero-human-access committed? | |
| **Data retention and deletion** | Retention period, deletion/archival policy, whether backups are covered | |
| **DSAR/user rights** | Does it affect access/correction/deletion/export processes or traceability evidence | |

---

## Risk Category Definitions

| Risk ID | Risk Category | Description | Auto-Detection Clue Examples |
|--------|----------|------|------------------|
| R0 | System Type | Consumer-facing vs Internal (determines required controls) | - |
| R1 | Data Classification | Personal data/correlatable data/high-sensitivity content (video/address+phone) | Table structures, field names, API responses |
| R2 | Cross-Boundary Access | Cross-domain/cross-entity/cross-region; could unauthorized personnel access sensitive data | Permission role changes, cross-domain calls |
| R3 | Access Bypass | Direct DB/K8s/VPC, debug/exec, scripts bypassing restricted platform | Database connection strings, kubectl commands, SSH configs |
| R4 | Bulk Capability | Export/bulk query/enumeration-based user targeting/cross-ticket aggregation/bulk outreach | `export`/`download`/`csv`/`xlsx`/`report`/`bulk`/`batch` |
| R5 | Observation Leakage | Do logs/tracking/error events carry PII, request bodies, device identifiers, IPs | Logger calls, tracking SDKs, error reporting |
| R6 | Secrets/Credentials | Could passwords/tokens/keys appear in plaintext in storage/transmission/logs/error reports | Hard-coded strings, env vars, config files |
| R7 | Third-Party Boundary | Changes to third-party visible data, admin permissions, or audit capabilities | Third-party SDKs, Webhooks, external API calls, vendor endpoints |
| R8 | Masking and Audit Platform | Must internal products integrate with masking+audit platforms | Data access interfaces, query APIs |
| R9 | Cross-Entity/Cross-Border Access | Is the US Entity vs CN Entity access boundary weakened | Permission configs, data repatriation, break-glass processes |
| R10 | Bulk Sensitive Data Risk | New/relaxed bulk query, export, cross-ticket aggregation, or batch log pull capability | Paginated traversal, full pulls, background task exports, BI report downloads |
| R11 | Zero Human Access to High-Sensitivity Data | Could video/address/phone be directly viewed or exported by employees | Video playback interfaces, address display fields |
| R12 | Retention & Deletion/DSAR | Changes to retention period, deletion chain; impact on data subject rights closure | TTL/retention config, cleanup jobs, deletion APIs |
| R13 | Compliance Framework Inference | Infer potentially relevant regulations/standards based on users/regions, system type, data fields, business scenarios | User geography, data types |
| R14 | Agent Skills Supply Chain | Do AI Agent Skills in the project contain prompt injection, credential leakage, or script risks | `SKILL.md`, `.cursor/skills/`, `.cursor/rules/`, `AGENTS.md` |

---

## Company Standard Items — Detailed

The following are company R&D standards, **enforced by default**. If input/evidence does not cover them, do not ask the user for clarification details — directly provide "implement per company standards" remediation recommendations and mark the gap as "evidence needed (not clarification)."

### R5 Observation Leakage

| Requirement | Description |
|------|------|
| Unified Observability SDK | Must use the company's unified tracking/logging SDK |
| Log field allowlist/blocklist | SDK-layer field interception and masking |
| Masking policy | Sensitive fields masked at source |
| Export restrictions | Log exports require audit and restrictions |
| No bypass | Self-built reporting chains are prohibited |

### R6 Secrets/Credentials

| Requirement | Description |
|------|------|
| Secret Zero | Applications obtain secrets from a secure source at startup |
| No plaintext secrets | Code/configuration must not contain plaintext secrets |
| No hard-coded tokens/keys | No hard-coded authentication credentials |
| Rotation and audit | Secrets are regularly rotated with auditable access |

### CI/CD and Helm/IaC

| Requirement | Description |
|------|------|
| GitLab CI | Use Vault for secret injection |
| Helm values/chart | Must use Vault injection and controlled Secret references |
| K8s manifests | No plaintext secrets; use External Secrets or Vault |

### Log/Error Reporting

| Requirement | Description |
|------|------|
| Source masking | Sensitive fields are masked at source before reporting |
| Export restrictions | Error log exports require audit |
| No passwords/tokens | Logs/error reports must not contain passwords or tokens |

### R14 Agent Skills Supply Chain

> Only triggered when Agent Skills-related files are detected in the MR/repository; otherwise mark `Not Relevant (N/A)`.

**Auto-detection clues**:
- `SKILL.md` files (Agent Skills specification)
- `.cursor/skills/` directory (Cursor project-level Skills)
- `.cursor/rules/` directory (Cursor Rules)
- `AGENTS.md` files (Codex format)
- `agents.json` or `agents.yaml`

| Requirement | Description |
|------|------|
| No unreviewed third-party Skills | Only internally reviewed Skills are allowed (source: your skills repository) |
| Prompt injection detection | Check for `ignore previous instructions`, `bypass safety`, `override system`, etc. |
| Hard-coded credential detection | Check for real API Keys (`sk-`/`AKIA`/`ghp_`/`glpat-`), passwords, connection strings |
| No-script policy | Skills with scripts have 2.12x the vulnerability risk of instruction-only Skills ([arXiv 2510.26328](https://arxiv.org/abs/2510.26328)); prefer instruction-only Skills |
| Hidden HTML content detection | Check `<!-- -->` comments (invisible to humans but readable by LLMs; common attack vector) |
| Internal information protection | Skills should not contain internal domains, IP addresses, system architecture, or other sensitive information |
| File size compliance | SKILL.md recommended ≤ 500 lines; overly long files increase prompt injection concealment risk |

**Risk background** (based on academic research of 31,132 Skills):
- **26.1%** of Skills contain at least one vulnerability
- **13.3%** have data leakage risk
- **11.8%** enable privilege escalation
- Every line of a Skill file executes as an LLM instruction; prompt injection is extremely easy

### Masking Policy Changes

| Requirement | Description |
|------|------|
| Existing coverage | Company standards already cover masking for `user_id`, `SN`, `email` |
| New PII | If new/additional PII fields are used, masking policy review and registration are required |
| Contact | Contact the security lead for field-level masking policy and evidence |

### Ops/Support Access Boundary

| Requirement | Description |
|------|------|
| Restricted platform access | Production data must be accessed through a restricted platform |
| Default masking | Sensitive fields are masked by default |
| Default no-export | Export is prohibited by default; requires approval |
| Ticket/task binding | Access must be bound to a ticket/task reason |
| Full audit | All access operations are fully audited |

---

## Must-Clarify Items — Detailed

The following items **materially affect risk judgment and conclusions**. When missing, they must enter the clarification/blocking logic.

### System Type (block if unknown)

Must explicitly identify Consumer-facing / Internal product / Mixed; otherwise block subsequent checks.

### Export/Bulk Capability (auto-determine first; clarify if unable)

Prioritize auto-detection from code/configuration/documentation for export/bulk query/cross-ticket aggregation/bulk outreach. If unable to determine or clues exist but controls are not described, clarification is needed — **typically a blocking item**.

**Auto-detection clues**:
- `export`/`download`/`csv`/`xlsx`/`report`/`bulk`/`batch` related interfaces or UI
- Paginated traversal / full pulls
- Background task exports
- Admin tools
- BI report downloads
- Batch log pull scripts

### Third-Party Boundary (auto-determine first; clarify if unable)

Prioritize auto-detection from dependencies and integration configurations for new/modified third-party (SaaS/channel/vendor) data visibility and export capabilities. If unable to determine or clues exist but boundary/audit is not described, clarification is needed — **typically a blocking item**.

**Auto-detection clues**:
- New/modified third-party SDKs
- Webhooks
- External API calls
- Vendor endpoints in Helm values/environment variables
- Permission roles and export toggles
- Third-party visible field mappings

### Encryption and Key Management Approach (auto-determine first; clarify if unable)

If this change involves PIN/password/OTP/token/key or other authentication elements or sensitive field handling, confirm generation/storage/transmission/encryption and key rotation. Prioritize auto-detection from implementation and configuration. **Block as high risk if unable to determine**.

**Auto-detection clues**:
- Cryptography library usage
- KMS/Vault integration
- DB field encryption/hashing and salting
- Key reference method (env/secret/vault)
- CI/Helm injection method

### New PII Fields and Masking Approach

If PII fields beyond `user_id/SN/email` appear, clarification of masking policy, implementation point (unified SDK/platform/service-side), export restrictions, and audit evidence is required (**typically blocking if unknown**).

### Cross-Entity/Cross-Border and Exception Paths (auto-determine first; clarify if unable)

Only relevant when this change touches "production data access boundaries/permission models/restricted platforms/exception processes/cross-entity data flows." Prioritize auto-determination from code/configuration/process documentation. Clarification is needed if unable to determine or there are suspected boundary impacts without evidence (**block if high risk**).

**Auto-detection clues**:
- Permission role changes
- Admin query/export capability
- Restricted platform integration/bypass
- Cross-domain calls
- Data repatriation to unauthorized side
- Break-glass / approval flow changes

### Retention & Deletion/DSAR Changes (auto-determine first; clarify if unable)

Only relevant when this change adds/modifies personal data storage, log/audit retention, deletion/archival chains, or DSAR (access/correction/deletion/export) processes; otherwise mark `Not Relevant (N/A)`.

**Auto-detection clues**:
- New tables/fields/object storage
- TTL/retention config
- Cleanup jobs
- Backup/archival policies
- Deletion APIs/workers
- DSAR ticket/process integration

---

## Red Line Rules — Detailed

The following are **absolute red lines**; violations must be judged as `Remediation Required / Fail`:

### Video Data Zero Human Access

- **Rule**: Regardless of system type or operator, **no employee (including ops/support) may directly access raw video**
- **Verification**: Confirm in code/configuration or documentation "no human access path + controlled service-to-service access + audit evidence"
- **Violation**: If a path exists for human access/export of video, must judge as `Remediation Required / Fail`

### Password/Credential Red Line

- **Rule**: No plaintext password storage/transmission; passwords or tokens must not appear in logs/error reports
- **Verification**: Check storage-layer encryption/hashing, transport-layer encryption, log output
- **Violation**: If plaintext password storage/transmission/log output is found, must judge as `Remediation Required / Fail`

### High-Sensitivity Data (Address/Phone) Zero Human Access

- **Rule**: Address/phone and other high-sensitivity fields have zero human access; only controlled service-to-service calls
- **Verification**: Confirm no human-viewable entry point; service-to-service calls are audited
- **Violation**: If a human-viewable/exportable entry point is found, must judge as `Remediation Required / Fail`

---

## Sensitive Clue Triggered Blocking Clarification

If any of the following clues appear in input materials but the protection strategy/evidence is not clearly stated, it must be listed as a **blocking item** with priority follow-up:

| Clue Type | Examples |
|----------|------|
| **Authentication elements/secrets** | PIN code, verification code, password, security questions, reset token, session, API token, Private Key |
| **High-sensitivity personal data/regulated data** | Address/phone, precise location, audio, medical/health info (PHI), financial account |
| **Encryption gaps** | Transport encryption, storage encryption, key management (KMS/Vault), encryption algorithm and rotation, irreversible hash/salt not described |
| **Observation data deviating from company standards** | Non-unified tracking/logging SDK, self-built reporting chain, reported content suspected of containing sensitive fields without interception/masking |
| **Ops/support access boundary deviating from company standards** | Can bypass restricted platform for direct access, can view plaintext sensitive fields, can export/bulk-pull, lacks ticket binding and full audit |

---

## Compliance Framework Auto-Inference

Do not require the user to provide compliance/certification targets. Must auto-infer potentially relevant regulations/standards based on the following information, and explicitly label them as "**inferred/assumed**" in the output:

| Inference Basis | Potentially Relevant Regulations/Standards |
|----------|---------------------|
| Users in Europe | GDPR |
| Users in California, US | CCPA/CPRA |
| Involves health/medical data | HIPAA |
| Enterprise SaaS | SOC2 Type II |
| Involves personal data processing | ISO 27701 |

**Note**: Inferences are only used to guide inspection priorities and remediation recommendations; they are not treated as established facts or external commitments.

---

## Control Point Library

### Universal Control Points

| Control Point | Requirement |
|--------|------|
| Restricted platform access | No direct connections or bypass; all data access/operations through restricted platform with audit |
| Masking policy | email alias / temporary id / masking policy review for new PII |
| Audit evidence | Operations traceable to subject+reason+time window+ticket/activity |
| Export/bulk capability | Strong restrictions by default (thresholds/rate limits/approval/audit/alerts/freeze) |
| Third-party boundary | Third-party visible fields minimized; permissions and audit; export restrictions; changes require evidence |
| Cross-entity/cross-border boundary | US/CN boundary is explicit; exception paths executed by authorized side with masked conclusions returned |
| Bulk risk controls | Thresholds, rate limits, alerts, freeze, and audit evidence for bulk query/export/aggregation |
| Retention and deletion | Retention period is explicit; deletion covers backups/archives; execution evidence can be provided |

### Consumer-Facing System Control Points

| Control Point | Requirement |
|--------|------|
| External interface minimization | APIs/clients do not expose unnecessary sensitive fields or correlatable identifiers |
| User outreach boundary | Third parties/channels can only reach users through platform rules; they cannot obtain direct user identifiers |
| Video (red line) | Employees may not directly access raw video; only controlled service-to-service processing with audit |
| Emergency service data | Address/phone have zero human access; only controlled service-to-service calls with audit |
| Pseudonymization and mapping table governance | temporary id / email alias mapping tables are isolated, minimum privilege, default no-export, full audit, expiration semantics |
| DSAR impact | Whether it affects user access/correction/deletion/export closure |

### Internal Product Control Points

| Control Point | Requirement |
|--------|------|
| Mandatory platformization | Integrate with masking+audit platform; no direct connection to production sensitive data sources; frontend must not display plaintext sensitive fields |
| Permissions and export | Minimum privilege; export/bulk default to strong restrictions with full audit; admin capabilities must not create bypass |
| Entity boundary and exception paths | Exception queries executed by authorized entity, returning only masked conclusions |
| Zero human access to high-sensitivity data | Video/address/phone and other high-sensitivity fields are not visible in internal systems by default; only controlled service-to-service calls with full audit |

---

## Complete Examples

### Bad - Violation Examples

#### 1. Plaintext Hard-Coded Secret

```python
# Problem: Hard-coded API key (violates R6)
API_KEY = "sk-<account-id>abcdef"

def call_api():
    requests.get(url, headers={"Authorization": f"Bearer {API_KEY}"})
```

**Analysis**:
- Violates Secret Zero principle
- Credentials could leak to version control
- Cannot be rotated or audited

#### 2. Logs Contain Sensitive Information

```java
// Problem: Logging user password (violates R5, R6 red line)
logger.info("User login: username={}, password={}", username, password);
```

**Analysis**:
- Password appears in logs, violating the red line rule
- Logs may be exported or accessed by multiple people

#### 3. Direct SQL Bypassing Audit

```python
# Problem: Direct connection to production database, bypassing audit platform (violates R3, R8)
conn = psycopg2.connect("postgresql://prod-db:5432/users")
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
```

**Analysis**:
- Bypasses restricted platform for direct production database access
- No masking, no audit
- Internal product not platformized

#### 4. Bulk Export Without Controls

```python
# Problem: Bulk user data export with no restrictions (violates R4, R10)
@app.route('/admin/export/users')
def export_all_users():
    users = db.query("SELECT * FROM users")
    return generate_csv(users)
```

**Analysis**:
- No thresholds/rate limits
- No approval workflow
- No audit logs
- Could leak large amounts of sensitive data

#### 5. Sensitive Fields Visible to Third Party

```javascript
// Problem: Passing user phone number to third-party SDK (violates R7, R11)
analytics.track('user_signup', {
  email: user.email,
  phone: user.phone,  // High-sensitivity data leaked to third party
  address: user.address
});
```

**Analysis**:
- High-sensitivity data (phone, address) passed to third party
- Violates third-party boundary minimization principle
- Cannot control how the third party uses the data

### Good - Correct Examples

#### 1. Using Vault for Secret Management

```python
# Correct: Obtaining keys from Vault
import hvac

client = hvac.Client(url=os.environ['VAULT_ADDR'])
secret = client.secrets.kv.read_secret_version(path='myapp/api-key')
API_KEY = secret['data']['data']['key']
```

**Compliance points**:
- Secret Zero principle
- Centralized key management
- Supports rotation and audit

#### 2. Log Masking

```java
// Correct: Not logging sensitive information
logger.info("User login: username={}", username);
// Or use the unified masking SDK
logger.info("User login: {}", LogMasker.mask(loginEvent));
```

**Compliance points**:
- Uses the unified Observability SDK
- Sensitive fields masked at source
- Complies with company R&D standards

#### 3. Access Through Audit Platform

```python
# Correct: Access through restricted platform with automatic masking and audit
from company_sdk.data_platform import DataAccessClient

client = DataAccessClient(reason="Ticket #12345")
users = client.query("users", filters={"email": email})
```

**Compliance points**:
- Access through restricted platform
- Bound to ticket reason
- Automatic masking and audit

#### 4. Bulk Export With Controls

```python
# Correct: Bulk export with complete controls
@app.route('/admin/export/users')
@require_permission('export:users')
@rate_limit(max_per_day=10)
@audit_log('user_export')
def export_users():
    if request.args.get('count', 0) > 1000:
        return error("Exceeds single export limit")

    approval = get_approval(request.user, 'export_users')
    if not approval.valid:
        return error("Approval required")

    users = db.query("SELECT id, masked_email FROM users LIMIT 1000")
    return generate_csv(users)
```

**Compliance points**:
- Permission control
- Rate limiting
- Audit logging
- Quantity threshold
- Approval workflow
- Field masking

#### 5. Third-Party Data Minimization

```javascript
// Correct: Only pass necessary anonymized data to third parties
analytics.track('user_signup', {
  anonymous_id: generateAnonymousId(user.id),  // Pseudonymized
  signup_source: user.source,
  // Do not pass email, phone, or address
});
```

**Compliance points**:
- Pseudonymization applied
- Field minimization
- No high-sensitivity data passed to third parties
