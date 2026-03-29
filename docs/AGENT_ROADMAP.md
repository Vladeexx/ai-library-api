# Agent Improvement Roadmap

This document defines the five workstreams for evolving the agent workflow system in this repository.

Each workstream is independent and can be advanced in small increments. No workstream requires redesigning the system.

---

## Workstream 1 — Agent Loop

**Goal:** Strengthen the state-driven orchestration loop.

**Problem it solves:**
The loop currently has one adaptive branch (`import_error` → `import_fixer`). All other failures route to the generic `fixer` stub. The loop cannot yet select different strategies based on failure history across runs, and the decision function has no way to escalate or de-escalate based on repeated identical failures.

**Expected improvements:**
- Add `lint_fixer` agent and route `lint_error` failures to it
- Detect when the same `failure_type` repeats across all attempts and surface this clearly in `fixer_notes`
- Extract action name strings into `Literal` constants or a small `StrEnum` to catch name mismatches statically
- Allow `decide_next_action` to read `fixer_notes` from prior attempts to vary routing (e.g. skip fixer on second repeat of the same unresolvable error)

---

## Workstream 2 — Memory Usage

**Goal:** Ensure `known_failures.json` and `successful_patterns.json` actively influence agent behavior.

**Problem it solves:**
Memory files are written after every run but rarely consulted. `known_failures.json` is read only by `import_fixer`. `successful_patterns.json` has one manually seeded entry and is never written to by the system. The planner detects prior runs but does not use the content of failure entries to change the plan.

**Expected improvements:**
- `skill_curator` writes to `successful_patterns.json` after successful runs, keyed by `plan_type + skill_used`
- `planner` reads `successful_patterns.json` to select a preferred skill on the first attempt (not only after a prior success for the exact goal)
- `fixer` reads `known_failures.json` to check whether the current `failure_type` has appeared before and includes that count in `fixer_notes`
- Add a `memory_summary` field to `RunState` that any agent can populate with a short note for `skill_curator` to record

---

## Workstream 3 — Skills and Prompts

**Goal:** Transform skill files from static documentation into reusable, repo-aware instructions that agents can act on.

**Problem it solves:**
The builder loads the relevant `.md` skill file from disk (`skill_file.read_text()`) but discards the return value. Skill content has no effect on what the builder does. Skills are currently only useful to a human reading them, not to the system.

**Expected improvements:**
- Parse the `## Conventions to follow` section from the loaded skill file and inject those lines into `executed_steps` so the history reflects skill-guided work
- Add a `skill_hint` field to `RunState` that the builder populates from the skill file and that `import_fixer` can consult
- Expand the `fix_import_error.md` skill file with concrete, repo-specific steps (e.g. "check `alembic/env.py` for missing model imports", "check `tests/conftest.py`") that `import_fixer` can surface in its diagnosis

---

## Workstream 4 — Real Fixer Capability

**Goal:** Make at least one fixer produce actionable repair strategies rather than diagnostic notes only.

**Problem it solves:**
All fixers currently append a note to `fixer_notes` and increment `attempt_number`, but no fixer modifies any file. If tests fail, the system retries with an identical codebase and fails again. The retry loop exhausts attempts without making progress.

**Expected improvements:**
- `import_fixer` reads the `fix_import_error.md` skill file and combines it with `state.test_output` to generate a specific repair instruction (e.g. the exact import line that is missing)
- `import_fixer` writes a structured `suggested_fix` into `RunState` rather than a free-text note, so a future LLM-backed step or human can apply it directly
- Add a `repair_applied: bool = False` field to `RunState` so `decide_next_action` and `skill_curator` can distinguish "fixer ran and diagnosed" from "fixer ran and repaired"
- Eventually: have `import_fixer` attempt a targeted file edit and re-test — this is the step that crosses from diagnosis to real execution capability

---

## Workstream 5 — AI Workflow Quality

**Goal:** Improve the quality and consistency of iterative AI-assisted development practices in this repository.

**Problem it solves:**
Changes are made incrementally but there is no consistent process for verifying that new agent code does not break the invariants the routing logic depends on (e.g. `len(errors) == completed tester runs`). Some agent functions have become more complex and could benefit from lightweight tests. Run history entries from before Phase 3 are missing fields that newer code expects.

**Expected improvements:**
- Add a small `tests/test_workflow.py` file with unit tests for `decide_next_action` covering all routing branches
- Add a unit test for `_classify_failure` covering each failure type
- Backfill missing `failure_type` and `fixer_notes` fields in old `run_history.jsonl` entries with `null` so `.get()` calls are not the only safety net
- Document the `len(errors) == attempt_number` invariant in a dedicated section of `AI_ADVISOR_CONTEXT.md` so future contributors do not accidentally break it
- Add a post-run assertion in the orchestrator (debug mode only) that verifies `RunState` invariants after each agent call
