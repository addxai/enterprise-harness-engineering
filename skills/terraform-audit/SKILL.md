---
name: terraform-audit
description: Audit Terraform codebases for security, cost, code quality, and architecture issues. Use when reviewing Terraform projects, checking infrastructure-as-code compliance, or assessing AWS resource configurations for best practices.
---

# Terraform Audit Skill

Perform a comprehensive audit of a Terraform codebase across four dimensions: security & compliance, cost optimization, code quality, and architecture design. The audit produces a structured Markdown report with findings classified by severity. Rules are grounded in the CIS AWS Foundations Benchmark and the AWS Well-Architected Framework, with a primary focus on AWS resources.

## Description

Perform a comprehensive audit of a Terraform codebase covering four dimensions: security and compliance, cost optimization, code quality, and architecture design. Based on the CIS AWS Foundations Benchmark and the AWS Well-Architected Framework, output a structured Markdown audit report for AWS resources classified by Critical / Important / Minor severity levels.

---

## Execution Guidelines

- Scan the project structure before auditing; determine scale by the number of `.tf` files (Small / Medium / Large) and choose the corresponding strategy
- Execute the four dimensions in order: Security -> Cost -> Quality -> Architecture, reading the corresponding sub-module checklist for each
- Every finding must include a severity level, affected file and line number, and specific remediation advice (including HCL code)
- Use the [report-template.md](report-template.md) template for the report, saved to the project root directory
- When cross-dimensional complementary rules exist (e.g., Multi-AZ in both architecture and cost), annotate the cross-reference context

---

## Examples

### Bad

```hcl
# S3 bucket with no encryption, no versioning, public access
resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket"
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}
```

### ✅ Good

```hcl
resource "aws_s3_bucket" "data" {
  bucket = "${var.project}-${var.environment}-data"
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.main.arn
    }
  }
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

---

## Audit Workflow

Copy this checklist and update it as you progress:

```
Audit Progress:
- [ ] Step 1: Scan project structure
- [ ] Step 2: Security & compliance audit
- [ ] Step 3: Cost optimization audit
- [ ] Step 4: Code quality audit
- [ ] Step 5: Architecture design audit
- [ ] Step 6: Generate report
```

---

## Step 1: Scan Project Structure

Use Glob to find all `**/*.tf` files in the target project. Then determine:

- **Module structure**: Identify root module, nested modules, and shared/reusable modules.
- **Backend configuration**: Check for remote state backend (S3, GCS, Terraform Cloud, etc.) and state locking.
- **Provider usage**: List providers and their version constraints.
- **Terraform version**: Check `required_version` in `terraform {}` blocks.
- **Project scale**:
  - **Small**: < 10 `.tf` files — audit all files in a single pass.
  - **Medium**: 10-30 `.tf` files — group by module, audit each module.
  - **Large**: 30+ `.tf` files — prioritize root module and shared modules first, then environment-specific configs.

Record the scale; it determines the audit strategy in later steps.

---

## Step 2: Security & Compliance Audit

Read [security-checklist.md](security-checklist.md) and apply each rule to the scanned codebase.

**Categories covered**: IAM policies & roles, S3 bucket configuration, networking (security groups, NACLs, public access), encryption at rest and in transit, logging & monitoring, secrets management.

Classify every finding as **Critical**, **Important**, or **Minor** per the severity table below.

---

## Step 3: Cost Optimization Audit

Read [cost-optimization.md](cost-optimization.md) and apply each rule to the scanned codebase.

**Categories covered**: Compute right-sizing, storage tiering & lifecycle, database instance sizing & reserved capacity, networking costs (NAT gateways, data transfer), tagging & cost governance.

Classify every finding as **Critical**, **Important**, or **Minor**.

---

## Step 4: Code Quality Audit

Read [code-quality.md](code-quality.md) and apply each rule to the scanned codebase.

**Categories covered**: Modularity & reuse, naming conventions, variable & output hygiene, state management, provider & module version pinning, DRY principle adherence, file & directory structure.

Classify every finding as **Critical**, **Important**, or **Minor**.

---

## Step 5: Architecture Design Audit

Read [architecture-review.md](architecture-review.md) and apply each rule to the scanned codebase.

**Categories covered**: High availability, disaster recovery, network design (VPC layout, subnet strategy, connectivity), environment isolation, scalability & auto-scaling readiness.

Classify every finding as **Critical**, **Important**, or **Minor**.

---

## Issue Severity Classification

| Level | Definition | Examples |
|-------|-----------|----------|
| **Critical** | Immediate security risk or data loss potential | Hardcoded secrets, publicly accessible S3 buckets, wildcard IAM permissions |
| **Important** | Best practice violation with significant impact | Missing state locking, no version pins, oversized instances |
| **Minor** | Style or optimization suggestion | Naming inconsistencies, missing variable descriptions |

---

## Step 6: Generate Report

Read [report-template.md](report-template.md) for the exact output format.

- Save the report to `{project_root}/terraform-audit-report.md`.
- Within each dimension, sort findings by severity: Critical first, then Important, then Minor.
- The executive summary must include total finding counts per severity level and an overall assessment (PASS / NEEDS ATTENTION / CRITICAL ISSUES).

---

## Project Scale Adaptation

| Scale | Strategy |
|-------|----------|
| **Small** (< 10 `.tf` files) | Audit every file directly in one pass. |
| **Medium** (10-30 files) | Group files by module. Audit each module as a unit. |
| **Large** (30+ files) | Audit root module and shared modules first. Then audit environment-specific configurations. Summarize cross-cutting concerns at the end. |
