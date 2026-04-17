# Multi-Tenant Patterns — Decision Card

## When to Use

- OEM / white-label products: the same system serves multiple brand customers, each with customization needs
- SaaS multi-tenancy: multiple organizations share infrastructure, requiring data and configuration isolation
- Large configuration differences between tenants: not just swapping a logo, but potentially different business processes
- Fault isolation requirements: one tenant's anomaly must not affect other tenants

## Core Concepts Quick Reference

| Concept | One-Line Explanation | Example Inquiry |
|------|----------|---------|
| **Data Isolation Level** | Shared database -> shared schema with row-level isolation -> separate schema -> separate database | "How significant is the risk of data leakage between tenants? What are the compliance requirements?" |
| **Configuration Routing** | Load different configurations/policies based on tenant ID | "Are the differences between tenants at the parameter level (changing thresholds) or the process level (changing steps)?" |
| **Tenant Context Propagation** | Always carry tenant identification throughout the request chain | "At every layer in the call chain, can we tell which tenant the current request belongs to?" |
| **Resource Limiting** | Prevent a single tenant from consuming excessive resources and affecting others | "If one tenant suddenly has 10x traffic, will other tenants slow down?" |
| **Tenant Lifecycle** | Provisioning, configuration, suspension, and deactivation of tenants | "How long does it take to onboard a new tenant? What manual operations are required?" |

## Isolation Level Selection

| Isolation Level | Pros | Cons | Applicable Scenarios |
|---------|------|------|---------|
| Row-level isolation (shared tables) | Lowest cost, simple operations | Weak isolation, queries must always include tenant_id | Large number of tenants, low data sensitivity |
| Schema isolation | Moderate isolation, migrations can be per-tenant | Connection pool management is complex | Moderate number of tenants, some isolation needed |
| Separate databases | Complete isolation, independent scaling | High cost, complex operations | Large customers, high compliance requirements, sensitive data |

## Relationship to This Skill

- In Step 2 User Story pattern recognition, "multi-tenant/OEM/white-label" points directly to this card
- Multi-tenant configuration routing design is a common scenario in Step 4 module design
- Tenant context propagation affects cross-cutting concerns throughout the architecture

## When NOT to Use

- Single-tenant system: serves only one organization, no isolation needed
- Tenants are completely identical: no customization requirements, no tenant routing logic needed
- Very few and fixed tenants (2-3): separate deployments may be simpler than multi-tenant architecture
