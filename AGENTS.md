# Repository guidelines

Keep this repository focused on deployable Agent Skills and their basic maintenance tools.

- Keep each skill self-contained: `SKILL.md`, references, runtime scripts, assets, and supported UI metadata.
- Put activation guidance in frontmatter descriptions and detailed instructions in linked references.
- Preserve source facts and attribution. Do not copy long source passages.
- Keep installs and packages limited to deployable files.
- Update `public-files.json` deliberately when changing the bundle inventory.
- Before handing off, run `uv run python scripts/validate.py`, `uv run pytest -q`, and `uv run ruff check scripts tests`.
