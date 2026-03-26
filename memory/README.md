# Memory

This directory stores persistent context for the agent improvement loop.

## Files

| File | Purpose |
|------|---------|
| `run_history.jsonl` | Append-only log of each improvement cycle (one JSON object per line) |
| `known_failures.json` | Map of recurring failure patterns to their known fixes |
| `successful_patterns.json` | Map of approaches that have worked reliably in this codebase |
| `repo_conventions.md` | Human-readable summary of project conventions the Builder must follow |

## Status

Scaffold only — files are initialized with empty structures. Content will be populated by the Skill Curator agent as the improvement loop runs.
