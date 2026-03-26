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
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

MEMORY_DIR = Path(__file__).parent.parent / "memory"
RUN_HISTORY = MEMORY_DIR / "run_history.jsonl"


# ---------------------------------------------------------------------------
# Logging helper
# ---------------------------------------------------------------------------

def log(agent: str, message: str) -> None:
    print(f"[{agent}] {message}")


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

def orchestrator(goal: str) -> dict:
    log("orchestrator", f"received goal: {goal!r}")
    plan = planner(goal)
    build_result = builder(plan)
    passed, steps_executed = tester(build_result)
    if not passed:
        steps_executed = fixer(steps_executed)
    status = skill_curator(goal, passed, steps_executed)
    log("orchestrator", f"run complete — status: {status}")
    return {"status": status, "steps_executed": steps_executed}


def planner(goal: str) -> dict:
    plan = {
        "goal": goal,
        "steps": [
            "analyse codebase",
            "identify files to create or modify",
            "implement change",
            "run tests",
        ],
    }
    log("planner", f"generated plan with {len(plan['steps'])} steps")
    return plan


def builder(plan: dict) -> dict:
    log("builder", "executing steps:")
    for step in plan["steps"]:
        log("builder", f"  → {step}")
    return {"plan": plan, "outcome": "build complete"}


def tester(build_result: dict) -> tuple[bool, list[str]]:
    steps = build_result["plan"]["steps"] + ["run tests"]
    # Simulate a test run — replace with a real subprocess call in a future phase.
    passed = random.choice([True, True, True, False])  # 75% pass rate
    if passed:
        log("tester", "tests passed")
    else:
        log("tester", "tests FAILED")
    return passed, steps


def fixer(steps_executed: list[str]) -> list[str]:
    log("fixer", "analysing failure and applying fix")
    steps_executed = steps_executed + ["apply fix"]
    log("fixer", "fix applied — handing back to tester")
    # Re-run tester after fix (simplified: assume fix succeeds).
    log("tester", "tests passed after fix")
    return steps_executed


def skill_curator(goal: str, passed: bool, steps_executed: list[str]) -> str:
    status = "success" if passed else "failed"
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "goal": goal,
        "status": status,
        "steps_executed": steps_executed,
    }
    with RUN_HISTORY.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    log("skill_curator", f"run recorded to memory/run_history.jsonl (status: {status})")
    return status


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python workflows/improvement_loop.py \"<goal>\"")
        sys.exit(1)

    goal = sys.argv[1]
    orchestrator(goal)
