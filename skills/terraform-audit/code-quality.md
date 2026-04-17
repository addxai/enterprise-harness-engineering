# Terraform Code Quality & Best Practices Checklist

## Table of Contents

1. [Modularity](#1-modularity)
2. [Naming Conventions](#2-naming-conventions)
3. [Variables & Outputs](#3-variables--outputs)
4. [State Management](#4-state-management)
5. [Version Pinning](#5-version-pinning)
6. [DRY Principles](#6-dry-principles)
7. [File Structure](#7-file-structure)

---

## 1. Modularity

### 1.1 Root module exceeding 300 lines should be split into child modules

```hcl
# Bad: monolithic main.tf with networking, compute, database, and IAM all in one file
resource "aws_vpc" "main" { ... }
resource "aws_subnet" "public" { ... }
resource "aws_instance" "app" { ... }
resource "aws_db_instance" "primary" { ... }
resource "aws_iam_role" "app_role" { ... }
# ... 400+ lines continuing in the same file
```

```hcl
# Good: split into focused child modules
module "networking" {
  source = "./modules/networking"
  cidr   = var.vpc_cidr
}

module "compute" {
  source    = "./modules/compute"
  subnet_id = module.networking.public_subnet_id
}

module "database" {
  source    = "./modules/database"
  subnet_id = module.networking.private_subnet_id
}
```

### 1.2 Repeated blocks (>2 similar resources) should use for_each or a module

```hcl
# Bad: copy-pasted resources with minor differences
resource "aws_s3_bucket" "logs" {
  bucket = "myapp-logs"
}
resource "aws_s3_bucket" "assets" {
  bucket = "myapp-assets"
}
resource "aws_s3_bucket" "backups" {
  bucket = "myapp-backups"
}
```

```hcl
# Good: driven by a map with for_each
locals {
  buckets = toset(["logs", "assets", "backups"])
}

resource "aws_s3_bucket" "this" {
  for_each = local.buckets
  bucket   = "myapp-${each.key}"
}
```

### 1.3 Module source versions must be pinned

```hcl
# Bad: unpinned module source
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
}
```

```hcl
# Good: version pinned for reproducibility
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.5.1"
}
```

### 1.4 No business logic in the root module for large projects

```hcl
# Bad: root module contains inline IAM policy JSON and complex conditionals
resource "aws_iam_policy" "app" {
  name = "app-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Effect = "Allow", Action = ["s3:GetObject"], Resource = var.env == "prod" ? "arn:aws:s3:::prod-*" : "arn:aws:s3:::dev-*" },
      { Effect = "Allow", Action = ["dynamodb:*"], Resource = var.enable_dynamo ? aws_dynamodb_table.this[0].arn : "" },
    ]
  })
}
```

```hcl
# Good: root module delegates to a purpose-built module
module "iam" {
  source      = "./modules/iam"
  environment = var.environment
  bucket_arns = module.storage.bucket_arns
}
```

---

## 2. Naming Conventions

### 2.1 Resources and data sources must use snake_case

```hcl
# Bad: camelCase or mixed naming
resource "aws_instance" "myAppServer" { ... }
data "aws_ami" "LatestUbuntu" { ... }
```

```hcl
# Good: consistent snake_case
resource "aws_instance" "my_app_server" { ... }
data "aws_ami" "latest_ubuntu" { ... }
```

### 2.2 Resource names must be descriptive, not generic placeholders

```hcl
# Bad: generic name that conveys no purpose
resource "aws_instance" "this" { ... }
resource "aws_security_group" "main" { ... }
```

```hcl
# Good: name describes the role of the resource
resource "aws_instance" "api_server" { ... }
resource "aws_security_group" "api_ingress" { ... }
```

### 2.3 Variable names should follow a consistent prefix/suffix convention

```hcl
# Bad: inconsistent naming across variables
variable "vpcCidr" {}
variable "db-name" {}
variable "EnableFlag" {}
```

```hcl
# Good: snake_case with consistent domain prefixes
variable "vpc_cidr_block" {}
variable "database_name" {}
variable "feature_flag_enabled" {}
```

### 2.4 Locals must be named by purpose, not by value

```hcl
# Bad: name describes the literal value
locals {
  string1 = "${var.project}-${var.environment}"
  list1   = ["<region>a", "<region>b"]
}
```

```hcl
# Good: name describes intent and usage
locals {
  resource_prefix    = "${var.project}-${var.environment}"
  availability_zones = ["<region>a", "<region>b"]
}
```

---

## 3. Variables & Outputs

### 3.1 Every variable must have a description

```hcl
# Bad: no description
variable "cidr" {
  type = string
}
```

```hcl
# Good: description explains purpose and expected format
variable "cidr" {
  description = "CIDR block for the VPC (e.g., <ip>/16)."
  type        = string
}
```

### 3.2 Every variable must have a type constraint

```hcl
# Bad: missing type allows any value
variable "instance_count" {
  description = "Number of instances."
}
```

```hcl
# Good: explicit type constraint
variable "instance_count" {
  description = "Number of instances to launch."
  type        = number
}
```

### 3.3 Variables whose output should be redacted must use sensitive = true

Any variable where plan output or state references should be hidden must be marked. This is a general code hygiene rule — for secret-specific detection (passwords, tokens, keys), see the security checklist.

```hcl
# Bad: internal IPs visible in plan output
variable "internal_api_endpoint" {
  description = "Internal API endpoint (not for public exposure)."
  type        = string
}
```

```hcl
# Good: redacted from CLI output
variable "internal_api_endpoint" {
  description = "Internal API endpoint (not for public exposure)."
  type        = string
  sensitive   = true
}
```

### 3.4 Complex variables should use validation blocks

```hcl
# Bad: no validation, invalid values surface only at apply time
variable "environment" {
  description = "Deployment environment."
  type        = string
}
```

```hcl
# Good: validation catches bad input at plan time
variable "environment" {
  description = "Deployment environment."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}
```

### 3.5 Outputs must have a description

```hcl
# Bad: output with no description
output "vpc_id" {
  value = aws_vpc.main.id
}
```

```hcl
# Good: description clarifies what consumers receive
output "vpc_id" {
  description = "ID of the provisioned VPC."
  value       = aws_vpc.main.id
}
```

### 3.6 No unused variables or outputs

```hcl
# Bad: variable declared but never referenced anywhere
variable "legacy_flag" {
  description = "No longer used."
  type        = bool
  default     = false
}
```

```hcl
# Good: remove dead declarations; keep only what is referenced
# (variable "legacy_flag" deleted entirely)
```

---

## 4. State Management

### 4.1 Remote backend must be configured

```hcl
# Bad: implicit local backend stores state on disk
terraform {
  # no backend block at all
}
```

```hcl
# Good: remote backend with encryption
terraform {
  backend "s3" {
    bucket  = "mycompany-tfstate"
    key     = "network/terraform.tfstate"
    region  = "<region>"
    encrypt = true
  }
}
```

### 4.2 State locking must be enabled

```hcl
# Bad: S3 backend without locking
terraform {
  backend "s3" {
    bucket = "mycompany-tfstate"
    key    = "app/terraform.tfstate"
    region = "<region>"
  }
}
```

```hcl
# Good: DynamoDB table enables locking on S3 backend
terraform {
  backend "s3" {
    bucket         = "mycompany-tfstate"
    key            = "app/terraform.tfstate"
    region         = "<region>"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}
```

### 4.3 State key path must include environment identifier

The backend key should contain the environment name so each environment resolves to a distinct state file. For the broader architectural concern of environment isolation (account separation, blast radius), see the architecture review checklist.

```hcl
# Bad: no environment in key path — all envs share one state
terraform {
  backend "s3" {
    key = "app/terraform.tfstate"
  }
}
```

```hcl
# Good: environment in key path via -backend-config or explicit path
terraform {
  backend "s3" {
    bucket         = "mycompany-tfstate"
    key            = "prod/app/terraform.tfstate"
    region         = "<region>"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

### 4.4 terraform.tfstate must not be committed to version control

```hcl
# Bad: .gitignore missing state files
# (no entry for *.tfstate)
```

```hcl
# Good: .gitignore excludes state and backup files
# .gitignore
*.tfstate
*.tfstate.backup
*.tfstate.*.backup
.terraform/
```

---

## 5. Version Pinning

### 5.1 required_version must be set in the terraform block

```hcl
# Bad: no version constraint, any Terraform CLI version accepted
terraform {
  required_providers { ... }
}
```

```hcl
# Good: constrained to a specific minor version range
terraform {
  required_version = "~> 1.7.0"
  required_providers { ... }
}
```

### 5.2 Provider versions must be pinned with ~> or = (never unpinned)

```hcl
# Bad: no version constraint on the provider
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}
```

```hcl
# Good: pessimistic constraint allows only patch upgrades
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }
}
```

### 5.3 Registry module versions must be pinned

```hcl
# Bad: no version on registry module
module "eks" {
  source = "terraform-aws-modules/eks/aws"
}
```

```hcl
# Good: explicit version pin
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.8.0"
}
```

### 5.4 Do not use >= 0.0.0 or no constraint as a version bound

```hcl
# Bad: effectively unpinned, accepts any version
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 0.0.0"
    }
  }
}
```

```hcl
# Good: meaningful lower bound with upper constraint
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.30, < 6.0"
    }
  }
}
```

---

## 6. DRY Principles

### 6.1 Repeated literal values should be extracted into locals

```hcl
# Bad: same tag map copy-pasted across resources
resource "aws_instance" "app" {
  tags = { Project = "acme", Environment = "prod", ManagedBy = "terraform" }
}
resource "aws_s3_bucket" "data" {
  tags = { Project = "acme", Environment = "prod", ManagedBy = "terraform" }
}
```

```hcl
# Good: common tags defined once in locals
locals {
  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_instance" "app" {
  tags = local.common_tags
}
resource "aws_s3_bucket" "data" {
  tags = local.common_tags
}
```

### 6.2 Repeated resources should use for_each or count

```hcl
# Bad: three nearly identical subnet resources
resource "aws_subnet" "az_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "<ip>/24"
  availability_zone = "<region>a"
}
resource "aws_subnet" "az_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "<ip>/24"
  availability_zone = "<region>b"
}
```

```hcl
# Good: for_each over a map
variable "subnets" {
  default = {
    "<region>a" = "<ip>/24"
    "<region>b" = "<ip>/24"
  }
}

resource "aws_subnet" "this" {
  for_each          = var.subnets
  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value
  availability_zone = each.key
}
```

### 6.3 Conditional resource creation should use count with a ternary

```hcl
# Bad: entire resource block commented out or duplicated across branches
# resource "aws_cloudwatch_log_group" "app" { ... }   # uncomment for prod
```

```hcl
# Good: count driven by a boolean variable
resource "aws_cloudwatch_log_group" "app" {
  count             = var.enable_logging ? 1 : 0
  name              = "/app/${var.environment}"
  retention_in_days = 30
}
```

### 6.4 Repeated nested blocks should use dynamic blocks

```hcl
# Bad: ingress rules manually duplicated
resource "aws_security_group" "web" {
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

```hcl
# Good: dynamic block iterates over a variable
variable "ingress_rules" {
  default = [
    { port = 80,  cidr = "0.0.0.0/0" },
    { port = 443, cidr = "0.0.0.0/0" },
  ]
}

resource "aws_security_group" "web" {
  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = "tcp"
      cidr_blocks = [ingress.value.cidr]
    }
  }
}
```

### 6.5 No copy-paste between environments; use workspaces or variable files

```hcl
# Bad: separate directories with duplicated .tf files
# envs/dev/main.tf   (copy of prod)
# envs/prod/main.tf  (copy of dev)
```

```hcl
# Good: single configuration with per-environment .tfvars
# terraform apply -var-file=envs/prod.tfvars

# envs/prod.tfvars
environment    = "prod"
instance_type  = "m5.large"
instance_count = 3

# envs/dev.tfvars
environment    = "dev"
instance_type  = "t3.micro"
instance_count = 1
```

---

## 7. File Structure

### 7.1 Standard files must be present in every module

```
# Bad: everything dumped into a single file
my-module/
  everything.tf
```

```
# Good: canonical file layout
my-module/
  main.tf          # resource and module blocks
  variables.tf     # all input variables
  outputs.tf       # all output values
  providers.tf     # provider configuration
  versions.tf      # terraform and required_providers blocks
```

### 7.2 Backend configuration belongs in backend.tf or providers.tf

```hcl
# Bad: backend block buried inside main.tf among resources
# main.tf
terraform {
  backend "s3" { ... }
}
resource "aws_vpc" "main" { ... }
```

```hcl
# Good: isolated in a dedicated backend.tf
# backend.tf
terraform {
  backend "s3" {
    bucket         = "mycompany-tfstate"
    key            = "network/terraform.tfstate"
    region         = "<region>"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

### 7.3 Data sources should be grouped together

```hcl
# Bad: data sources scattered between resources throughout main.tf
resource "aws_instance" "app" { ... }
data "aws_ami" "ubuntu" { ... }
resource "aws_security_group" "app" { ... }
data "aws_vpc" "selected" { ... }
```

```hcl
# Good: data sources collected at the top of main.tf or in data.tf
# data.tf
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-*-amd64-server-*"]
  }
}

data "aws_vpc" "selected" {
  id = var.vpc_id
}
```

### 7.4 Every reusable module must include a README.md

```
# Bad: module with no documentation
modules/networking/
  main.tf
  variables.tf
  outputs.tf
```

```
# Good: README describes purpose, inputs, outputs, and usage
modules/networking/
  README.md        # module purpose, example usage, input/output table
  main.tf
  variables.tf
  outputs.tf
```
