"""Check local resource portability through the real validator and Git index."""

import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


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
