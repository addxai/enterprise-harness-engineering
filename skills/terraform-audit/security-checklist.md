# AWS Terraform Security Audit Checklist

## Table of Contents

- [1. IAM](#1-iam)
- [2. S3](#2-s3)
- [3. Networking](#3-networking)
- [4. Encryption](#4-encryption)
- [5. Logging & Monitoring](#5-logging--monitoring)
- [6. Secrets Management](#6-secrets-management)

---

## 1. IAM

### 1.1 No wildcard Actions in IAM policies

Policies must not use `"Action": "*"` or overly broad wildcards. Scope actions to the minimum required.

Bad:
```hcl
statement {
  actions   = ["*"]
  resources = ["*"]
}
```

Good:
```hcl
statement {
  actions   = ["s3:GetObject", "s3:PutObject"]
  resources = ["arn:aws:s3:::my-bucket/*"]
}
```

### 1.2 No wildcard Resources in IAM policies

Resources must reference specific ARNs, not `"*"`, unless the action genuinely requires it (e.g., `s3:ListAllMyBuckets`).

Bad:
```hcl
statement {
  actions   = ["s3:DeleteBucket"]
  resources = ["*"]
}
```

Good:
```hcl
statement {
  actions   = ["s3:DeleteBucket"]
  resources = [aws_s3_bucket.this.arn]
}
```

### 1.3 No inline IAM policies

Use `aws_iam_role_policy_attachment` with managed policies instead of `aws_iam_role_policy` inline policies. Inline policies are harder to audit and reuse.

Bad:
```hcl
resource "aws_iam_role_policy" "inline" {
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.this.json
}
```

Good:
```hcl
resource "aws_iam_policy" "this" {
  policy = data.aws_iam_policy_document.this.json
}
resource "aws_iam_role_policy_attachment" "this" {
  role       = aws_iam_role.this.name
  policy_arn = aws_iam_policy.this.arn
}
```

### 1.4 Condition blocks required for sensitive actions

Actions such as `sts:AssumeRole`, `iam:CreateUser`, and `kms:Decrypt` must include a `condition` block to restrict by source IP, MFA, or organization.

Bad:
```hcl
statement {
  actions   = ["sts:AssumeRole"]
  resources = [aws_iam_role.target.arn]
}
```

Good:
```hcl
statement {
  actions   = ["sts:AssumeRole"]
  resources = [aws_iam_role.target.arn]
  condition {
    test     = "Bool"
    variable = "aws:MultiFactorAuthPresent"
    values   = ["true"]
  }
}
```

### 1.5 Cross-account access must use sts:ExternalId

Any `aws_iam_role` trust policy that allows cross-account `sts:AssumeRole` must require an `sts:ExternalId` condition to prevent the confused deputy problem.

Bad:
```hcl
statement {
  actions = ["sts:AssumeRole"]
  principals {
    type        = "AWS"
    identifiers = ["arn:aws:iam::<account-id>:root"]
  }
}
```

Good:
```hcl
statement {
  actions = ["sts:AssumeRole"]
  principals {
    type        = "AWS"
    identifiers = ["arn:aws:iam::<account-id>:root"]
  }
  condition {
    test     = "StringEquals"
    variable = "sts:ExternalId"
    values   = [var.external_id]
  }
}
```

### 1.6 No iam:PassRole with wildcard resource

`iam:PassRole` with `"Resource": "*"` allows passing any role to any service, enabling privilege escalation.

Bad:
```hcl
statement {
  actions   = ["iam:PassRole"]
  resources = ["*"]
}
```

Good:
```hcl
statement {
  actions   = ["iam:PassRole"]
  resources = [aws_iam_role.lambda_exec.arn]
}
```

---

## 2. S3

### 2.1 Public access block on every bucket

Every `aws_s3_bucket` must have a corresponding `aws_s3_bucket_public_access_block` with all four flags set to `true`.

Bad:
```hcl
resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket"
}
```

Good:
```hcl
resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

### 2.2 Server-side encryption enabled (SSE-S3 or KMS)

All buckets must have `aws_s3_bucket_server_side_encryption_configuration` using either `aws:kms` or `AES256`.

Bad:
```hcl
resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket"
}
```

Good:
```hcl
resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}
```

### 2.3 Versioning enabled for data buckets

Buckets storing application or user data must have `aws_s3_bucket_versioning` enabled to protect against accidental deletion.

Bad:
```hcl
resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket"
}
```

Good:
```hcl
resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  versioning_configuration {
    status = "Enabled"
  }
}
```

### 2.4 Access logging configured

S3 buckets should have `aws_s3_bucket_logging` pointing to a dedicated logging bucket for audit trail purposes.

Bad:
```hcl
resource "aws_s3_bucket" "app" {
  bucket = "my-app-bucket"
}
```

Good:
```hcl
resource "aws_s3_bucket_logging" "app" {
  bucket        = aws_s3_bucket.app.id
  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "s3-access-logs/"
}
```

### 2.5 No public-read or public-read-write ACL

Bucket ACLs must never be set to `public-read` or `public-read-write`. Use bucket policies with explicit principals instead.

Bad:
```hcl
resource "aws_s3_bucket_acl" "data" {
  bucket = aws_s3_bucket.data.id
  acl    = "public-read"
}
```

Good:
```hcl
resource "aws_s3_bucket_acl" "data" {
  bucket = aws_s3_bucket.data.id
  acl    = "private"
}
```

---

## 3. Networking

### 3.1 No 0.0.0.0/0 ingress on sensitive ports

Security groups must not allow `0.0.0.0/0` or `::/0` ingress on ports 22 (SSH), 3389 (RDP), 3306 (MySQL), 5432 (PostgreSQL), or 27017 (MongoDB).

Bad:
```hcl
ingress {
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}
```

Good:
```hcl
ingress {
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = [var.admin_cidr]
}
```

### 3.2 VPC flow logs enabled

Every `aws_vpc` must have an associated `aws_flow_log` for network traffic auditing.

Bad:
```hcl
resource "aws_vpc" "main" {
  cidr_block = "<ip>/16"
}
```

Good:
```hcl
resource "aws_flow_log" "main" {
  vpc_id          = aws_vpc.main.id
  traffic_type    = "ALL"
  iam_role_arn    = aws_iam_role.flow_log.arn
  log_destination = aws_cloudwatch_log_group.flow.arn
}
```

### 3.3 Databases in private subnets only

RDS instances and ElastiCache clusters must use subnet groups composed of private subnets. `publicly_accessible` must be `false`.

Bad:
```hcl
resource "aws_db_instance" "main" {
  publicly_accessible = true
  db_subnet_group_name = aws_db_subnet_group.public.name
}
```

Good:
```hcl
resource "aws_db_instance" "main" {
  publicly_accessible  = false
  db_subnet_group_name = aws_db_subnet_group.private.name
}
```

### 3.4 No use of default VPC

The default VPC has permissive networking defaults. All infrastructure must be deployed into explicitly defined VPCs.

Bad:
```hcl
resource "aws_instance" "app" {
  ami           = var.ami_id
  instance_type = "t3.micro"
}
```

Good:
```hcl
resource "aws_instance" "app" {
  ami           = var.ami_id
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.private.id
}
```

### 3.5 Security group descriptions required

All `aws_security_group` resources must include a meaningful `description` for audit and documentation purposes.

Bad:
```hcl
resource "aws_security_group" "web" {
  name   = "web-sg"
  vpc_id = aws_vpc.main.id
}
```

Good:
```hcl
resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Allow HTTPS from ALB to web tier"
  vpc_id      = aws_vpc.main.id
}
```

---

## 4. Encryption

### 4.1 EBS volumes encrypted

All `aws_ebs_volume` and `aws_instance` root/EBS block devices must set `encrypted = true`.

Bad:
```hcl
resource "aws_ebs_volume" "data" {
  availability_zone = "<region>a"
  size              = 100
}
```

Good:
```hcl
resource "aws_ebs_volume" "data" {
  availability_zone = "<region>a"
  size              = 100
  encrypted         = true
  kms_key_id        = aws_kms_key.ebs.arn
}
```

### 4.2 RDS storage encryption enabled

All `aws_db_instance` resources must set `storage_encrypted = true`.

Bad:
```hcl
resource "aws_db_instance" "main" {
  engine            = "postgres"
  instance_class    = "db.t3.medium"
  storage_encrypted = false
}
```

Good:
```hcl
resource "aws_db_instance" "main" {
  engine            = "postgres"
  instance_class    = "db.t3.medium"
  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds.arn
}
```

### 4.3 RDS TLS enforcement configured

RDS parameter groups should enforce SSL/TLS connections via `rds.force_ssl` (PostgreSQL) or `require_secure_transport` (MySQL).

Bad:
```hcl
resource "aws_db_parameter_group" "pg" {
  family = "postgres14"
}
```

Good:
```hcl
resource "aws_db_parameter_group" "pg" {
  family = "postgres14"
  parameter {
    name  = "rds.force_ssl"
    value = "1"
  }
}
```

### 4.4 KMS key rotation enabled

All `aws_kms_key` resources must have `enable_key_rotation = true` for automatic annual key rotation.

Bad:
```hcl
resource "aws_kms_key" "data" {
  description = "Data encryption key"
}
```

Good:
```hcl
resource "aws_kms_key" "data" {
  description         = "Data encryption key"
  enable_key_rotation = true
}
```

### 4.5 Elasticsearch/OpenSearch encryption at rest

All `aws_elasticsearch_domain` and `aws_opensearch_domain` resources must enable `encrypt_at_rest`.

Bad:
```hcl
resource "aws_opensearch_domain" "search" {
  domain_name    = "app-search"
  engine_version = "OpenSearch_2.5"
}
```

Good:
```hcl
resource "aws_opensearch_domain" "search" {
  domain_name    = "app-search"
  engine_version = "OpenSearch_2.5"
  encrypt_at_rest {
    enabled = true
  }
}
```

---

## 5. Logging & Monitoring

### 5.1 CloudTrail enabled in all regions

At least one `aws_cloudtrail` must have `is_multi_region_trail = true` to capture API activity across every AWS region.

Bad:
```hcl
resource "aws_cloudtrail" "main" {
  name           = "main-trail"
  s3_bucket_name = aws_s3_bucket.trail.id
}
```

Good:
```hcl
resource "aws_cloudtrail" "main" {
  name                  = "main-trail"
  s3_bucket_name        = aws_s3_bucket.trail.id
  is_multi_region_trail = true
}
```

### 5.2 CloudTrail log bucket has access logging

The S3 bucket receiving CloudTrail logs must itself have access logging enabled to detect tampering.

Bad:
```hcl
resource "aws_s3_bucket" "trail" {
  bucket = "cloudtrail-logs"
}
```

Good:
```hcl
resource "aws_s3_bucket_logging" "trail" {
  bucket        = aws_s3_bucket.trail.id
  target_bucket = aws_s3_bucket.access_logs.id
  target_prefix = "trail-bucket-logs/"
}
```

### 5.3 CloudWatch log group retention set

All `aws_cloudwatch_log_group` resources must define `retention_in_days` to avoid unbounded log storage costs and to meet compliance retention requirements.

Bad:
```hcl
resource "aws_cloudwatch_log_group" "app" {
  name = "/app/logs"
}
```

Good:
```hcl
resource "aws_cloudwatch_log_group" "app" {
  name              = "/app/logs"
  retention_in_days = 90
}
```

### 5.4 GuardDuty detector enabled

The account must have an `aws_guardduty_detector` resource with `enable = true` for threat detection.

Bad:
```hcl
resource "aws_guardduty_detector" "main" {
  enable = false
}
```

Good:
```hcl
resource "aws_guardduty_detector" "main" {
  enable = true
}
```

### 5.5 AWS Config recorder enabled

An `aws_config_configuration_recorder` must be present and started with `aws_config_configuration_recorder_status` to track resource configuration changes.

Bad:
```hcl
resource "aws_config_configuration_recorder_status" "main" {
  name       = aws_config_configuration_recorder.main.name
  is_enabled = false
}
```

Good:
```hcl
resource "aws_config_configuration_recorder_status" "main" {
  name       = aws_config_configuration_recorder.main.name
  is_enabled = true
}
```

---

## 6. Secrets Management

### 6.1 No hardcoded AWS access keys

Terraform files must not contain hardcoded AWS access key IDs (strings matching `AKIA*`) or secret keys. Use IAM roles or environment variables.

Bad:
```hcl
provider "aws" {
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}
```

Good:
```hcl
provider "aws" {
  region = var.aws_region
}
```

### 6.2 No plaintext password defaults in variables

Variables for passwords, tokens, or secrets must not have plaintext `default` values. Use `null` or omit the default to force callers to provide values.

Bad:
```hcl
variable "db_password" {
  default = "SuperSecret123!"
}
```

Good:
```hcl
variable "db_password" {
  type      = string
  sensitive = true
}
```

### 6.3 Use SSM Parameter Store or Secrets Manager

Secrets consumed at runtime should be stored in `aws_ssm_parameter` (SecureString) or `aws_secretsmanager_secret` rather than passed as plain Terraform outputs.

Bad:
```hcl
output "db_password" {
  value = var.db_password
}
```

Good:
```hcl
resource "aws_ssm_parameter" "db_password" {
  name  = "/app/db_password"
  type  = "SecureString"
  value = var.db_password
}
```

### 6.4 Variables with secret names must be marked sensitive = true

Variables whose names contain `password`, `secret`, `token`, `key`, or `credential` must include `sensitive = true`. This prevents secret values from appearing in CLI output and state file diffs. For the general practice of marking any variable `sensitive`, see the code quality checklist.

Bad:
```hcl
variable "api_token" {
  type = string
}
```

Good:
```hcl
variable "api_token" {
  type      = string
  sensitive = true
}
```
