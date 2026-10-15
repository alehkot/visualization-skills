# Visualization Skills

Two independent Agent Skills for making difficult information easier to understand visually. They produce information structure and suggested ways to represent it, independent of whether the final artifact becomes PlantUML, Mermaid, an ASCII chart, or another medium.

## Skills

- [design-visual-explanation](skills/design-visual-explanation/SKILL.md)
- [review-visual-explanation](skills/review-visual-explanation/SKILL.md)

## Install

Clone this repository, then copy or symlink the desired folder from `skills/` into your agent's skills directory.

```sh
npx skills add alehkot/visualization-skills --skill '*'
```

## Maintenance

Frontmatter must start at the beginning of `SKILL.md`, between standalone `---`
lines (trailing spaces or tabs are allowed). Prefixes such as `---oops` and `----`
are not closing delimiters. Invalid YAML is reported with the skill filename and,
when available, a one-based line and column. The checker uses PyYAML's safe loader;
it does not enforce every optional Agent Skills field or replace a full Markdown
parser. These maintenance checks do not measure explanation quality.

```sh
uv sync --dev
uv run python scripts/validate.py
uv run pytest -q
uv run ruff check scripts tests
```

The checker validates metadata, local resources, and the tracked bundle inventory. Update `public-files.json` deliberately when adding a distributable file.
