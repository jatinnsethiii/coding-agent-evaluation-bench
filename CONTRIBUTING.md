# Contributing

New tasks should be original and licensed for public use. Each task must include `task.json`, `README.md`, `buggy.py`, `reference.py`, and `test_solution.py`. Tests should pass for the reference implementation and fail for the buggy baseline. Prefer deterministic edge cases over flaky timing tests, document simplifications and threat models, and avoid leaking proprietary interview/annotation content.

Run `python -m pytest -q` before proposing a change. For model-generated samples, disclose the model/version, prompting approach and evaluation environment; never label synthetic or seeded baseline results as real model performance.
