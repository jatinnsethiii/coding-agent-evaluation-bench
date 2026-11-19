from pathlib import Path
import pytest
from evaluator.runner import evaluate, list_tasks


@pytest.mark.parametrize("task", [t.name for t in list_tasks()])
def test_reference_passes(task):
    result = evaluate(task, Path("tasks") / task / "reference.py")
    assert result["status"] == "passed", result["test_output_tail"]
    assert result["score_percent"] == 100


@pytest.mark.parametrize("task", [t.name for t in list_tasks()])
def test_buggy_fails(task):
    result = evaluate(task, Path("tasks") / task / "buggy.py")
    assert result["status"] == "failed", result["test_output_tail"]
    assert result["failed"] >= 1


def test_invalid_task_rejected():
    with pytest.raises(ValueError):
        evaluate("does-not-exist", Path("tasks/cache_expiration/reference.py"))
