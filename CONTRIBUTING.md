# Contributing to annox

Thank you for helping build a robust, open annotation conversion tool.

- Code style: follow ruff/black defaults where applicable.
- Tests: add unit tests for new behavior; keep CI green.
- Licensing: project is GPL-3.0-only. Retain MIT headers when reusing code and list sources in `docs/development.md`.
- Python first: ensure pure-Python fallbacks exist before Rust.

## Dev setup

- Python 3.9+
- Create a venv and install in editable mode: `pip install -e .[dev]`
- Run tests: `pytest -q`
- Lint: `ruff check .`

## Commit guidance

Use short, clear messages. For major tasks, include Purpose / Scope / Outcome in the PR description.
