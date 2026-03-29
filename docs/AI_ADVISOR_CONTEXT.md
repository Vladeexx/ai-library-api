# AI Advisor Context

## Purpose

This repository contains a lightweight, experimental **agent-driven improvement system** built on top of a standard FastAPI backend.

The backend itself (books CRUD API, PostgreSQL, Redis, Alembic) is a real, working application. The agent workflow system layered on top of it is an evolving experiment in how AI-assisted development tooling can be structured incrementally — starting from a fixed script and growing toward an adaptive, memory-informed agent loop.

The system is **intentionally simple and educational**. It is not a production autonomous coding agent.

---

## Current Maturity Level

The system recently crossed from a fixed pipeline into a **baseline agent loop with early adaptive routing**.

Specifically:
- The orchestrator no longer has a hardcoded execution sequence. It dispatches dynamically via `decide_next_action(state)`.
- The system has a real retry cycle (up to `MAX_ATTEMPTS` attempts).
- Tester failure output is classified into structured `failure_type` values.
- A dedicated `import_fixer` agent is routed to when `failure_type == "import_error"`.
- `import_fixer` reads prior failure memory and produces a contextual diagnosis.
- Every run is recorded to persistent memory (`run_history.jsonl`, `known_failures.json`).

**Honest assessment:** the control plane exists and is well-structured. Execution capability is still weak — fixers diagnose failures but do not yet repair them. The system can observe, classify, and record, but cannot reliably act.

---

## Architecture

### RunState

`RunState` is a shared dataclass passed through every agent. It holds all workflow state:

- `goal` — the task being worked on
- `plan` / `plan_type` — output from the planner
- `build_complete` — whether the builder has finished
- `selected_skill` — which skill the builder used
- `executed_steps` — ordered log of what happened
- `test_passed` / `test_output` — tester results
- `errors` — one entry per failed tester run (invariant relied on by routing logic)
- `failure_type` — classified failure from the most recent tester run
- `fixer_notes` — diagnosis written by whichever fixer ran
- `attempt_number` — current retry attempt (incremented by fixers)
- `final_status` — `"success"` or `"failed"`, set by skill_curator

No agent communicates through any mechanism other than reading and writing `RunState`.

### Orchestrator

The orchestrator is a pure dispatch loop:

```
state = RunState(goal=goal)
while True:
    action = decide_next_action(state)
    if action == "done":
        break
    state = AGENT_REGISTRY[action](state)
```

All sequencing logic lives in `decide_next_action`. The orchestrator contains no per-agent conditionals.

### Agents

| Agent | Role | Status |
|-------|------|--------|
| `planner` | Selects plan type and steps based on goal keywords and run history | Working — reads history, detects prior failures |
| `builder` | Executes plan steps and loads skill file from disk | Partial stub — loads skill file but does not consume its content |
| `tester` | Runs `make test`, captures output, classifies failure type | Fully working |
| `fixer` | Generic failure handler | Stub — logs and increments attempt |
| `import_fixer` | Import-specific failure handler | Early capability — reads failure memory, produces diagnosis |
| `skill_curator` | Records run outcome to persistent memory | Working |

### Agent Registry

`AGENT_REGISTRY` is a `dict[str, Callable[[RunState], RunState]]` mapping agent names to functions. `decide_next_action` returns a name; the orchestrator looks it up and calls it. Adding a new agent requires one function and one registry entry.

### Decision Function

`decide_next_action(state)` is a priority-ordered chain:

1. No plan yet → `planner`
2. Build not done → `builder`
3. Final status already set → `done`
4. Tests passed → `skill_curator`
5. Tester has not run this attempt → `tester`
6. Tests failed, retries remain, `import_error` → `import_fixer`
7. Tests failed, retries remain, other → `fixer`
8. Retries exhausted → `skill_curator`

---

## Memory System

Memory files live in `memory/`:

- `run_history.jsonl` — append-only log of every run, including `failure_type`, `fixer_notes`, `skill_used`, and outcome
- `known_failures.json` — list of structured failure entries written by `skill_curator` on failed runs; read by `import_fixer`
- `successful_patterns.json` — patterns from successful runs; currently has one manually seeded entry
- `repo_conventions.md` — human-readable project conventions for agents to follow

### Current gap

`known_failures.json` is written and read. `successful_patterns.json` is seeded but not yet written to by `skill_curator` after successful runs — it does not grow automatically.

---

## Skills System

Skill files live in `.claude/skills/coding/` and `.claude/skills/operational/`. Each is a markdown file describing a reusable development capability.

The builder currently loads the relevant skill file from disk but discards the content. Skill files are documentation only at this stage — they are not yet interpreted or executed by any agent.

---

## Current Limitations

1. **Fixers do not modify files.** Diagnosis is produced but no repair is applied to the codebase. If tests fail, the retry cycle runs, fixers write notes, but the underlying problem is never fixed.

2. **Builder ignores skill content.** Skill `.md` files are loaded but not read. The builder executes step labels from the plan, not instructions from the skill.

3. **`successful_patterns.json` does not grow.** `skill_curator` does not write to it on success. The pattern memory is static.

4. **Planner's `"review previous failure"` step is decorative.** When a prior failure is detected, a step label is inserted into the plan, but the builder does not act on it differently.

5. **`fixer` (generic) is a complete stub.** It logs, appends a step, and increments the attempt counter. Only `import_fixer` does something meaningful.

---

## Development Philosophy

- **Plain Python only.** No external agent frameworks, no LLM API calls inside the workflow script itself.
- **Incremental improvements.** Each change adds one small capability without redesigning the system.
- **Clarity over cleverness.** Code should be readable without knowing the full history of changes.
- **The test suite is the ground truth.** `tester` runs `make test` — real subprocess, real exit code, real output.

---

## Strategic Direction

The system should evolve through these stages:

1. Fixed pipeline ✓ (completed)
2. State-driven agent loop ✓ (completed)
3. Adaptive routing based on failure classification ✓ (in progress)
4. Memory-informed behavior — agents consult history to change what they do
5. Skill-based execution — builder uses skill file content to guide real code changes
6. Actionable fixers — at least one fixer modifies the codebase to repair a failure

The goal is a **credible minimal agent workflow**, not a theoretical design or a heavyweight platform.
