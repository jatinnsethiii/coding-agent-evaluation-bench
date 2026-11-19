"""Compare recorded code-evaluation results without executing submitted code."""
import argparse
import json
from pathlib import Path

REQUIRED_FIELDS = {"id", "task", "report", "source"}
VALID_STATUSES = {"passed", "failed", "timeout", "infrastructure_error"}


def load_comparison(manifest_path: Path) -> dict:
    manifest_path = manifest_path.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    candidates = manifest.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("Manifest requires a nonempty 'candidates' array")
    observed = set()
    rows = []
    for item in candidates:
        if not isinstance(item, dict) or not REQUIRED_FIELDS.issubset(item):
            raise ValueError(f"Each candidate must provide: {sorted(REQUIRED_FIELDS)}")
        if not all(isinstance(item[k], str) and item[k].strip() for k in REQUIRED_FIELDS):
            raise ValueError("Candidate id, task, report and source must be nonempty strings")
        identity = (item["task"], item["id"])
        if identity in observed:
            raise ValueError(f"Duplicate candidate: {identity}")
        observed.add(identity)
        report_file = (manifest_path.parent / item["report"]).resolve()
        report = json.loads(report_file.read_text(encoding="utf-8"))
        results = report.get("results", [])
        if len(results) != 1 or results[0].get("task") != item["task"]:
            raise ValueError(f"Report for {identity} must contain exactly its matching task")
        result = results[0]
        if result.get("status") not in VALID_STATUSES:
            raise ValueError(f"Unknown status for {identity}")
        for field in ("passed", "failed", "errors", "skipped"):
            if type(result.get(field)) is not int or result[field] < 0:
                raise ValueError(f"Invalid {field} for {identity}")
        total = result["passed"] + result["failed"] + result["errors"]
        if total == 0 and result["status"] in {"passed", "failed"}:
            raise ValueError(f"No executed tests for {identity}")
        if result["status"] == "passed" and (result["failed"] or result["errors"]):
            raise ValueError(f"Inconsistent passing result for {identity}")
        rows.append({
            "id": item["id"], "task": item["task"], "source": item["source"],
            "model": item.get("model"), "model_version": item.get("model_version"),
            "prompt_sha256": item.get("prompt_sha256"), "notes": item.get("notes", ""),
            "status": result["status"], "passed": result["passed"],
            "failed": result["failed"], "errors": result["errors"],
            "skipped": result["skipped"], "executed_tests": total,
            "pass_fraction": round(result["passed"] / total, 4) if total else None,
            "human_review": {"correctness": None, "edge_cases": None,
                             "maintainability": None, "explanation_quality": None,
                             "reviewer_notes": "Not yet assessed"},
        })
    return {"schema_version": 1, "purpose": "candidate comparison; no code executed",
            "candidates": rows}


def markdown_report(comparison: dict) -> str:
    lines = ["# Candidate evaluation comparison", "",
             "> Scores are fractions of executed automated tests, not calibrated model quality. "
             "Human-review fields are deliberately unscored. Source labels are self-reported; "
             "no model origin is independently verified.", "",
             "| Task | Candidate | Source | Tests passed | Outcome |",
             "|---|---|---|---:|---|"]
    for row in comparison["candidates"]:
        source = row["source"].replace("|", "\\|").replace("\n", " ")
        fraction = f'{row["passed"]}/{row["executed_tests"]}' if row["executed_tests"] else "N/A"
        lines.append(f'| {row["task"]} | {row["id"]} | {source} | {fraction} | {row["status"]} |')
    lines.extend(["", "## Interpretation", "",
                  "- Passing tests is necessary but does not establish production correctness.",
                  "- Compare results only for candidates evaluated against the same task and test suite.",
                  "- Review security, maintainability, edge cases, and explanations manually.",
                  "- Do not run untrusted AI-generated code on your host machine.", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()
    try:
        result = load_comparison(args.manifest)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    rendered = markdown_report(result)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(rendered, encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
