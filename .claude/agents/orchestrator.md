# Orchestrator Agent

## Purpose

Top-level agent that manages the full improvement loop. Receives a high-level goal and coordinates all other agents in sequence.

## Actual behavior

Pure dispatch loop — no sequencing logic. Initialises `RunState(goal)`, calls
`decide_next_action(state)` on every iteration, dispatches through `AGENT_REGISTRY`,
and repeats until action == `"done"`. All routing decisions live in
`decide_next_action`.

Routing order: planner → builder → tester → (fixer or import_fixer) →
planner (replan, once) → builder → tester → skill_curator.

## Location

`workflows/improvement_loop.py` — `orchestrator()` and `decide_next_action()`
