# State Machine — Decision Card

## When to Use

- Entity has a clear lifecycle: device (offline -> online -> upgrading -> online), order (pending payment -> paid -> shipped -> completed)
- State transitions have rules: not all states can reach all states (a cancelled order cannot become shipped)
- Concurrent state changes: multiple requests may simultaneously attempt to change the same entity's state
- Bugs are frequent in state-related logic: implicit state management (a pile of if/else) leads to illegal states

## Core Concepts Quick Reference

| Concept | One-Line Explanation | Example Inquiry |
|------|----------|---------|
| **State** | The entity's condition at a given moment | "What are all the possible states for this entity? Can you draw a complete list?" |
| **Transition** | A change from one state to another | "From state A, which states can be reached? Which cannot?" |
| **Guard Condition** | The prerequisite for a transition to occur | "What conditions must be met for this transition to be allowed?" |
| **Side Effect** | Operations triggered when a transition occurs | "After the state changes, who needs to be notified? What needs to be triggered?" |
| **Concurrency Control** | What happens when two requests change state simultaneously | "If two requests simultaneously trigger different transitions, which one wins?" |

## Design Checklist

1. **Are all states exhaustively listed?** Draw a state diagram and confirm nothing is missing
2. **How are illegal transitions handled?** Silently ignored? Error thrown? Logged?
3. **Are terminal states reversible?** Are cancelled/deleted truly irreversible?
4. **How are timeout states handled?** If "upgrading" for more than 30 minutes with no response, auto-rollback?

## Relationship to This Skill

- In the Step 2 User Story pattern recognition table, "order/ticket/device lifecycle" points directly to this card
- In Step 4 module design, entities with state must explicitly define a state machine

## When NOT to Use

- Entity has only two states (active/inactive): a boolean is sufficient
- State transitions have no rules: any state can reach any other state, no state machine needed
- State is entirely controlled by an external system: this system only mirrors the display, with no transition logic
