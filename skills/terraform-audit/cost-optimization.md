# AWS Cost Optimization Checklist for Terraform Audits

Use this checklist when reviewing Terraform code for AWS cost issues. Every rule is
actionable -- flag it only when the code can be changed to produce real savings.

---

## Table of Contents

1. [Compute](#1-compute)
2. [Storage](#2-storage)
3. [Database](#3-database)
4. [Networking](#4-networking)
5. [Governance](#5-governance)

---

## 1. Compute

### 1.1 Oversized instances (>= x2large without justification)

**Flag:** Any `instance_type` set to `*.2xlarge` or larger where no inline comment or
variable description explains the sizing requirement.

**Why:** Large instances are the single biggest source of cloud waste; most workloads
never sustain the CPU/memory that justifies them.

**Recommendation:** Downsize to the smallest instance that meets peak + 20% headroom,
or add a comment documenting the sizing rationale.

### 1.2 Missing Auto Scaling Group

**Flag:** Standalone `aws_instance` resources used for application workloads (not
bastion hosts or one-off tooling).

**Why:** Fixed instance counts pay for peak capacity 24/7 even when demand is low.

**Recommendation:** Replace with `aws_autoscaling_group` and a target-tracking scaling
policy tied to CPU or request count.

### 1.3 Non-Graviton instance families

**Flag:** Instance families starting with `m5`, `c5`, `r5`, `t3` or similar x86
families when a Graviton equivalent exists (`m7g`, `c7g`, `r7g`, `t4g`).

**Why:** Graviton instances deliver up to 40% better price-performance than comparable
x86 instances.

**Recommendation:** Switch to the equivalent Graviton family after confirming the
application runs on ARM64.

### 1.4 On-demand instances in non-production environments

**Flag:** `aws_instance` or `aws_autoscaling_group` without a `spot_price`,
`instance_market_options`, or `mixed_instances_policy` block when the resource is
tagged or named as dev, staging, qa, or test.

**Why:** Spot instances cost 60-90% less than on-demand and are acceptable for
non-production workloads that tolerate interruption.

**Recommendation:** Use spot instances or a mixed instances policy.

```hcl
resource "aws_autoscaling_group" "app" {
  mixed_instances_policy {
    instances_distribution {
      on_demand_base_capacity                  = 0
      on_demand_percentage_above_base_capacity = 0   # 100% spot for non-prod
      spot_allocation_strategy                 = "capacity-optimized"
    }
    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.app.id
        version            = "$Latest"
      }
      override {
        instance_type = "m7g.large"
      }
      override {
        instance_type = "m6g.large"
      }
    }
  }
}
```

### 1.5 EBS optimization not enabled

**Flag:** `aws_instance` resources where `ebs_optimized` is not set to `true` (for
instance types that support but do not default to it).

**Why:** Without EBS optimization the instance shares network bandwidth between EBS
and general traffic, causing throttling and potentially requiring a larger instance.

**Recommendation:** Set `ebs_optimized = true`.

---

## 2. Storage

### 2.1 S3 buckets missing lifecycle rules

**Flag:** Any `aws_s3_bucket` without a corresponding `aws_s3_bucket_lifecycle_configuration`
resource.

**Why:** Without lifecycle rules, objects accumulate indefinitely in the most expensive
storage class.

**Recommendation:** Add a lifecycle configuration that transitions objects to cheaper
tiers and expires old versions.

```hcl
resource "aws_s3_bucket_lifecycle_configuration" "this" {
  bucket = aws_s3_bucket.this.id

  rule {
    id     = "archive-and-expire"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}
```

### 2.2 EBS volumes using gp2 instead of gp3

**Flag:** `aws_ebs_volume` or root/additional block devices with `type = "gp2"` or no
type specified (gp2 is the legacy default in some provider versions).

**Why:** gp3 is 20% cheaper than gp2 at baseline and includes 3000 IOPS and 125 MiB/s
throughput at no extra cost.

**Recommendation:** Change volume type to `gp3`.

### 2.3 Large io1/io2 volumes without IOPS justification

**Flag:** `aws_ebs_volume` with type `io1` or `io2` where provisioned IOPS exceed
10,000 and there is no sizing comment.

**Why:** Provisioned IOPS volumes are billed per IOPS-month; over-provisioning is
extremely expensive.

**Recommendation:** Document the required IOPS with a comment, or switch to gp3 which
provides up to 16,000 IOPS at lower cost.

### 2.4 Missing S3 Intelligent-Tiering

**Flag:** Buckets with unpredictable or unknown access patterns that use `STANDARD`
storage class without Intelligent-Tiering.

**Why:** Intelligent-Tiering automatically moves objects between access tiers with no
retrieval fees, saving up to 68% on infrequently accessed data.

**Recommendation:** Set the default storage class to `INTELLIGENT_TIERING` or add it
as a lifecycle transition at day 0.

### 2.5 Unused EBS snapshots

**Flag:** `aws_ebs_snapshot` resources that are not referenced by any AMI, launch
template, or volume restoration logic in the codebase.

**Why:** EBS snapshots are billed per GB-month and orphaned snapshots accumulate cost
silently.

**Recommendation:** Remove the snapshot resource or add a retention/cleanup mechanism.

---

## 3. Database

### 3.1 RDS Multi-AZ enabled in non-production

**Flag:** `aws_db_instance` with `multi_az = true` where the resource name, tags, or
workspace indicates a non-production environment.

**Why:** Multi-AZ doubles the RDS cost by running a synchronous standby replica that
non-production workloads do not need.

**Recommendation:** Set `multi_az = false` for dev/staging/qa environments. Use a
variable to toggle by environment. Note: for production environments, Multi-AZ is recommended for availability (see architecture review).

```hcl
variable "environment" {
  type = string
}

resource "aws_db_instance" "main" {
  # ...
  multi_az = var.environment == "production" ? true : false
}
```

### 3.2 Oversized RDS instances

**Flag:** RDS instances using `db.r5.2xlarge` or larger, or any `db.r*`/`db.m*`
instance in a non-production environment above `db.t4g.medium`.

**Why:** Database instance cost is the largest component of most RDS bills and
right-sizing delivers immediate savings.

**Recommendation:** Use `db.t4g.*` burstable instances for non-production and
right-size production based on CloudWatch CPU/memory metrics.

### 3.3 Missing RDS storage auto-scaling

**Flag:** `aws_db_instance` without `max_allocated_storage` set.

**Why:** Without storage auto-scaling teams over-provision disk to avoid running out of
space, paying for capacity they may never use.

**Recommendation:** Set `max_allocated_storage` to a reasonable upper bound (e.g., 2x
the initial `allocated_storage`).

### 3.4 Aurora vs single-instance evaluation

**Flag:** `aws_rds_cluster` with a single `aws_rds_cluster_instance` for workloads
that do not need Aurora features (global databases, fast cloning, read replicas).

**Why:** Aurora pricing is higher per ACU/instance-hour than standard RDS; a single
writer with no readers often costs more on Aurora for no benefit.

**Recommendation:** Evaluate whether standard RDS with Multi-AZ meets the availability
requirement at lower cost.

### 3.5 DynamoDB on-demand vs provisioned evaluation

**Flag:** `aws_dynamodb_table` with `billing_mode = "PAY_PER_REQUEST"` that serves
predictable, steady-state traffic (identifiable from naming conventions like
`sessions`, `config`, `metadata`).

**Why:** On-demand mode costs roughly 6.5x more per unit than provisioned capacity for
predictable workloads.

**Recommendation:** Switch to `PROVISIONED` billing mode with auto-scaling for tables
with steady traffic patterns.

```hcl
resource "aws_dynamodb_table" "sessions" {
  billing_mode   = "PROVISIONED"
  read_capacity  = 10
  write_capacity = 5
  # ...
}

resource "aws_appautoscaling_target" "read" {
  max_capacity       = 100
  min_capacity       = 5
  resource_id        = "table/${aws_dynamodb_table.sessions.name}"
  scalable_dimension = "dynamodb:table:ReadCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_policy" "read" {
  name               = "DynamoDBReadAutoScaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.read.resource_id
  scalable_dimension = aws_appautoscaling_target.read.scalable_dimension
  service_namespace  = aws_appautoscaling_target.read.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = 70.0
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBReadCapacityUtilization"
    }
  }
}
```

---

## 4. Networking

### 4.1 NAT Gateway per-AZ cost

**Flag:** More than two `aws_nat_gateway` resources without a comment justifying high
availability requirements.

**Why:** Each NAT Gateway costs ~$32/month plus $0.045/GB processed; deploying one per
AZ in a 3+ AZ VPC adds significant fixed cost.

**Recommendation:** For non-production or cost-sensitive environments, use a single NAT
Gateway. For production, document the HA justification if deploying one per AZ.

### 4.2 Missing VPC endpoints for S3 and DynamoDB

**Flag:** A VPC definition (`aws_vpc`) that contains resources accessing S3 or
DynamoDB but has no `aws_vpc_endpoint` for those services.

**Why:** Without a Gateway VPC endpoint, S3/DynamoDB traffic routes through the NAT
Gateway incurring per-GB data processing charges that the free Gateway endpoint
eliminates.

**Recommendation:** Add Gateway VPC endpoints for S3 and DynamoDB in every VPC.

```hcl
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.region}.s3"
  route_table_ids = [
    aws_route_table.private.id,
  ]
}

resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${var.region}.dynamodb"
  route_table_ids = [
    aws_route_table.private.id,
  ]
}
```

### 4.3 Cross-AZ data transfer

**Flag:** Architecture patterns where application tiers (e.g., web servers and
databases) are placed in different availability zones without acknowledgment of data
transfer costs.

**Why:** Cross-AZ data transfer costs $0.01/GB in each direction, which adds up
quickly for high-throughput services.

**Recommendation:** Co-locate tightly coupled services in the same AZ where possible,
or document that the cross-AZ cost is accepted for availability.

### 4.4 Unused Elastic IPs

**Flag:** `aws_eip` resources that are not associated with a running instance or NAT
Gateway via `aws_eip_association` or inline `allocation_id`.

**Why:** Unattached Elastic IPs cost $0.005/hour ($3.60/month each) and serve no
purpose.

**Recommendation:** Remove the EIP resource or associate it with an active resource.

---

## 5. Governance

### 5.1 Missing cost-allocation tags

**Flag:** Any billable resource (`aws_instance`, `aws_db_instance`, `aws_s3_bucket`,
`aws_lb`, etc.) missing the following tags: `Project`, `Environment`, `Owner`,
`CostCenter`.

**Why:** Without cost-allocation tags it is impossible to attribute spend to teams or
projects, making optimization invisible.

**Recommendation:** Enforce tags via `default_tags` in the provider block and validate
with a policy tool (Sentinel, OPA, or `tflint`).

```hcl
provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project     = var.project
      Environment = var.environment
      Owner       = var.owner
      CostCenter  = var.cost_center
      ManagedBy   = "terraform"
    }
  }
}
```

### 5.2 No budget alarm defined

**Flag:** A Terraform codebase with no `aws_budgets_budget` resource.

**Why:** Without a budget alarm, cost overruns go unnoticed until the monthly bill
arrives.

**Recommendation:** Add at least one budget with an SNS notification at 80% and 100%
of the forecasted monthly spend.

```hcl
resource "aws_budgets_budget" "monthly" {
  name         = "${var.project}-monthly-budget"
  budget_type  = "COST"
  limit_amount = var.monthly_budget_limit
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator       = "GREATER_THAN"
    threshold                 = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "FORECASTED"
    subscriber_sns_topic_arns = [aws_sns_topic.billing_alerts.arn]
  }

  notification {
    comparison_operator       = "GREATER_THAN"
    threshold                 = 100
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_sns_topic_arns = [aws_sns_topic.billing_alerts.arn]
  }
}
```

### 5.3 No cost anomaly detection

**Flag:** A Terraform codebase with no `aws_ce_anomaly_monitor` or
`aws_ce_anomaly_subscription` resource.

**Why:** Anomaly detection catches unexpected spend spikes (e.g., a misconfigured ASG
or runaway Lambda) within hours instead of days.

**Recommendation:** Add a Cost Explorer anomaly monitor scoped to the account or a
specific service.

```hcl
resource "aws_ce_anomaly_monitor" "main" {
  name              = "${var.project}-cost-anomaly-monitor"
  monitor_type      = "DIMENSIONAL"
  monitor_dimension = "SERVICE"
}

resource "aws_ce_anomaly_subscription" "alerts" {
  name      = "${var.project}-anomaly-alerts"
  frequency = "DAILY"

  monitor_arn_list = [
    aws_ce_anomaly_monitor.main.arn,
  ]

  subscriber {
    type    = "SNS"
    address = aws_sns_topic.billing_alerts.arn
  }

  threshold_expression {
    dimension {
      key           = "ANOMALY_TOTAL_IMPACT_ABSOLUTE"
      values        = ["100"]
      match_options = ["GREATER_THAN_OR_EQUAL"]
    }
  }
}
```
