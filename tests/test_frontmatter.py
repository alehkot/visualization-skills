"""Exercise frontmatter parsing through the validator CLI and a real Git index."""

import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
HEADER = "name: example\ndescription: A test skill.\n"


@pytest.fixture
def bundle(tmp_path):
    (tmp_path / "scripts").mkdir()
    for name in ("check_inventory.py", "skill_resources.py", "validate.py"):
        shutil.copyfile(ROOT / "scripts" / name, tmp_path / "scripts" / name)
    (tmp_path / "skills/example").mkdir(parents=True)
    (tmp_path / "skills/example/SKILL.md").write_text("", encoding="utf-8")
    names = ["public-files.json", "skills/example/SKILL.md", *[
        f"scripts/{name}" for name in ("check_inventory.py", "skill_resources.py", "validate.py")
    ]]
    (tmp_path / "public-files.json").write_text(json.dumps(names), encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, timeout=10)
    subprocess.run(["git", "add", "--", *names], cwd=tmp_path, check=True, timeout=10)
    return tmp_path


def validate(bundle, content):
    # write_bytes deliberately preserves CRLF for the portability control.
    (bundle / "skills/example/SKILL.md").write_bytes(content.encode("utf-8"))
    return subprocess.run(
        [sys.executable, "scripts/validate.py"], cwd=bundle,
        capture_output=True, text=True, timeout=15,
    )


def assert_rejected(result, message):
    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout == ""
    assert result.stderr.startswith("validation failed: ")
    assert "skills/example/SKILL.md" in result.stderr
    assert message in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("closing", [
    "---oops", "----", "--- trailing text", "---\ttrailing text", "--- # comment",
])
def test_rejects_delimiter_prefixes(bundle, closing):
    result = validate(bundle, f"---\n{HEADER}{closing}\n# Example\n")
    assert_rejected(result, "standalone --- lines")


@pytest.mark.parametrize("content", [
    HEADER + "---\n# Example\n",
    "\n---\n" + HEADER + "---\n",
    "---oops\n" + HEADER + "---\n",
    "---\n" + HEADER,
    "---\n" + HEADER + "  ---\n",
])
def test_requires_opening_and_closing_lines(bundle, content):
    assert_rejected(validate(bundle, content), "frontmatter")


@pytest.mark.parametrize("header", [
    "name: example\ndescription: [broken\n",
    "name: example\ndescription: \"unfinished\n",
    "name: example\ndescription: *unknown\n",
    "name: example\ndescription: !!python/object:untrusted.Type {}\n",
    "name: example\ndescription: Test\nmetadata:\n  key: value\n other: value\n",
])
def test_yaml_errors_use_normal_validation_diagnostic(bundle, header):
    result = validate(bundle, f"---\n{header}---\n# Example\n")
    assert_rejected(result, "invalid YAML frontmatter")
    assert "<unicode string>" not in result.stderr


def test_yaml_diagnostic_uses_skill_file_coordinates(bundle):
    result = validate(bundle, "---\nname: example\ndescription: *unknown\n---\n")
    assert_rejected(result, "SKILL.md:3:14: invalid YAML frontmatter")


@pytest.mark.parametrize("header,expected", [
    ("", "frontmatter"),
    ("- example\n", "frontmatter must be a mapping"),
    ("name: example\n", "description must be a nonempty string"),
    ("name: other\ndescription: Fine\n", "name must match directory name"),
    ("name: example\ndescription: 42\n", "description must be a nonempty string"),
    ("name: example\ndescription: " + "x" * 1025 + "\n", "1024 characters or fewer"),
])
def test_preserves_frontmatter_semantic_checks(bundle, header, expected):
    assert_rejected(validate(bundle, f"---\n{header}---\n"), expected)


@pytest.mark.parametrize("content", [
    "---\n" + HEADER + "---\n# Example\n",
    "---\n" + HEADER + "---",
    "--- \t\n" + HEADER + "--- \t\n# Example\n",
    ("---\n" + HEADER + "---\n# Example\n").replace("\n", "\r\n"),
    "---\nname: example\ndescription: |\n  Explain this:\n  ---\n  More detail.\n---\n",
    "---\nname: example\ndescription: >\n  Explain difficult\n  information.\n---\n",
    "---\n" + HEADER + "---extra: a valid YAML key\n---\n",
    "---\n" + HEADER + "metadata:\n  author: Example\n  version: '1.0'\n---\n",
    "---\n" + HEADER + "---\n# Body\nThis is not: [valid YAML\n---\n",
    "---\nname: example\ndescription: &description A test skill.\nmetadata:\n  summary: *description\n---\n",
])
def test_accepts_valid_frontmatter_and_ignores_body_yaml(bundle, content):
    result = validate(bundle, content)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == "Validated 1 deployable skills.\n"
    assert result.stderr == ""


def test_yaml_reader_error_still_has_filename_and_no_traceback(bundle):
    result = validate(bundle, "---\nname: example\ndescription: bad\x00text\n---\n")
    assert_rejected(result, "invalid YAML frontmatter")
