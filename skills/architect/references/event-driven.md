# Event-Driven Architecture — Decision Card

## When to Use

- Cross-service coordination: when A completes, B, C, and D all need to respond, but A does not need to wait for them
- State change notifications: events like service coming online, order payment, or software upgrade completion need to be broadcast
- Traffic smoothing: burst traffic needs buffering so downstream consumers can process at their own rate
- Audit trail: need to record a complete timeline of "what happened"

## Core Concepts Quick Reference

| Concept | One-Line Explanation | Example Inquiry |
|------|----------|---------|
| **Event Sourcing** | Instead of storing final state, store all change events; state is rebuilt by replaying events | "Do we need to know 'how we got to the current state' or just 'what the current state is'?" |
| **CQRS** | Separate read and write models, optimize each independently | "Are the read and write patterns significantly different? Do queries need to assemble data across multiple aggregates?" |
| **Saga / Orchestration vs Choreography** | Coordination approach for cross-service long-running transactions. Orchestration: central controller. Choreography: each service listens to events and responds independently | "How many steps does this flow have? Do we need a single place to see the overall progress?" |
| **Dead Letter Queue (DLQ)** | Where messages go when consumption fails | "What happens to events that fail to be consumed? Drop? Retry? Manual intervention?" |
| **Idempotent Consumption** | Consuming the same event multiple times produces the same result | "If this event is delivered twice, what happens?" |

## Relationship to This Skill

- The "integration patterns" inquiry in Step 2 directly relates to the sync vs async decision in this pattern
- When User Story mentions "notification", "push", "async", or "eventual consistency", reference this card for evaluation

## When NOT to Use

- Strong consistency requirements: operations like transfers need immediate confirmation; eventual consistency from event-driven does not suffice
- Simple request-response: A calls B to get a result with no broadcast needs; synchronous calls are simpler
- Unacceptable debugging complexity: event-driven makes issue tracing harder; use with caution if the team lacks distributed tracing infrastructure
