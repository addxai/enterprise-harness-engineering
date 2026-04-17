# Terraform Audit Report: {project_name}

**Date:** {date} | **Auditor:** {auditor} | **Scope:** {scope}

## Executive Summary

| Severity | Count |
|----------|-------|
| Critical | {critical_count} |
| Important | {important_count} |
| Minor | {minor_count} |

**Overall Assessment:** {PASS | NEEDS ATTENTION | CRITICAL ISSUES}

**Priority Actions:**
1. {priority_action_1}
2. {priority_action_2}
3. {priority_action_3}

---

## 1. Security & Compliance

### Critical
{issue_block}
### Important
{issue_block}
### Minor
{issue_block}

## 2. Cost Optimization

### Critical
{issue_block}
### Important
{issue_block}
### Minor
{issue_block}

## 3. Code Quality

### Critical
{issue_block}
### Important
{issue_block}
### Minor
{issue_block}

## 4. Architecture Design

### Critical
{issue_block}
### Important
{issue_block}
### Minor
{issue_block}

---

### Issue Format

Each `{issue_block}` above follows this template (repeat per finding):

- **Location:** `{file}:{line}`
- **Resource:** `{resource_type}.{resource_name}`
- **Problem:** {description}
- **Risk:** {risk_explanation}
- **Fix:**
  ```hcl
  {suggested_hcl_fix}
  ```
- **Reference:** {link_or_standard}

If no issues exist for a subsection, write: *No issues found.*

---

## Action Items

| # | Task | Severity | Effort | Owner |
|---|------|----------|--------|-------|
| 1 | {task_description} | Critical | {hours}h | {owner} |
| 2 | {task_description} | Important | {hours}h | {owner} |
| 3 | {task_description} | Minor | {hours}h | {owner} |

---

## Appendix

- **Files Scanned:** {file_list}
- **Modules Analyzed:** {module_list}
- **Audit Criteria Version:** {criteria_version}