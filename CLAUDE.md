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

* goal
* plan type
* executed steps
* failure type
* fixer notes
* attempt count
* completion flags

All agents read and update this object.

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

Reusable skills are stored in the `skills/` directory.

Skills represent **reusable development capabilities**, such as:

* fixing import errors
* adding endpoints
* adding tests
* following repo conventions

Skill files should include:

purpose
trigger conditions
steps to perform
constraints
expected outcome

Agents may consult skills to guide decisions.

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

# Long-Term Direction

Future improvements should focus on:

* making fixers produce actionable repairs
* making builder consume skill content
* improving memory reuse
* demonstrating adaptive behavior

The system should become a **credible minimal agent workflow**, not a theoretical design.

---

# Final Rule

Do not rewrite the project.

Extend it carefully.
