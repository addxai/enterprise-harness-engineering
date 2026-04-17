# Hexagonal Architecture (Ports & Adapters) — Decision Card

## When to Use

- Multiple external integrations: the same core logic needs to interface with multiple external systems (Stripe + Airwallex + Apple Pay)
- High testability requirements: need to test core business logic without depending on external services
- External systems may be replaced: using Redis today, might switch to DynamoDB tomorrow, without changing core code
- Prevent framework lock-in: core logic should not know whether it runs on Express/Spring/Flask

## Core Concepts Quick Reference

| Concept | One-Line Explanation | Example Inquiry |
|------|----------|---------|
| **Port** | Interface defined by the core domain ("what capabilities do I need") | "What external capabilities does this module need? Storage? Notifications? Payment?" |
| **Adapter** | Concrete implementation of a Port ("who provides this capability") | "Who provides this capability now? Might it change in the future?" |
| **Driving Adapter** | External calls coming in (HTTP Controller, message consumer) | "What entry points trigger this business logic?" |
| **Driven Adapter** | Core calls going out (database, third-party API) | "After the core logic completes, what external systems need to be called?" |
| **Dependency Direction** | All dependencies point toward the core domain; the core does not depend on any external implementation | "If we remove this external dependency, can the core logic still compile?" |

## Relationship to This Skill

- The "dependency direction" check in Step 4 is essentially verifying hexagonal architecture dependency rules
- When User Story involves multiple third-party integrations, recommend using Port/Adapter for isolation

## When NOT to Use

- Only one external dependency that is unlikely to change: over-abstraction adds unnecessary complexity
- Script/utility projects: one-time execution, no long-term maintenance needed
- Team is unfamiliar with this pattern and under delivery pressure: learning cost may exceed the benefit
