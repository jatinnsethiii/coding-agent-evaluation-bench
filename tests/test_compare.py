"""Offline comparison tests: no execution of candidate code."""
import json
from pathlib import Path
import pytest
from evaluator.compare import load_comparison, markdown_report


def write_pair(tmp_path: Path, *, status="failed", passed=1, failed=1):
    (tmp_path / "report.json").write_text(json.dumps({"results": [{
        "task": "api_pagination", "status": status, "passed": passed,
        "failed": failed, "errors": 0, "skipped": 0,
    }]}))
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"candidates": [{
        "id": "test-1", "task": "api_pagination", "report": "report.json",
        "source": "synthetic_fixture", "notes": "Not a real model output"
    }]}))
    return manifest


def test_compare_parses_results_and_generates_markdown(tmp_path):
    comparison = load_comparison(write_pair(tmp_path))
    row = comparison["candidates"][0]
    assert row["pass_fraction"] == 0.5
    assert row["human_review"]["correctness"] is None
    assert "1/2" in markdown_report(comparison)
    assert "synthetic_fixture" in markdown_report(comparison)


def test_compare_rejects_mismatched_task(tmp_path):
    manifest = write_pair(tmp_path)
    data = json.loads(manifest.read_text())
    data["candidates"][0]["task"] = "cache_expiration"
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="matching task"):
        load_comparison(manifest)


def test_compare_rejects_duplicate_candidate(tmp_path):
    manifest = write_pair(tmp_path)
    data = json.loads(manifest.read_text())
    data["candidates"].append(data["candidates"][0])
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="Duplicate"):
        load_comparison(manifest)


def test_compare_rejects_false_pass(tmp_path):
    with pytest.raises(ValueError, match="Inconsistent"):
        load_comparison(write_pair(tmp_path, status="passed"))


def test_zero_executed_tests_not_reported_as_success(tmp_path):
    with pytest.raises(ValueError, match="No executed tests"):
        load_comparison(write_pair(tmp_path, status="passed", passed=0, failed=0))
