# Orchestrator Agent

## Purpose

Top-level agent that manages the full improvement loop. Receives a high-level goal and coordinates all other agents in sequence.

## Planned responsibilities

- Parse the incoming goal and delegate to the Planner
- Pass the plan to the Builder for implementation
- Trigger the Tester to validate output
- Route failures to the Fixer for repair
- Signal the Skill Curator to record the outcome

## Status

Scaffold only — not yet implemented.
