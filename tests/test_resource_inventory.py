"""Check local resource portability through the real validator and Git index."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
from urllib.parse import unquote

import pytest
from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parents[1]
SKILL = "skills/example"
FRONTMATTER = "---\nname: example\ndescription: A test skill.\n---\n\n# Example\n"


@pytest.fixture
def bundle(tmp_path):
    for name in ("check_inventory.py", "skill_resources.py", "validate.py"):
        target = tmp_path / "scripts" / name
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(ROOT / "scripts" / name, target)
    skill = tmp_path / SKILL
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        FRONTMATTER + "\n[Context](references/context.md#details)\n", encoding="utf-8"
    )
    (skill / "references/context.md").write_text("# Context\n\n## Details\n", encoding="utf-8")
    # Local-only resources deliberately exist under Git's ignored-file boundary.
    (tmp_path / ".gitignore").write_text("*\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    names = sorted(
        str(path.relative_to(tmp_path)) for path in tmp_path.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(tmp_path).parts
    )
    names.append("public-files.json")
    (tmp_path / "public-files.json").write_text(json.dumps(names), encoding="utf-8")
    subprocess.run(["git", "add", "-f", "--", *names], cwd=tmp_path, check=True)
    return tmp_path


def validate(bundle):
    return subprocess.run(
        [sys.executable, "scripts/validate.py"], cwd=bundle,
        capture_output=True, text=True, timeout=15,
    )


def append_link(bundle, target, source="SKILL.md", image=False):
    path = bundle / SKILL / source
    with path.open("a", encoding="utf-8") as stream:
        stream.write(f"\n{'!' if image else ''}[Resource]({target})\n")


def add_resource(bundle, name, content="Resource\n", *, declare=True, stage=True):
    path = bundle / SKILL / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    relative = str(path.relative_to(bundle))
    if declare:
        manifest = bundle / "public-files.json"
        manifest.write_text(json.dumps([*json.loads(manifest.read_text()), relative]))
    if stage:
        subprocess.run(["git", "add", "-f", "--", relative], cwd=bundle, check=True)
    return path


@pytest.mark.parametrize("name,target,source,image", [
    ("assets/local.txt", "assets/local.txt", "SKILL.md", False),
    ("scripts/local.py", "scripts/local.py", "SKILL.md", False),
    ("assets/local.svg", "assets/local.svg", "SKILL.md", True),
    ("assets/local file.txt", "assets/local%20file.txt", "SKILL.md", False),
    ("assets/local.txt", "../assets/local.txt", "references/context.md", False),
    ("references/local.md", "references/local.md", "SKILL.md", False),
])
def test_rejects_existing_local_only_targets(bundle, name, target, source, image):
    resource = add_resource(bundle, name, declare=False, stage=False)
    append_link(bundle, target, source, image)
    ignored = subprocess.run(
        ["git", "check-ignore", "--", str(resource)], cwd=bundle, capture_output=True,
    )
    assert ignored.returncode == 0
    result = validate(bundle)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "not in the tracked bundle inventory" in result.stderr


@pytest.mark.parametrize("declare,stage,expected", [
    (True, False, "missing="),
    (False, True, "unexpected="),
])
def test_declaration_and_staging_are_both_required(bundle, declare, stage, expected):
    add_resource(bundle, "assets/data.txt", declare=declare, stage=stage)
    append_link(bundle, "assets/data.txt")
    result = validate(bundle)
    assert result.returncode == 1
    assert "Bundle inventory differs" in result.stderr
    assert expected in result.stderr


@pytest.mark.parametrize("encoded", [False, True])
def test_rejects_absolute_paths_even_to_bundled_files(bundle, encoded):
    target = str(bundle / SKILL / "references/context.md")
    append_link(bundle, target.replace("/", "%2F") if encoded else target)
    result = validate(bundle)
    assert result.returncode == 1
    assert "must use a relative path" in result.stderr


@pytest.mark.parametrize("target", [
    "file:///not-shipped/resource.md",
    "FILE:///not-shipped/resource.md",
    "file://localhost/not-shipped/resource.md",
    "C:/local/resource.md",
    "C:\\local\\resource.md",
])
def test_rejects_nonportable_filesystem_urls_and_drive_paths(bundle, target):
    append_link(bundle, target)
    result = validate(bundle)
    assert result.returncode == 1
    assert "must use a relative path" in result.stderr


@pytest.mark.parametrize("kind,target", [
    ("file", "alias.md#details"),
    ("directory", "alias/context.md#details"),
    ("directory", "alias/../SKILL.md#example"),
])
def test_rejects_unshipped_symlink_aliases_to_bundled_files(bundle, kind, target):
    skill = bundle / SKILL
    if kind == "file":
        (skill / "alias.md").symlink_to("references/context.md")
    else:
        (skill / "alias").symlink_to("references", target_is_directory=True)
    append_link(bundle, target)
    result = validate(bundle)
    assert result.returncode == 1
    assert "uses a symlink" in result.stderr


def test_accepts_packaged_assets_scripts_and_encoded_relative_links(bundle):
    add_resource(bundle, "assets/data file.txt")
    add_resource(bundle, "assets/chart.svg", "<svg/>\n")
    add_resource(bundle, "scripts/helper.py", "print('example')\n")
    append_link(bundle, "assets/data%20file.txt")
    append_link(bundle, "assets/chart.svg", image=True)
    append_link(bundle, "scripts/helper.py")
    append_link(bundle, "../assets/data%20file.txt", "references/context.md")
    append_link(bundle, "#details", "references/context.md")
    result = validate(bundle)
    assert result.returncode == 0, result.stderr
    assert "Validated 1 deployable skills." in result.stdout


def test_accepts_external_links_code_examples_and_unused_local_assets(bundle):
    add_resource(bundle, "assets/unused.txt", declare=False, stage=False)
    append_link(bundle, "https://example.com/missing.md#unverified")
    append_link(bundle, "//example.com/missing.md")
    append_link(bundle, "mailto:maintainer@example.com")
    entry = bundle / SKILL / "SKILL.md"
    with entry.open("a", encoding="utf-8") as stream:
        stream.write("\n`[Example](not-shipped.txt)`\n\n```md\n[Example](missing.md)\n```\n")
    result = validate(bundle)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("target,expected", [
    ("assets/absent.txt", "broken local link"),
    ("references/context.md#absent", "incorrect anchor"),
    ("../../public-files.json", "escapes the standalone skill"),
])
def test_preserves_existing_link_failures(bundle, target, expected):
    append_link(bundle, target)
    result = validate(bundle)
    assert result.returncode == 1
    assert expected in result.stderr


def test_packaged_reference_must_still_be_linked_from_entrypoint(bundle):
    add_resource(bundle, "references/unlinked.md", "# Unlinked\n")
    result = validate(bundle)
    assert result.returncode == 1
    assert "never linked directly from SKILL.md" in result.stderr


def test_packaged_links_survive_copy_without_ignored_files(bundle, tmp_path_factory):
    add_resource(bundle, "assets/data.txt")
    add_resource(bundle, "assets/unused.txt", declare=False, stage=False)
    append_link(bundle, "assets/data.txt")
    assert validate(bundle).returncode == 0
    destination = tmp_path_factory.mktemp("relocated")
    names = json.loads((bundle / "public-files.json").read_text())
    for name in names:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(bundle / name, target)
    subprocess.run(["git", "init", "-q", str(destination)], check=True)
    subprocess.run(["git", "add", "-f", "--", *names], cwd=destination, check=True)
    assert not (destination / SKILL / "assets/unused.txt").exists()
    result = validate(destination)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("name,markup", [
    ("assets/chart(1).svg", "[Chart](assets/chart(1).svg)"),
    ("assets/chart(1).svg", "[Chart](<assets/chart(1).svg>)"),
    ("assets/chart(1).svg", r"[Chart](assets/chart\(1\).svg)"),
    ("assets/chart((1)).svg", "[Chart](assets/chart((1)).svg)"),
    ("assets/chart(1.svg", "[Chart](<assets/chart(1.svg>)"),
    ("assets/chart(1.svg", r"[Chart](assets/chart\(1.svg)"),
    ("assets/chart (1).svg", "[Chart](<assets/chart (1).svg>)"),
    ("assets/chart(1).svg", '[Chart](assets/chart(1).svg "Draft (1)")'),
    ("assets/chart(1).svg", "[Chart](assets/chart(1).svg 'Draft (1)')"),
    ("assets/chart(1).svg", "[Chart](assets/chart(1).svg (Draft))"),
    ("assets/chart(1).svg", r'[Chart](assets/chart(1).svg "A \"draft\"")'),
    ("assets/chart.svg", "[Chart [draft]](assets/chart.svg)"),
    ("assets/chart.svg", r"[Chart \[draft\]](assets/chart.svg)"),
    ("assets/chart.svg", "![Chart [draft]](assets/chart.svg)"),
])
def test_accepts_packaged_inline_links_with_balanced_syntax(bundle, name, markup):
    add_resource(bundle, name, "<svg/>\n")
    with (bundle / SKILL / "SKILL.md").open("a", encoding="utf-8") as stream:
        stream.write("\n" + markup + "\n")
    result = validate(bundle)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("markup,expected", [
    ("[Chart [draft]](assets/missing.svg)", "broken local link"),
    ("![Chart [draft]](assets/missing.svg)", "broken local link"),
    (r"[Chart \[draft\]](assets/missing.svg)", "broken local link"),
    ("[Chart](assets/local(1).svg)", "not in the tracked bundle inventory"),
    ("[Chart](<assets/local(1).svg>)", "not in the tracked bundle inventory"),
    (r"[Chart](assets/local\(1\).svg)", "not in the tracked bundle inventory"),
    ("[Chart [draft]](../../public-files.json)", "escapes the standalone skill"),
    ("[Context [draft]](references/context.md#absent)", "incorrect anchor"),
])
def test_balanced_inline_syntax_preserves_resource_safeguards(bundle, markup, expected):
    add_resource(bundle, "assets/local(1).svg", declare=False, stage=False)
    with (bundle / SKILL / "SKILL.md").open("a", encoding="utf-8") as stream:
        stream.write("\n" + markup + "\n")
    result = validate(bundle)
    assert result.returncode == 1, result.stdout + result.stderr
    assert expected in result.stderr


def test_balanced_labels_count_as_direct_reference_links(bundle):
    entry = bundle / SKILL / "SKILL.md"
    entry.write_text(FRONTMATTER + "\n[Context [details]](references/context.md#details)\n")
    result = validate(bundle)
    assert result.returncode == 0, result.stdout + result.stderr


def test_inline_parser_ignores_examples_titles_and_malformed_destinations(bundle):
    entry = bundle / SKILL / "SKILL.md"
    with entry.open("a", encoding="utf-8") as stream:
        stream.write(r'''
`[Example [draft]](assets/missing(1).svg)`

```md
[Example [draft]](assets/missing(1).svg)
```

~~~md
[Example](<assets/missing(1).svg>)
~~~

\[Example](assets/missing.svg)
[Broken](assets/unbalanced(1.svg)
[Broken](<assets/missing.svg)
[Broken](assets/missing.svg "unclosed)
[Context](references/context.md "[Example](missing.svg)")
''')
    result = validate(bundle)
    assert result.returncode == 0, result.stdout + result.stderr


def test_inline_parser_handles_multiple_links_and_linked_images(bundle):
    add_resource(bundle, "assets/chart(1).svg", "<svg/>\n")
    entry = bundle / SKILL / "SKILL.md"
    with entry.open("a", encoding="utf-8") as stream:
        stream.write(
            '\n[![Chart [draft]](assets/chart(1).svg)](references/context.md#details) '
            '[Context](references/context.md "Details (1)")\n'
        )
    result = validate(bundle)
    assert result.returncode == 0, result.stdout + result.stderr
    # An ordinary link nested in another ordinary link only renders the inner link.
    with entry.open("a", encoding="utf-8") as stream:
        stream.write('\n[Outer [Context](references/context.md)](missing.md)\n')
    result = validate(bundle)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("heading,anchor", [
    ("An _important_ detail", "an-important-detail"),
    ("__Important__ detail", "important-detail"),
    ("___Important___ detail", "important-detail"),
    ("**An _important_ detail**", "an-important-detail"),
    ("_An **important** detail_", "an-important-detail"),
    ("[_Important_ detail](https://example.com)", "important-detail"),
    ("![An _important_ diagram](https://example.com/diagram.svg)", "an-important-diagram"),
    ("<em>_Important_</em> detail", "important-detail"),
    ("~~_Old_~~ detail", "old-detail"),
    ("A &amp; B", "a--b"),
    ("read_csv settings", "read_csv-settings"),
    ("`_literal_` settings", "_literal_-settings"),
    (r"\_literal\_ settings", "_literal_-settings"),
    ("_unclosed settings", "_unclosed-settings"),
    ("a_b_c settings", "a_b_c-settings"),
    ("_read_csv_ settings", "read_csv-settings"),
])
def test_accepts_anchors_from_heading_text_not_emphasis_markup(bundle, heading, anchor):
    reference = bundle / SKILL / "references/context.md"
    with reference.open("a", encoding="utf-8") as stream:
        stream.write(f"\n## {heading}\n")
    append_link(bundle, f"references/context.md#{anchor}")
    result = validate(bundle)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("heading,wrong_anchor", [
    ("An _important_ detail", "an-_important_-detail"),
    ("__Important__ detail", "__important__-detail"),
    ("___Important___ detail", "___important___-detail"),
    ("[_Important_ detail](https://example.com)", "_important_-detail"),
    ("read_csv settings", "readcsv-settings"),
    ("`_literal_` settings", "literal-settings"),
    (r"\_literal\_ settings", "literal-settings"),
    ("_unclosed settings", "unclosed-settings"),
])
def test_rejects_nonexistent_formatted_or_literal_heading_anchors(bundle, heading, wrong_anchor):
    reference = bundle / SKILL / "references/context.md"
    with reference.open("a", encoding="utf-8") as stream:
        stream.write(f"\n## {heading}\n")
    append_link(bundle, f"references/context.md#{wrong_anchor}")
    result = validate(bundle)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "incorrect anchor" in result.stderr


def test_formatted_headings_share_duplicate_anchor_namespace(bundle):
    reference = bundle / SKILL / "references/context.md"
    reference.write_text(
        "# Context\n\n## _Details_\n\n## Details\n\n## __Details__\n"
        "\n## Details-1\n\n## `Details`\n",
        encoding="utf-8",
    )
    for anchor in ("details", "details-1", "details-2", "details-1-1", "details-3"):
        append_link(bundle, f"references/context.md#{anchor}")
    result = validate(bundle)
    assert result.returncode == 0, result.stdout + result.stderr
    append_link(bundle, "references/context.md#details-4")
    result = validate(bundle)
    assert result.returncode == 1
    assert "incorrect anchor" in result.stderr


@pytest.mark.parametrize("markup", [
    r"\`[Resource](assets/missing.svg)\`",
    "`[Resource](assets/missing.svg)``",
    "``[Resource](assets/missing.svg)`",
    "`example` [Resource](assets/missing.svg)",
    r"`example \` [Resource](assets/missing.svg) `",
    r"\\\`[Resource](assets/missing.svg)\\\`",
])
def test_backtick_text_does_not_hide_live_resource_links(bundle, markup):
    tokens = MarkdownIt("commonmark").parseInline(markup)[0].children
    assert any(token.type == "link_open" and token.attrGet("href") == "assets/missing.svg"
               for token in tokens)
    with (bundle / SKILL / "SKILL.md").open("a", encoding="utf-8") as stream:
        stream.write("\n" + markup + "\n")
    result = validate(bundle)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "broken local link 'assets/missing.svg'" in result.stderr


@pytest.mark.parametrize("markup", [
    "`` `[Example](assets/missing.svg)` ``",
    "`` a ``` [Example](assets/missing.svg) ``",
    r"\\`[Example](assets/missing.svg)`",
    "`` [Example](assets/missing.svg) `` [Context](references/context.md#details)",
    "`unmatched ``[Example](assets/missing.svg)``",
])
def test_exact_backtick_spans_hide_only_code_examples(bundle, markup):
    tokens = MarkdownIt("commonmark").parseInline(markup)[0].children
    assert not any(token.type == "link_open" and token.attrGet("href") == "assets/missing.svg"
                   for token in tokens)
    with (bundle / SKILL / "SKILL.md").open("a", encoding="utf-8") as stream:
        stream.write("\n" + markup + "\n")
    result = validate(bundle)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("markup", [
    "[Resource](assets/missing`draft`.svg)",
    "[Resource](<assets/missing`draft`.svg>)",
    r"[Resource](assets/missing\`draft\`.svg)",
    "![Resource](assets/missing`draft`.svg)",
    "[Resource `label`](assets/missing`draft`.svg)",
    '[Resource](assets/missing`draft`.svg "Literal `title`")',
])
def test_backticks_in_destinations_preserve_resource_checks(bundle, markup):
    target = "assets/missing`draft`.svg"
    tokens = MarkdownIt("commonmark").parseInline(markup)[0].children
    assert any(
        unquote(token.attrGet("href") or token.attrGet("src") or "") == target
        for token in tokens
    )
    with (bundle / SKILL / "SKILL.md").open("a", encoding="utf-8") as stream:
        stream.write("\n" + markup + "\n")
    result = validate(bundle)
    assert result.returncode == 1, result.stdout + result.stderr
    assert f"broken local link {target!r}" in result.stderr


@pytest.mark.parametrize("title", ['"Use `"', "'Use `'", "(Use `)"])
def test_title_backticks_do_not_hide_following_live_links(bundle, title):
    markup = f"[Context](references/context.md {title}) [Resource](assets/missing.svg) `"
    tokens = MarkdownIt("commonmark").parseInline(markup)[0].children
    assert [token.attrGet("href") for token in tokens if token.type == "link_open"] == [
        "references/context.md", "assets/missing.svg",
    ]
    with (bundle / SKILL / "SKILL.md").open("a", encoding="utf-8") as stream:
        stream.write("\n" + markup + "\n")
    result = validate(bundle)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "broken local link 'assets/missing.svg'" in result.stderr


@pytest.mark.parametrize("markup", [
    "[Resource](assets/local`draft`.svg)",
    "[Resource](<assets/local`draft`.svg>)",
    "![Resource](assets/local`draft`.svg)",
    '[Resource](assets/local`draft`.svg "Use ` [Example](missing.svg)") `',
    '[![Resource](assets/local`draft`.svg)](references/context.md "Use `") `',
])
def test_accepts_packaged_backtick_destinations_and_literal_titles(bundle, markup):
    add_resource(bundle, "assets/local`draft`.svg", "<svg/>\n")
    with (bundle / SKILL / "SKILL.md").open("a", encoding="utf-8") as stream:
        stream.write("\n" + markup + "\n")
    result = validate(bundle)
    assert result.returncode == 0, result.stdout + result.stderr


def test_backtick_reference_name_counts_as_direct_entrypoint_link(bundle):
    add_resource(bundle, "references/code`example`.md", "# Example\n")
    append_link(bundle, "references/code`example`.md#example")
    result = validate(bundle)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("markup", [
    "[Not a `link](assets/missing.svg`)",
    "``[Example](assets/missing`draft`.svg)``",
    '[Context `literal ](missing.svg)`](references/context.md "`title`")',
])
def test_code_spans_still_take_precedence_inside_labels(bundle, markup):
    tokens = MarkdownIt("commonmark").parseInline(markup)[0].children
    assert not any(
        token.type == "link_open" and "missing" in (token.attrGet("href") or "")
        for token in tokens
    )
    with (bundle / SKILL / "SKILL.md").open("a", encoding="utf-8") as stream:
        stream.write("\n" + markup + "\n")
    result = validate(bundle)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("markup", [
    "```literal code```\n\n[Resource](assets/missing.svg)",
    "```language`extra\n[Resource](assets/missing.svg)",
    "```language\\`extra\n[Resource](assets/missing.svg)",
    "   ```literal code```\n\n[Resource](assets/missing.svg)",
    "````literal ``` code```` [Resource](assets/missing.svg)",
    "```literal code``` [Resource](assets/missing.svg)",
    "```literal code``` ![Resource](assets/missing.svg)",
])
def test_invalid_backtick_fence_info_does_not_hide_live_resources(bundle, markup):
    # Parse blocks too: parseInline cannot distinguish a fence from inline code.
    tokens = MarkdownIt("commonmark").parse(markup)
    assert not any(token.type == "fence" for token in tokens)
    assert any(
        (child.type == "link_open" and child.attrGet("href") == "assets/missing.svg")
        or (child.type == "image" and child.attrGet("src") == "assets/missing.svg")
        for token in tokens for child in token.children or []
    )
    with (bundle / SKILL / "SKILL.md").open("a", encoding="utf-8") as stream:
        stream.write("\n" + markup + "\n")
    result = validate(bundle)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "broken local link 'assets/missing.svg'" in result.stderr


@pytest.mark.parametrize("prefix", [
    "```literal code```",
    "```language`extra",
    "```language\\`extra",
    "   ````literal code````",
])
def test_invalid_backtick_fence_info_keeps_live_heading_anchors(bundle, prefix):
    markup = f"# Context\n\n{prefix}\n\n## Details\n"
    tokens = MarkdownIt("commonmark").parse(markup)
    assert not any(token.type == "fence" for token in tokens)
    assert any(token.type == "heading_open" and token.tag == "h2" for token in tokens)
    (bundle / SKILL / "references/context.md").write_text(markup, encoding="utf-8")
    result = validate(bundle)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("opener,closer", [
    ("```", "```"),
    ("```md", "```"),
    ("   ```md", "  ```` \t"),
    ("```md ~~~", "```"),
    ("~~~md", "~~~"),
    ("~~~md ``` ~~~", "~~~"),
    ("   ~~~~md `extra`", " ~~~~~ \t"),
])
def test_valid_fences_hide_examples_and_exclude_heading_anchors(bundle, opener, closer):
    markup = (
        f"# Context\n\n{opener}\n[Example](missing.md)\n## Details\n"
        f"{closer}\n\n## Details\n"
    )
    tokens = MarkdownIt("commonmark").parse(markup)
    assert sum(token.type == "fence" for token in tokens) == 1
    assert sum(token.type == "heading_open" and token.tag == "h2" for token in tokens) == 1
    (bundle / SKILL / "references/context.md").write_text(markup, encoding="utf-8")
    result = validate(bundle)
    assert result.returncode == 0, result.stdout + result.stderr
    append_link(bundle, "references/context.md#details-1")
    result = validate(bundle)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "incorrect anchor" in result.stderr


@pytest.mark.parametrize("opener,non_closer,closer", [
    ("````md", "```", "````"),
    ("```md", "~~~", "```"),
    ("```md", "``` extra", "```"),
    ("```md", "```literal`info", "```"),
    ("```md", "    ```", "```"),
    ("~~~md", "~~~ extra", "~~~"),
    ("~~~md", "```", "~~~"),
    ("~~~~md", "~~~", "~~~~"),
])
def test_only_matching_bare_fences_end_code_blocks(bundle, opener, non_closer, closer):
    markup = f"{opener}\n{non_closer}\n[Example](missing.md)\n{closer}\n"
    tokens = MarkdownIt("commonmark").parse(markup)
    assert len(tokens) == 1 and tokens[0].type == "fence"
    assert "[Example](missing.md)" in tokens[0].content
    with (bundle / SKILL / "SKILL.md").open("a", encoding="utf-8") as stream:
        stream.write("\n" + markup + "\n")
    result = validate(bundle)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("opener", ["```md", "~~~md", "~~~md `extra`", "```~~~"])
def test_valid_unclosed_fences_hide_examples_to_end_of_document(bundle, opener):
    markup = f"{opener}\n[Example](missing.md)\n"
    tokens = MarkdownIt("commonmark").parse(markup)
    assert len(tokens) == 1 and tokens[0].type == "fence"
    with (bundle / SKILL / "SKILL.md").open("a", encoding="utf-8") as stream:
        stream.write("\n" + markup)
    result = validate(bundle)
    assert result.returncode == 0, result.stdout + result.stderr


def test_invalid_backtick_info_does_not_prevent_later_real_fences(bundle):
    markup = (
        "```literal code```\n\n~~~md\n[Example](missing.md)\n~~~\n"
        "[Context](references/context.md#details)\n"
    )
    tokens = MarkdownIt("commonmark").parse(markup)
    assert sum(token.type == "fence" for token in tokens) == 1
    assert any(
        child.type == "link_open" and child.attrGet("href") == "references/context.md#details"
        for token in tokens for child in token.children or []
    )
    (bundle / SKILL / "SKILL.md").write_text(FRONTMATTER + "\n" + markup, encoding="utf-8")
    result = validate(bundle)
    assert result.returncode == 0, result.stdout + result.stderr
