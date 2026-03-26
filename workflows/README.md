# Workflows

This directory contains orchestration scripts for the agent-based improvement loop.

## Files

| File | Purpose |
|------|---------|
| `improvement_loop.py` | Entry point that will orchestrate the full agent pipeline |

## Planned pipeline

```
goal → Planner → Builder → Tester → (pass) → Skill Curator
                                  ↘ (fail) → Fixer → Tester → Skill Curator
```

## Status

Scaffold only — not yet implemented.
