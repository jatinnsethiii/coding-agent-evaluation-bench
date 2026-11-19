# Coding Agent Evaluation Bench

[![Tests](https://img.shields.io/badge/tests-pytest-informational)](#reproduce-the-results)

A **small, reproducible code-evaluation benchmark** for backend bug-fixing tasks. Built to demonstrate the skills needed to assess AI-generated code: task specification, executable grading, edge cases, and failure analysis.

> **Status:** Initial benchmark with **3 hand-authored tasks**, broken baselines, and reference implementations. It does **not** yet contain independently sampled AI-model outputs, comparative model results, or evidence that any model achieves a particular score. Do not interpret a baseline/reference comparison as an AI model benchmark.

## Why this project

AI coding evaluations should verify behavior, not just whether a solution looks plausible. Each task includes an original engineering problem, an intentionally broken solution, a reference implementation, and executable tests. A subprocess runner emits machine-readable scoring summaries.

## Included tasks

| Task | Failure mode | What tests reveal |
|---|---|---|
| `payment_idempotency` | Check-then-act race on duplicate webhook | Concurrent delivery can charge multiple times |
| `cache_expiration` | Strict vs non-strict TTL expiry check | Entries survive at exact expiration boundary |
| `api_pagination` | Off-by-one cursor advancement | A page silently drops a valid item |

These are simplified, original educational exercises, **not** production-grade transaction or cache implementations.

## Reproduce the results

Requires Python 3.10+. Commands from repository root:

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m evaluator.runner --all --candidate reference --output reports/reference-results.json
python -m evaluator.runner --all --candidate buggy --output reports/buggy-results.json  # expected exit code 1
```

For one scenario or your own locally trusted solution:

```bash
python -m evaluator.runner --task api_pagination --candidate buggy
python -m evaluator.runner --task api_pagination --candidate-file /path/to/solution.py
```

Report fields: per-task `status`, passed/failed/error counts, `score_percent` (pass fraction of executed tests), run time, and pytest output. Scores are test-pass fractions, **not** calibrated AI capability scores. A task is only marked passed if all tests pass. Timed-out or crashed tasks are not treated as successes.

### Security warning

**Candidate code is executed by pytest and is NOT sandboxed.** Use only locally trusted code. To evaluate external AI submissions safely, isolate execution in a restricted container/VM without network access, with nonprivileged user, resource limits, and a read-only filesystem. A subprocess timeout is not a security boundary.

## Evaluation design

1. Specify behavior and edge cases in each task's README.
2. Prove reference passes all tests.
3. Prove seeded buggy implementation fails at least one test.
4. Collect machine-readable scores and diagnostic output.
5. Inspect test gaps (e.g., distributed concurrency isn't covered by an in-process lock).
6. For future model comparisons, record model name/version, prompt, temperature, sample count, execution environment and independent review notes.

## Limitations and roadmap

- Only three small Python backend tasks; this is an initial evaluation harness, not SWE-bench.
- No model outputs have been collected or scored yet.
- Test scores can be gamed and do not capture maintainability, security, or performance.
- Concurrency test deliberately increases race exposure; does not guarantee universal correctness.
- No secure sandbox for untrusted candidates.
- Next: add independent AI-generated candidate solutions, blinded human rubric reviews, task-level weights, and containerized execution.

## Repository layout

```text
evaluator/runner.py       # repeatable subprocess test runner
tasks/*/task.json        # task metadata
tasks/*/README.md        # behavioral specification
tasks/*/buggy.py         # known incorrect baseline
tasks/*/reference.py     # passing reference implementation
tasks/*/test_solution.py # grading test suite
tests/test_runner.py     # harness self-tests
reports/                 # reproducible sample reports
.github/workflows/       # multi-version continuous integration
```

## Responsible use

All examples are newly written for this repository. Do not paste confidential employer code or private paid annotation tasks. Contributions are welcome as small test-backed tasks; see [CONTRIBUTING.md](CONTRIBUTING.md). Licensed MIT.
