# AWS Architecture Review Checklist for Terraform

Scope: high availability, disaster recovery, network design, environment isolation, scalability.
Out of scope: security hardening and cost optimization (separate skill files).

## Table of Contents

1. [High Availability](#1-high-availability)
2. [Disaster Recovery](#2-disaster-recovery)
3. [Network Design](#3-network-design)
4. [Environment Isolation](#4-environment-isolation)
5. [Scalability](#5-scalability)

---

## 1. High Availability

### 1.1 EC2/ECS deployed to a single Availability Zone

**Check:** Instances or ECS tasks provisioned in only one AZ or referencing a single subnet.
**Risk:** A single AZ outage takes down the entire workload.
**Recommendation:** Spread across at least two AZs using multiple subnets.

```hcl
resource "aws_autoscaling_group" "app" {
  vpc_zone_identifier = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id,
    aws_subnet.private_c.id,
  ]
}
```

### 1.2 Load balancer without cross-zone load balancing

**Check:** `aws_lb` or `aws_elb` with `enable_cross_zone_load_balancing` absent or `false`.
**Risk:** Uneven traffic distribution causes hot spots and partial outages when one AZ degrades.
**Recommendation:** Set `enable_cross_zone_load_balancing = true` on every ALB/NLB.

### 1.3 RDS without Multi-AZ in production

**Check:** `aws_db_instance` where `multi_az = false` or missing in a production context.
**Risk:** No standby replica; failover requires a full restore from snapshot.
**Recommendation:** Set `multi_az = true` for every production database. Note: for non-production environments, Multi-AZ may be an unnecessary cost (see cost optimization review).

### 1.4 Missing health checks on target groups

**Check:** `aws_lb_target_group` without a `health_check` block, or TCP-only when the service speaks HTTP.
**Risk:** Unhealthy targets keep receiving traffic.
**Recommendation:** Define an HTTP/HTTPS health check with an explicit path and realistic thresholds.

```hcl
resource "aws_lb_target_group" "app" {
  health_check {
    path                = "/healthz"
    protocol            = "HTTP"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
    timeout             = 5
  }
}
```

### 1.5 Auto Scaling min_size equals max_size

**Check:** `aws_autoscaling_group` where `min_size == max_size`, disabling scaling.
**Risk:** Cannot respond to load increases or replace failed instances beyond the fixed count.
**Recommendation:** Set `max_size` above `min_size` and attach a scaling policy. Document if a fixed fleet is intentional.

---

## 2. Disaster Recovery

### 2.1 No AWS Backup plan

**Check:** No `aws_backup_plan` or `aws_backup_selection` for stateful resources (RDS, EBS, EFS, DynamoDB).
**Risk:** Recovery depends on ad-hoc snapshots or manual intervention.
**Recommendation:** Create a tag-based backup plan covering every stateful resource.

```hcl
resource "aws_backup_plan" "daily" {
  name = "daily-backup"
  rule {
    rule_name         = "daily"
    target_vault_name = aws_backup_vault.main.name
    schedule          = "cron(0 3 * * ? *)"
    lifecycle { delete_after = 30 }
  }
}

resource "aws_backup_selection" "tagged" {
  iam_role_arn = aws_iam_role.backup.arn
  name         = "tagged-resources"
  plan_id      = aws_backup_plan.daily.id
  selection_tag {
    type = "STRINGEQUALS"
    key  = "Backup"
    value = "true"
  }
}
```

### 2.2 RDS backup retention period set to zero

**Check:** `aws_db_instance` with `backup_retention_period = 0`.
**Risk:** Automated snapshots disabled; point-in-time restore impossible.
**Recommendation:** At least 7 days (non-prod) or 14-35 days (prod).

### 2.3 S3 cross-region replication missing for critical data

**Check:** Critical S3 buckets lacking `aws_s3_bucket_replication_configuration`.
**Risk:** A regional outage or accidental deletion has no secondary copy.
**Recommendation:** Enable cross-region replication to a geographically separate region.

### 2.4 DynamoDB without point-in-time recovery

**Check:** `aws_dynamodb_table` without `point_in_time_recovery { enabled = true }`.
**Risk:** Accidental writes or deletes cannot be rolled back without external backups.
**Recommendation:** Enable PITR on every DynamoDB table.

### 2.5 No documented RTO/RPO

**Check:** No variables, locals, or comments referencing Recovery Time/Point Objective values.
**Risk:** Cannot verify backup frequency and restore procedures meet business requirements.
**Recommendation:** Define RTO/RPO as Terraform locals or variable descriptions, version-controlled with infra.

---

## 3. Network Design

### 3.1 VPC CIDR too small for production

**Check:** `aws_vpc` with CIDR smaller than `/20` (fewer than 4,096 addresses) in production.
**Risk:** IP exhaustion blocks new subnets, ENIs, or peering as the workload grows.
**Recommendation:** Use at least `/16` for production VPCs; plan for future growth and peering.

### 3.2 Missing subnet tiers

**Check:** Only one subnet tier instead of distinct public, private, and isolated layers.
**Risk:** Databases and internal services on unnecessarily internet-routable paths.
**Recommendation:** Three tiers: public (IGW), private (NAT), isolated (no internet).

```hcl
# Public  - ALBs, NAT gateways
# Private - app instances, ECS tasks (route via NAT)
# Isolated - RDS, ElastiCache (no internet route)
resource "aws_route_table" "isolated" {
  vpc_id = aws_vpc.main.id
  # Intentionally no route to NAT or IGW
}
```

### 3.3 No Network ACLs beyond defaults

**Check:** No custom `aws_network_acl` resources; all subnets use the default allow-all NACL.
**Risk:** No subnet-level defense-in-depth; a security group misconfiguration has no guard.
**Recommendation:** Add NACLs restricting traffic between tiers, blocking direct internet to isolated subnets.

### 3.4 Missing transit gateway for multi-VPC

**Check:** Multiple VPCs connected via individual peering instead of `aws_ec2_transit_gateway`.
**Risk:** Peering does not scale; each new VPC needs O(n) new connections.
**Recommendation:** Use a transit gateway when three or more VPCs exist or growth is anticipated.

### 3.5 Route 53 health checks for failover routing

**Check:** `aws_route53_record` with `failover_routing_policy` but no `aws_route53_health_check`.
**Risk:** Failover records without health checks never trigger.
**Recommendation:** Attach a health check to every primary failover record.

---

## 4. Environment Isolation

### 4.1 Shared Terraform state across environments

**Check:** Single S3 backend key or local state file used for both prod and non-prod.
**Risk:** A mistaken `terraform apply` in dev can destroy production infrastructure.
**Recommendation:** Separate state per environment via workspaces, directory structure, or distinct backend keys.

```hcl
# envs/prod/backend.tf
terraform {
  backend "s3" {
    bucket = "tfstate-prod"
    key    = "infra/terraform.tfstate"
    region = "<region>"
  }
}
```

### 4.2 Same AWS account for prod and non-prod

**Check:** No `aws_organizations_account`, no provider aliases with different `assume_role`, no variable-driven account IDs.
**Risk:** Blast radius in dev (broad IAM policy, runaway script) can impact production.
**Recommendation:** Separate AWS accounts per environment via AWS Organizations with cross-account deploy roles.

### 4.3 Hardcoded environment values

**Check:** Strings like `"prod"` or `"staging"` in resource arguments instead of a variable.
**Risk:** Environment logic is scattered; promotion between environments requires manual edits.
**Recommendation:** Derive all environment-dependent values from a single `var.environment` input.

### 4.4 Missing workspace or directory-based separation

**Check:** One flat directory with no workspaces, no `envs/` structure, no Terragrunt config.
**Risk:** All environments share configuration surface, increasing accidental cross-env changes.
**Recommendation:** Directory-per-environment (`envs/dev`, `envs/prod`) or workspaces with `.tfvars` per env.

---

## 5. Scalability

### 5.1 Auto Scaling without scale-in cooldown

**Check:** `aws_autoscaling_policy` missing `cooldown` or `estimated_instance_warmup`, or `default_cooldown = 0`.
**Risk:** Aggressive scale-in removes instances before they finish draining.
**Recommendation:** Cooldown at least 300s; set `estimated_instance_warmup` on target-tracking policies.

```hcl
resource "aws_autoscaling_policy" "scale_out" {
  autoscaling_group_name    = aws_autoscaling_group.app.name
  policy_type               = "TargetTrackingScaling"
  estimated_instance_warmup = 300
  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 60.0
  }
}
```

### 5.2 Missing connection draining on load balancers

**Check:** `aws_lb_target_group` with `deregistration_delay = 0`, or `aws_elb` with `connection_draining = false`.
**Risk:** In-flight requests dropped when instances deregister during scale-in or deployment.
**Recommendation:** Set `deregistration_delay` to at least 30s (default 300); tune to longest expected request.

### 5.3 Hardcoded resource counts

**Check:** Literal integers in `count` or `desired_capacity` instead of variables.
**Risk:** Scaling requires code changes and a full apply cycle rather than a variable override.
**Recommendation:** Use variables for all capacity arguments; adjust per environment via `.tfvars`.

### 5.4 Missing CloudWatch alarms for scaling triggers

**Check:** Auto Scaling groups with no `aws_cloudwatch_metric_alarm` and no target-tracking policy.
**Risk:** Infrastructure cannot react to load changes; scaling is entirely manual.
**Recommendation:** Create alarms or target-tracking policies for CPU, memory, request count, or queue depth.

```hcl
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "high-cpu-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 120
  statistic           = "Average"
  threshold           = 70
  dimensions          = { AutoScalingGroupName = aws_autoscaling_group.app.name }
  alarm_actions       = [aws_autoscaling_policy.scale_out.arn]
}
```

---

## How to Use This Checklist

1. Flag each finding by section number (e.g., "1.3 RDS without Multi-AZ").
2. Rate severity: **Critical** (outage risk), **Important** (degraded reliability), **Minor** (operational friction).
3. Group findings by category in the audit report.
4. Provide the HCL recommendation or a project-specific variant.
5. Note items intentionally not applicable and document justification.
