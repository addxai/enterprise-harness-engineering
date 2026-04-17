# DDD (Domain-Driven Design) — Decision Card

## When to Use

- Business terminology is confused: the same concept has different names across teams/modules ("order" vs "ticket" vs "request")
- Service boundaries are unclear: uncertain about which logic should be grouped together vs separated
- Multi-team collaboration: need to establish a common language across teams to reduce communication ambiguity
- Complex business rules: the core domain has significant business logic, beyond simple CRUD

## Core Concepts Quick Reference

| Concept | One-Line Explanation | Example Inquiry |
|------|----------|---------|
| **Ubiquitous Language** | Business and tech use the same terminology, eliminating translation layers | "What does product call this concept? What does the code call it? Are they the same?" |
| **Bounded Context** | A term has a clear meaning only within one context; cross-context use requires translation | "Are these two modules referring to the same 'user' concept?" |
| **Aggregate** | A group of objects that must maintain consistency, accessed through the Aggregate Root | "Which data must be modified together in this operation to maintain consistency?" |
| **Domain Event** | Something business-meaningful has occurred | "After this operation completes, who needs to know about it?" |
| **Anti-Corruption Layer** | Prevents an external model from polluting the internal domain model | "After integrating this external system, does our model need to conform to theirs?" |

## Relationship to This Skill

- `domain-model.md` is the concrete implementation of Ubiquitous Language
- The boundary-drawing questions in Step 2 are essentially Bounded Context identification
- In Step 4 module design, the Aggregate definition determines transaction boundaries

## When NOT to Use

- Simple CRUD applications with thin business logic
- Prototype/MVP phase where the business model is still rapidly evolving; fixing context boundaries too early hinders exploration
- Team has only 1-2 people and communication cost is already low
