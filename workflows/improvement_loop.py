"""
improvement_loop.py
-------------------
Minimal runnable agent improvement loop.

Orchestrates the pipeline:
    orchestrator → planner → builder → tester → (fixer) → skill_curator

Usage:
    python workflows/improvement_loop.py "add books CRUD endpoint"
"""

import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------

@dataclass
class RunState:
    goal: str
    attempt_number: int = 1
    plan: dict = field(default_factory=dict)
    selected_skill: Optional[str] = None
    build_complete: bool = False
    executed_steps: list[str] = field(default_factory=list)
    test_passed: bool = False
    test_output: str = ""
    # One entry is appended per failed tester run. decide_next_action depends
    # on len(errors) == number of completed tester runs to route correctly.
    errors: list[str] = field(default_factory=list)
    fixer_notes: str = ""
    failure_type: str = ""
    final_status: Optional[str] = None


MEMORY_DIR = Path(__file__).parent.parent / "memory"
RUN_HISTORY = MEMORY_DIR / "run_history.jsonl"
KNOWN_FAILURES_FILE = MEMORY_DIR / "known_failures.json"
SUCCESSFUL_PATTERNS_FILE = MEMORY_DIR / "successful_patterns.json"
TEST_COMMAND = "make test"
MAX_ATTEMPTS = 3


# ---------------------------------------------------------------------------
# Logging helper
# ---------------------------------------------------------------------------

def log(agent: str, message: str) -> None:
    print(f"[{agent}] {message}")


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------


def _load_json_file(path: Path) -> dict:
    """Load a JSON file, returning an empty dict on any error."""
    try:
        text = path.read_text().strip()
        if not text:
            return {}
        return json.loads(text)
    except (OSError, json.JSONDecodeError):
        return {}


# Keywords associated with each plan type, used for memory pattern matching.
_PLAN_KEYWORDS = {
    "crud_endpoint": {"crud", "endpoint", "router", "schema", "route"},
    "migration": {"migration", "migrate", "model", "alembic", "column", "table"},
    "generic": set(),
}


def _find_relevant_patterns(goal: str, plan_type: str) -> list[str]:
    """
    Return pattern names from memory files that are relevant to the goal.

    Relevance is determined by simple keyword overlap: a pattern name is
    included if any word from it appears in the goal, or if the pattern
    name contains a keyword associated with the current plan type.
    """
    goal_words = set(goal.lower().split())
    type_keywords = _PLAN_KEYWORDS.get(plan_type, set())

    relevant: list[str] = []
    for source_file in (SUCCESSFUL_PATTERNS_FILE, KNOWN_FAILURES_FILE):
        data = _load_json_file(source_file)
        for key in data:
            key_words = set(key.lower().replace("_", " ").replace("-", " ").split())
            if key_words & goal_words or key_words & type_keywords:
                relevant.append(key)

    return relevant


def _load_run_history() -> list[dict]:
    if not RUN_HISTORY.exists():
        return []
    entries = []
    for line in RUN_HISTORY.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return entries


def planner(state: RunState) -> RunState:
    history = _load_run_history()
    prior_runs = [e for e in history if e.get("goal") == state.goal]
    last_failed = False
    preferred_skill = None
    if prior_runs:
        last_status = prior_runs[-1].get("status", "unknown")
        log("planner", "previous run detected for goal")
        log("planner", f"last status: {last_status}")
        last_failed = last_status == "failed"
        successful = [
            e for e in prior_runs
            if e.get("status") == "success" and e.get("skill_used")
        ]
        if successful:
            preferred_skill = successful[-1]["skill_used"]
            log("planner", f"previous successful skill detected: {preferred_skill}")

    keywords = state.goal.lower()

    if any(k in keywords for k in ("crud", "endpoint")):
        plan_type = "crud_endpoint"
        steps = [
            "analyse codebase",
            "inspect routers",
            "inspect schemas",
            "inspect models",
            "implement endpoint change",
            "add or update tests",
            "run tests",
        ]
    elif "migration" in keywords:
        plan_type = "migration"
        steps = [
            "analyse codebase",
            "inspect models",
            "prepare migration change",
            "run migrations",
            "run tests",
        ]
    else:
        plan_type = "generic"
        steps = [
            "analyse codebase",
            "identify files to create or modify",
            "implement change",
            "run tests",
        ]

    if last_failed:
        steps.insert(1, "review previous failure")
        log("planner", "adapting plan based on previous failure")

    relevant_patterns = _find_relevant_patterns(state.goal, plan_type)
    state.plan = {
        "plan_type": plan_type,
        "preferred_skill": preferred_skill,
        "steps": steps,
        "relevant_patterns": relevant_patterns,
    }
    log(
        "planner",
        f"selected plan_type={plan_type!r} with {len(steps)} steps"
        f" and {len(relevant_patterns)} relevant patterns",
    )
    return state


SKILL_MAP = {
    "crud_endpoint": "add_crud_endpoint",
    "migration": "add_alembic_migration",
    "generic": None,
}

SKILLS_DIR = Path(__file__).parent.parent / ".claude" / "skills" / "coding"


def builder(state: RunState) -> RunState:
    log("builder", "starting execution")

    preferred_skill = state.plan.get("preferred_skill")
    if preferred_skill:
        skill = preferred_skill
        log("builder", f"reusing preferred skill from memory: {skill}")
    else:
        skill = SKILL_MAP.get(state.plan.get("plan_type", "generic"))
        if skill:
            log("builder", f"using default skill: {skill}")
        else:
            log("builder", "no specific skill for this plan type")

    if skill:
        skill_file = SKILLS_DIR / f"{skill}.md"
        if skill_file.exists():
            skill_file.read_text()
            log("builder", f"loaded skill definition for {skill}")
        else:
            log("builder", "skill definition file not found")

    state.selected_skill = skill
    steps = state.plan.get("steps", [])
    total = len(steps)
    for i, step in enumerate(steps, start=1):
        log("builder", f"step {i}/{total}: {step}")
        state.executed_steps.append(step)
    state.build_complete = True
    return state


def tester(state: RunState) -> RunState:
    log("tester", f"running real test suite: {TEST_COMMAND!r}")

    result = subprocess.run(
        TEST_COMMAND,
        shell=True,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    state.test_output = "\n".join(filter(None, [result.stdout.rstrip(), result.stderr.rstrip()]))
    if state.test_output:
        print(state.test_output)

    state.test_passed = result.returncode == 0
    if state.test_passed:
        log("tester", "tests passed")
    else:
        log("tester", f"tests FAILED (exit code {result.returncode})")
        state.errors.append(f"tests failed with exit code {result.returncode}")

    return state


def _classify_failure(test_output: str) -> str:
    """Classify the most recent tester output into a structured failure type."""
    if any(t in test_output for t in ("ImportError", "ModuleNotFoundError")):
        return "import_error"
    if any(t in test_output for t in ("AssertionError", "FAILED", "ERROR")):
        return "test_failure"
    if any(t in test_output for t in ("E501", "E302", "flake8", "ruff")):
        return "lint_error"
    return "unknown"


def fixer(state: RunState) -> RunState:
    log("fixer", "tests failed — a fix would be attempted here in a future phase")
    last_error = state.errors[-1] if state.errors else "unknown error"
    state.failure_type = _classify_failure(state.test_output)
    state.fixer_notes = f"attempt {state.attempt_number} failed: {last_error}"
    log("fixer", f"classified failure as: {state.failure_type}")
    log("fixer", f"noted: {state.fixer_notes}")
    state.executed_steps.append("fix attempted")
    state.attempt_number += 1
    return state


def skill_curator(state: RunState) -> RunState:
    state.final_status = "success" if state.test_passed else "failed"
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "goal": state.goal,
        "plan_type": state.plan.get("plan_type"),
        "builder_status": "completed",
        "skill_used": state.selected_skill,
        "status": state.final_status,
        "steps_executed": state.executed_steps,
        "test_command": TEST_COMMAND,
        "test_passed": state.test_passed,
        "fixer_notes": state.fixer_notes or None,
        "failure_type": state.failure_type or None,
    }
    with RUN_HISTORY.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    log("skill_curator", f"run recorded to memory/run_history.jsonl (status: {state.final_status})")

    if state.final_status == "failed":
        failure = {
            "failure_type": "test_failure",
            "goal": state.goal,
            "plan_type": state.plan.get("plan_type"),
            "skill_used": state.selected_skill,
            "last_error": state.errors[-1] if state.errors else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        existing = _load_json_file(KNOWN_FAILURES_FILE)
        failures = existing if isinstance(existing, list) else []
        failures.append(failure)
        KNOWN_FAILURES_FILE.write_text(json.dumps(failures, indent=2))
        log("skill_curator", "failure recorded to memory/known_failures.json")

    return state


# ---------------------------------------------------------------------------
# Agent registry
#
# Maps agent names to their handler functions.  The orchestrator uses this
# table instead of calling functions directly, which is the groundwork for
# later decision-based orchestration where the next agent is chosen at
# runtime rather than being hardcoded in the control flow.
# ---------------------------------------------------------------------------

AGENT_REGISTRY: dict[str, Callable[[RunState], RunState]] = {
    "planner": planner,
    "builder": builder,
    "tester": tester,
    "fixer": fixer,
    "skill_curator": skill_curator,
}


# ---------------------------------------------------------------------------
# Decision function
#
# Separates "what should happen next?" from "execute it". The orchestrator
# calls this on every iteration and dispatches whatever name is returned.
#
# This is the foundation for future adaptive behavior: fixer or skill_curator
# can write a diagnosis or structured result back into RunState, and this
# function can then route differently on the next iteration — without touching
# the orchestrator or any other agent.
# ---------------------------------------------------------------------------

def decide_next_action(state: RunState) -> str:
    if not state.plan:
        return "planner"
    if not state.build_complete:
        return "builder"
    if state.final_status is not None:
        return "done"
    if state.test_passed:
        return "skill_curator"
    # Invariant: len(state.errors) == number of completed tester runs.
    # If errors < attempt_number, tester has not yet run this attempt.
    if len(state.errors) < state.attempt_number:
        return "tester"
    # Tester ran and failed this attempt.
    # Route to fixer if retries remain, otherwise close out.
    if state.attempt_number < MAX_ATTEMPTS:
        return "fixer"
    return "skill_curator"


def orchestrator(goal: str) -> RunState:
    """
    Pure dispatch loop. Contains no sequencing logic of its own.

    On each iteration decide_next_action reads RunState and returns the name
    of the next agent to run. The orchestrator dispatches it through
    AGENT_REGISTRY and repeats. This loop is what makes future adaptive
    behavior possible: once fixer writes a real diagnosis into RunState,
    decide_next_action can route differently on the next pass — and
    skill_curator can record richer outcomes — without changing anything here.
    """
    log("orchestrator", f"received goal: {goal!r}")
    state = RunState(goal=goal)

    while True:
        action = decide_next_action(state)
        if action == "done":
            break
        if action == "tester":
            log("orchestrator", f"test attempt {state.attempt_number}/{MAX_ATTEMPTS}")
        if action == "skill_curator" and not state.test_passed:
            log("orchestrator", f"all {MAX_ATTEMPTS} attempts exhausted — recording as failed")
        state = AGENT_REGISTRY[action](state)

    log("orchestrator", f"run complete — status: {state.final_status}")
    return state


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python workflows/improvement_loop.py \"<goal>\"")
        sys.exit(1)

    goal = sys.argv[1]
    final_state = orchestrator(goal)
    sys.exit(0 if final_state.final_status == "success" else 1)
