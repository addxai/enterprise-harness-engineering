# Integration Patterns — Decision Card

## When to Use

- Integrating with third-party APIs: payment (Stripe/Airwallex), messaging (Feishu/Slack), cloud services
- External systems are unreliable: third parties have downtime, rate limits, and slow responses
- External model does not match internal model: the third party's data structure differs significantly from your domain model
- Multiple external systems provide similar capabilities: need a unified abstraction (e.g., multiple payment channels)

## Core Concepts Quick Reference

| Concept | One-Line Explanation | Example Inquiry |
|------|----------|---------|
| **Anti-Corruption Layer (ACL)** | Add a translation layer between the external system and internal model to prevent external model invasion | "After integrating this API, does our code need to use its data format everywhere?" |
| **Circuit Breaker** | Fail fast when downstream is faulty to prevent cascading failures | "If this external service is down for 5 minutes, what happens to our system?" |
| **Retry + Backoff** | Automatically retry transient failures with exponential backoff to avoid retry storms | "If this call fails, is it safe to retry? Could it cause duplicate operations?" |
| **Idempotency Key** | Ensure duplicate requests produce only one effect | "If the user clicks the pay button twice, will they be charged twice?" |
| **Timeout + Fallback** | Degradation strategy after an external call times out | "When the call times out, what does the user see? Is there a cache we can use?" |
| **Reconciliation** | Periodically compare data between two systems to detect inconsistencies | "If a callback is lost, how do we discover this transaction's status is inconsistent?" |

## Relationship to This Skill

- The "integration patterns" inquiry in Step 2 directly relates to this card
- In Step 4, any module depending on external services needs to evaluate these patterns
- Works together with hexagonal architecture: ACL = the Driven Adapter's responsibility

## When NOT to Use

- Calling internal controllable services: internal services have high reliability and model consistency, no need for heavy-duty isolation
- Prototype phase with only one external API: direct calls are faster; abstract when a second one is needed
