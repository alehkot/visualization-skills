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
when available, a one-based line and column. The checker uses PyYAML's safe loader
and rejects repeated explicit string fields in the same mapping, including nested
metadata, rather than silently keeping the last value. Quoted and unquoted spellings of the same string field count as a
repeat. Anchors, aliases, and deliberate YAML merge overrides remain supported.
This check targets string field names, not every possible YAML key type; it does
not enforce every optional Agent Skills field or replace a full Markdown parser.
These maintenance checks do not measure explanation quality.

```sh
uv sync --dev
uv run python scripts/validate.py
uv run pytest -q
uv run ruff check scripts tests
```

The checker validates metadata, local resources, and the tracked bundle inventory. Update `public-files.json` deliberately when adding a distributable file.

Local Markdown links must use relative paths to files inside the same skill and in
the tracked inventory. An ignored or untracked file can exist in your workspace
while being absent from a fresh checkout; it must not make the bundle check pass.
When adding a resource, update the inventory and `.gitignore` allowlist, then stage
the file before validating. Absolute filesystem paths (including rooted drive-letter
paths), `file:` URLs, and symlink aliases are rejected so local-only paths cannot
stand in for distributed resources.

These are offline maintenance checks for single-line inline Markdown links and
images. They retain balanced parentheses in destinations (such as
`assets/chart(1).svg`), angle-bracket destinations, backslash-escaped punctuation,
and balanced brackets in labels. Optional single-line titles are separate from
the resource path. These forms follow the [CommonMark link syntax](https://spec.commonmark.org/0.31.2/#links).
The checker is not a complete Markdown parser: it does not validate remote URLs
or cover every Markdown form, such as reference-style or multiline links. It
does not measure the skills' explanation quality or reader comprehension.

For ATX heading anchors, the checker reads inline text before generating the
fragment: `_Important_` contributes `important`, while literal underscores in
`read_csv`, escaped text, and code spans remain meaningful. Formatted and plain
headings with the same resulting fragment share the duplicate-heading suffix
sequence. Inline heading parsing uses `markdown-it-py`; this does not extend the
resource-link checker to all Markdown syntax or certify every GitHub extension.
See [GitHub's section-link rules](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#section-links).

## Woodpecker CI

The [workflow](.woodpecker.yaml) runs on pushes to `development` and on manual runs after this
repository is enabled in Woodpecker. It selects a native Mac or Linux ARM64/Pi worker with the
tools below. Both use the **local backend**, not a Docker image: `image: bash` selects the
shell. Portable jobs take any matching available worker; strict Mac-first priority is not
configured.

[`.ci/check.sh`](.ci/check.sh) contains the project-specific build/test commands. Run the same
checks locally from the repository root with `bash .ci/check.sh`. Prerequisites: Python 3.11+,
uv and Git. These are offline bundle/validator tests, not live model evaluations.

Configure the server's GitHub integration and a reachable webhook endpoint once. The agents
connect outbound; no SSH access to the Mac is needed. Install the native `plugin-git` clone
helper and put all required tools on the worker's PATH. Use one workflow at a time per worker
because browser suites and simulators share local resources. Run only trusted code under a
dedicated worker account; the local backend is not a sandbox. Configure a finite repository
pipeline timeout.

Add a repository-scoped fine-grained **user PAT** as the Woodpecker secret
`github_comment_token`, with Contents: write permission for this repository (required to update
comments). It is injected only into the comment step. That step creates a pass/fail comment on
`CI_COMMIT_SHA`, with the pipeline link and a bounded failure excerpt; repeating the report for
the same pipeline/workflow updates its own comment. A reporting failure fails the step instead
of silently claiming that a comment was sent. Woodpecker's built-in commit statuses remain
separate from these comments.

Console output is retained by Woodpecker according to the server's retention policy. Files in
`.ci-output/` (including any raw Xcode log/result bundle) are temporary workspace output, not
automatically uploaded artifacts. Configure artifact storage before relying on those files after
worker cleanup. A Tailnet-only log link requires Tailnet access; the comment excerpt is stored
on GitHub and visible to repository readers. Known token values are masked, but logs must not
contain private data.

Test the reporter without network access: `python3 -B .ci/test_report.py`. No CI server, secret,
webhook or worker is provisioned merely by adding these files. Existing GitHub Actions workflows
are unchanged.
