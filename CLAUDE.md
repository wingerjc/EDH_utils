# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

EDH_utils is a collection of MTG (Magic: The Gathering) utility tools for sorting, searching, and finding cards.

Current projects:
- **set-finder**: finds possible sets for a list of cards

## Technology Stack

This is a Python project using **poetry** as the package manager.
- **Testing**: pytest
- **Linting/formatting**: ruff
- **Type checking**: mypy

## Commands

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run a single test
poetry run pytest tests/path/to/test_file.py::test_name

# Lint
poetry run ruff check .

# Format
poetry run ruff format .

# Type check
poetry run mypy .
```

## Workflow

Before making any code changes, present a plan and wait for explicit confirmation. Do not begin implementation until the user approves.

## README

When commands are added or removed, or when command options are added, removed, or updated, always regenerate the affected help text and update `README.md` as part of the same change:

```bash
poetry run edh-utils --help
poetry run edh-utils <subcommand> --help
```

## Git

Always use `--no-gpg-sign` when creating local commits. Always include the following trailer in commit messages:

```
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```
