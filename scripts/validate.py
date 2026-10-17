from __future__ import annotations
import re
import sys
from pathlib import Path

import yaml

try:
    from scripts.skill_resources import validate_reference_resources
    from scripts.check_inventory import check_inventory
except ModuleNotFoundError:
    from skill_resources import validate_reference_resources
    from check_inventory import check_inventory


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"


def validate_frontmatter(skill_dir: Path) -> None:
    path = skill_dir / "SKILL.md"
    if not path.exists():
        raise ValueError(f"{skill_dir}: missing SKILL.md")
    content = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        raise ValueError(f"{path}: missing YAML frontmatter")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: frontmatter must be a mapping")
    for field in ("name", "description"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ValueError(f"{path}: {field} must be a nonempty string")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", data["name"]) or len(data["name"]) > 64:
        raise ValueError(f"{path}: invalid skill name")
    if data["name"] != skill_dir.name:
        raise ValueError(f"{path}: name must match directory name {skill_dir.name}")
    if len(data["description"]) > 1024:
        raise ValueError(f"{path}: description must be 1024 characters or fewer")


def validate_markdown_references(skill_dir: Path, bundle_files: frozenset[Path]) -> None:
    validate_reference_resources(skill_dir, bundle_files)


def validate_skill_files(skill_dir: Path) -> None:
    forbidden = ("README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md")
    for name in forbidden:
        if (skill_dir / name).exists():
            raise ValueError(f"{skill_dir / name}: do not include auxiliary docs in skills")
    for ref_dir in ("references", "scripts", "assets"):
        path = skill_dir / ref_dir
        if path.exists() and not path.is_dir():
            raise ValueError(f"{path}: expected a directory")


def run_checks() -> int:
    bundle_files = check_inventory()
    skill_dirs = sorted(
        path for path in SKILLS_DIR.iterdir() if path.is_dir() and not path.name.startswith(".")
    )
    if not skill_dirs:
        raise ValueError("No skills found")
    for skill_dir in skill_dirs:
        validate_frontmatter(skill_dir)
        validate_skill_files(skill_dir)
        validate_markdown_references(skill_dir, bundle_files)
    print(f"Validated {len(skill_dirs)} deployable skills.")
    return 0


def main() -> int:
    try:
        return run_checks()
    except (ValueError, OSError) as error:
        print(f"validation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
