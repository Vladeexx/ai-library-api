# AI Library API - Claude Instructions

This repository contains a backend API for managing books and recommendations.

## Technology Stack

- Python 3.11
- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy
- Alembic
- Docker
- pytest

## Project Structure

app/
- api/ → API routes
- models/ → database models
- services/ → business logic
- core/ → configuration and shared utilities

tests/
- unit and integration tests

infra/
- infrastructure (Terraform / cloud deployment)

## Coding Guidelines

- Keep code modular and clean
- Use type hints
- Follow FastAPI best practices
- Use environment variables for configuration
- Separate API routes from business logic

## Tasks Claude May Perform

Claude may:
- generate FastAPI endpoints
- create SQLAlchemy models
- write tests
- update Docker configuration
- improve documentation

Claude should:
- explain major architectural decisions
- keep changes minimal and focused
- avoid unnecessary complexity

# AI Development Context for This Repository

## Project Purpose

This repository contains a lightweight experimental **agent-driven improvement system** for a backend API project.

The goal of the system is to demonstrate a **state-driven agent workflow** that can:

* plan tasks
* build code changes
* run tests
* classify failures
* attempt fixes
* retry work
* record memory from previous runs

The system is intentionally **simple and educational**, not a production autonomous coding agent.

The objective is to evolve the workflow gradually so that agents become **more useful over time through memory and reusable skills**.

---

# Core Design Principles

When modifying this repository, follow these rules strictly:

1. **Keep everything lightweight**

   * No external frameworks
   * Plain Python only
   * Avoid heavy abstractions

2. **Prefer incremental improvements**

   * Modify existing code instead of rewriting systems
   * Add small capabilities one at a time

3. **Do not redesign the whole architecture**

   * Extend the current structure
   * Maintain compatibility with existing files

4. **Favor clarity over cleverness**

   * Code should be easy to read and reason about
   * Avoid magic or hidden behavior

---

# Current Agent Architecture

The system implements a **state-driven agent loop**.

Agents operate on a shared state object.

Example flow:

Goal
↓
Planner
↓
Builder
↓
Tester
↓
Failure classification
↓
Fixer
↓
Retry loop
↓
Memory recorded

The orchestrator determines the next step dynamically.

---

# Core Components

## RunState

A shared state object that contains:

* goal, plan, plan_version
* selected_skill, skills_applied, skill_notes, pattern_hint
* executed_steps, build_complete
* test_passed, test_output, failure_type, errors
* fixer_notes, suggested_fix, repair_applied, repair_summary
* replanned, last_failure_summary
* final_status

All agents read and update this object. `plan_version` increments on every planner call (1 = initial, 2+ = replan). `replanned` gates post-failure replanning to once per run.

---

## Orchestrator

The orchestrator drives the system through a **decision loop**.

Pseudo-flow:

while not finished:

```
action = decide_next_action(state)

dispatch(action)

update_state()

if max_attempts_reached:
    stop
```

The orchestrator must remain **simple and readable**.

---

## Agents

The system contains several specialized agents.

Planner
Determines what steps should be executed.

Builder
Executes the planned work (code generation or repo modifications).

Tester
Runs the real test suite.

Fixer
Analyzes failures and proposes repair strategies.

Skill Curator
Records useful knowledge from successful runs.

Agents should remain **small functions**, not complex frameworks.

---

# Memory System

The system records structured memory in the `memory/` directory.

## Files

run_history.jsonl
Stores execution history for each run.

known_failures.json
Stores classified failures and related diagnostics.

successful_patterns.json
Stores patterns that led to successful outcomes.

---

# Skills System

Reusable skills live in `.claude/skills/coding/` and `.claude/skills/operational/`.

Each skill file uses this structured format:

```
## Purpose     — one-line description (prose, not parsed)
## Trigger     — bullet list of match conditions (parsed by planner)
## Steps       — bullet list of ordered actions (consumed by builder)
## Conventions — bullet list of repo rules (stored in skill_notes)
## Constraints — bullet list of things to avoid (stored in skill_notes)
```

**Trigger bullets** use two parseable forms:
- `Goal contains "X"` — scores 1 if any quoted keyword appears in the goal
- `failure_type == "X"` — scores 2 if failure_type matches exactly

Planner selects skills using a four-level priority chain:
1. Exact goal match in `run_history.jsonl`
2. Plan-type match in `successful_patterns.json`
3. Trigger-based match across all skill files (highest score wins)
4. Hardcoded `SKILL_MAP` fallback in builder

Builder reads `## Steps`, `## Conventions`, and `## Constraints` from the selected skill file and appends them to `executed_steps` and `skill_notes`.

---

# Important Constraints

When modifying the repository:

DO NOT

* introduce large frameworks
* convert the project to a complex agent platform
* add unnecessary dependencies
* redesign the entire workflow

DO

* keep improvements incremental
* explain reasoning before making large changes
* maintain compatibility with existing structure

---

# Development Philosophy

This repository is intended to demonstrate how an agent system can evolve from:

1. fixed pipeline
2. state-driven workflow
3. adaptive loop
4. memory-informed behavior
5. skill-based improvements

The goal is **clear evolution**, not instant complexity.

---

# Preferred Change Process

When implementing improvements:

1. Inspect the current code.
2. Identify the smallest meaningful improvement.
3. Explain what files will change.
4. Implement changes incrementally.
5. Summarize what improved.
6. Identify what still remains stubbed.

---

# Current Implementation Status

The following is **fully implemented** in `workflows/improvement_loop.py`:

* State-driven dispatch loop (`orchestrator` + `decide_next_action`)
* Four-priority skill selection in `planner`
* Trigger-based skill matching with weighted scoring
* Builder consuming `## Steps`, `## Conventions`, `## Constraints` from skill files
* Prior successful `skill_notes` reuse across runs
* Import error fixer with structured patch proposals and safety-gated auto-repair
* Post-failure replanning (`plan_version`, `replanned`, `last_failure_summary`)
* `successful_patterns.json` written on success and consulted on next run
* `known_failures.json` written on failure
* `run_history.jsonl` append-only run log

The following remains **stubbed or limited**:

* `builder` logs and records steps but does not write files — changes must still be made by Claude Code directly
* `fixer` is a placeholder for non-import failures — only `import_fixer` is fully implemented
* Operational skills (`run_tests.md`, `run_migrations.md`, `inspect_api_logs.md`) are documentation only

---

# How to Run the Improvement Loop

```bash
python workflows/improvement_loop.py "add books CRUD endpoint"
python workflows/improvement_loop.py "add migration for authors table"
python workflows/improvement_loop.py "add tests for the reviews endpoint"
```

The loop will plan, build (record steps), run `make test`, classify failures, replan if needed, and record memory. Exit code 0 = success, 1 = failed after all attempts.

To inspect memory after a run:
```bash
tail -1 memory/run_history.jsonl | python3 -m json.tool
cat memory/successful_patterns.json
cat memory/known_failures.json
```

---

# Long-Term Direction

The system is a credible minimal agent workflow. Next meaningful improvements:

* Connect builder to real file writes (currently logs steps only)
* Implement a real `fixer` for `test_failure` type (beyond the skill hint)
* Add skill_curator pattern curation — propose new skills from repeated successful runs
* Expand trigger vocabulary to support `plan_type ==` matching

---

# Final Rule

Do not rewrite the project.

Extend it carefully.
