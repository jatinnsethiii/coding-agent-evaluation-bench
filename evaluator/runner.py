"""Run executable grading tests against a locally trusted candidate solution.

WARNING: pytest executes candidate Python code. This is NOT a sandbox.
Never run an untrusted model response on your main workstation without isolation.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "tasks"


def list_tasks():
    return sorted(x for x in TASKS.iterdir() if x.is_dir() and (x / "task.json").is_file())


def evaluate(task_id: str, candidate: Path, timeout: int = 20) -> dict:
    task = TASKS / task_id
    if task not in list_tasks():
        raise ValueError(f"Unknown task: {task_id}")
    if not candidate.is_file():
        raise FileNotFoundError(candidate)
    metadata = json.loads((task / "task.json").read_text())
    with tempfile.TemporaryDirectory(prefix="code-eval-") as work:
        cwd = Path(work)
        shutil.copy2(candidate, cwd / "solution.py")
        shutil.copy2(task / "test_solution.py", cwd / "test_solution.py")
        started = time.monotonic()
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "test_solution.py", "--junitxml=results.xml"],
                cwd=cwd, capture_output=True, text=True, timeout=timeout,
                env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": __import__("os").environ.get("PATH", "")},
            )
            timed_out = False
        except subprocess.TimeoutExpired:
            result = None
            timed_out = True
        elapsed = round(time.monotonic() - started, 3)
        passed = failed = errors = skipped = 0
        if (cwd / "results.xml").exists():
            root = ET.parse(cwd / "results.xml").getroot()
            cases = root.findall(".//testcase")
            for case in cases:
                if case.find("failure") is not None:
                    failed += 1
                elif case.find("error") is not None:
                    errors += 1
                elif case.find("skipped") is not None:
                    skipped += 1
                else:
                    passed += 1
        total = passed + failed + errors
        status = "timeout" if timed_out else ("infrastructure_error" if (not total or result.returncode not in (0, 1)) else ("passed" if failed == 0 and errors == 0 else "failed"))
        return {
            "task": task_id, "candidate": str(candidate), "description": metadata["title"],
            "status": status, "passed": passed, "failed": failed, "errors": errors,
            "skipped": skipped, "score_percent": round(100 * passed / total, 1) if total else 0.0,
            "runtime_seconds": elapsed, "timeout_seconds": timeout,
            "test_output_tail": ("Timed out" if timed_out else (result.stdout + "\n" + result.stderr)[-2500:]),
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", choices=[t.name for t in list_tasks()], help="Task to evaluate")
    parser.add_argument("--candidate", choices=["buggy", "reference"], default="reference", help="Bundled baseline candidate")
    parser.add_argument("--candidate-file", type=Path, help="Path to an alternative local candidate .py file")
    parser.add_argument("--all", action="store_true", help="Run every task")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--output", type=Path, help="Write results to JSON file")
    args = parser.parse_args()
    if not args.all and not args.task:
        parser.error("Specify --task or --all")
    if args.all and args.candidate_file:
        parser.error("--candidate-file requires one --task")
    if args.timeout < 1:
        parser.error("--timeout must be at least 1")
    ids = [t.name for t in list_tasks()] if args.all else [args.task]
    reports = [evaluate(t, args.candidate_file or (TASKS / t / f"{args.candidate}.py"), args.timeout) for t in ids]
    payload = {"schema_version": 1, "results": reports, "summary": {
        "tasks": len(reports), "passed_tasks": sum(r["status"] == "passed" for r in reports),
        "mean_test_pass_rate": round(sum(r["score_percent"] for r in reports) / len(reports), 1),
    }}
    print(json.dumps(payload, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0 if all(r["status"] == "passed" for r in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
