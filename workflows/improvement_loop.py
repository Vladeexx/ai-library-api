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
from datetime import datetime, timezone
from pathlib import Path

MEMORY_DIR = Path(__file__).parent.parent / "memory"
RUN_HISTORY = MEMORY_DIR / "run_history.jsonl"
TEST_COMMAND = "make test"


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
    status = skill_curator(
        goal=goal,
        passed=passed,
        steps_executed=steps_executed,
        plan_type=plan["plan_type"],
        builder_status=build_result["builder_status"],
    )
    log("orchestrator", f"run complete — status: {status}")
    return {"status": status, "steps_executed": steps_executed}


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


def planner(goal: str) -> dict:
    history = _load_run_history()
    prior_runs = [e for e in history if e.get("goal") == goal]
    if prior_runs:
        last_status = prior_runs[-1].get("status", "unknown")
        log("planner", "previous run detected for goal")
        log("planner", f"last status: {last_status}")

    keywords = goal.lower()

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

    plan = {"goal": goal, "plan_type": plan_type, "steps": steps}
    log("planner", f"selected plan_type={plan_type!r} with {len(steps)} steps")
    return plan


def builder(plan: dict) -> dict:
    log("builder", "starting execution")
    steps = plan["steps"]
    total = len(steps)
    executed_steps = []
    for i, step in enumerate(steps, start=1):
        log("builder", f"step {i}/{total}: {step}")
        executed_steps.append(step)
    return {"plan": plan, "executed_steps": executed_steps, "builder_status": "completed"}


def tester(build_result: dict) -> tuple[bool, list[str]]:
    steps = build_result["executed_steps"] + ["run tests"]
    log("tester", f"running real test suite: {TEST_COMMAND!r}")

    result = subprocess.run(
        TEST_COMMAND,
        shell=True,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())

    passed = result.returncode == 0
    if passed:
        log("tester", "tests passed")
    else:
        log("tester", f"tests FAILED (exit code {result.returncode})")

    return passed, steps


def fixer(steps_executed: list[str]) -> list[str]:
    log("fixer", "tests failed — a fix would be attempted here in a future phase")
    return steps_executed + ["fix attempted"]


def skill_curator(
    goal: str,
    passed: bool,
    steps_executed: list[str],
    plan_type: str,
    builder_status: str,
) -> str:
    status = "success" if passed else "failed"
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "goal": goal,
        "plan_type": plan_type,
        "builder_status": builder_status,
        "status": status,
        "steps_executed": steps_executed,
        "test_command": TEST_COMMAND,
        "test_passed": passed,
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
