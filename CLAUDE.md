# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

EDH_utils is a collection of MTG (Magic: The Gathering) utility tools for sorting, searching, and finding cards.

Current projects:
- **set-finder**: finds possible sets for a list of cards

## Technology Stack

This is a Python project. The `.gitignore` suggests the following tooling is expected:
- **Package manager**: uv, poetry, or pdm (not yet configured — check `pyproject.toml` once added)
- **Testing**: pytest
- **Linting/formatting**: ruff
- **Type checking**: mypy

## Commands

Once a `pyproject.toml` is in place, typical commands will be (update this section as tooling is established):

```bash
# Install dependencies
uv sync  # or: poetry install / pdm install

# Run tests
pytest

# Run a single test
pytest path/to/test_file.py::test_name

# Lint
ruff check .

# Format
ruff format .

# Type check
mypy .
```
