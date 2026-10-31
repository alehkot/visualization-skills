#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
trap 'printf "CI check failed at line %s\n" "$LINENO" >&2' ERR

uv sync --locked --dev
uv run python scripts/validate.py
uv run pytest -q
uv run ruff check scripts tests
