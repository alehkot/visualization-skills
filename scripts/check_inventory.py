"""Check the exact tracked bundle inventory; no network access is needed."""

import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def check_inventory() -> frozenset[Path]:
    """Validate the inventory and return its absolute, tracked file paths."""
    allowed = json.loads((ROOT / "public-files.json").read_text())
    if not isinstance(allowed, list) or len(allowed) != len(set(allowed)):
        raise ValueError("The bundle inventory must contain unique file paths")
    output = subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-files", "--stage", "-z"], text=True
    )
    tracked = set()
    for entry in output.split("\0"):
        if not entry:
            continue
        metadata, name = entry.split("\t", 1)
        mode, _, stage = metadata.split()
        if mode not in {"100644", "100755"} or stage != "0":
            raise ValueError(f"Expected an ordinary tracked file: {name}")
        tracked.add(name)
    if tracked != set(allowed):
        raise ValueError(
            f"Bundle inventory differs: missing={sorted(set(allowed) - tracked)}, "
            f"unexpected={sorted(tracked - set(allowed))}"
        )
    for name in allowed:
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Bundle paths must be relative and contained")
        path = ROOT / relative
        if not path.is_file() or any(
            (ROOT / Path(*relative.parts[:n])).is_symlink()
            for n in range(1, len(relative.parts) + 1)
        ):
            raise ValueError(f"Expected an ordinary file without symlinks: {name}")
    return frozenset((ROOT / name).resolve() for name in allowed)
