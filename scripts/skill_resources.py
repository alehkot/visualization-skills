"""Validate contained local reference links."""
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote, urlsplit

def unfenced_lines(text: str) -> list[tuple[int, str]]:
    """Return numbered Markdown lines outside backtick and tilde fences."""
    result = []
    fence: tuple[str, int] | None = None
    for number, line in enumerate(text.splitlines(), 1):
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if match:
            marker, tail = match.groups()
            if fence is None:
                fence = (marker[0], len(marker))
            elif marker[0] == fence[0] and len(marker) >= fence[1] and not tail.strip():
                fence = None
            continue
        if fence is None:
            result.append((number, line))
    return result


def markdown_headings(text: str) -> list[tuple[int, int, str, str]]:
    """Return ATX headings with GitHub-style, duplicate-aware fragment IDs."""
    result = []
    used: set[str] = set()
    for number, line in unfenced_lines(text):
        match = re.match(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        marks, title = match.groups()
        plain = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", title)
        plain = re.sub(r"<[^>]+>", "", plain).lower()
        base = "".join(
            char for char in plain if char in "-_ " or unicodedata.category(char)[0] in {"L", "N"}
        ).replace(" ", "-")
        anchor = base
        suffix = 0
        while anchor in used:
            suffix += 1
            anchor = f"{base}-{suffix}"
        used.add(anchor)
        result.append((number, len(marks), title, anchor))
    return result


def markdown_links(text: str) -> list[str]:
    """Read inline link destinations outside fenced examples and inline code."""
    result = []
    for _, line in unfenced_lines(text):
        # Code spans are examples, not resource links.
        line = re.sub(r"(`+)(.*?)\1", lambda m: " " * len(m[0]), line)
        for match in re.finditer(r"\[[^\]\n]*\]\(([^)\n]+)\)", line):
            target = match[1].strip()
            if target.startswith("<"):
                target = target[1:].split(">", 1)[0]
            else:
                target = target.split(' "', 1)[0].split(" '", 1)[0]
            result.append(target)
    return result


def validate_reference_resources(skill_dir: Path, bundle_files: frozenset[Path]) -> None:
    """Require relative links to bundled resources and valid anchors."""
    root = skill_dir.resolve()
    skill_md = root / "SKILL.md"
    references = root / "references"
    paths = sorted(references.rglob("*.md")) if references.is_dir() else []
    for path in paths:
        if path.parent != references:
            raise ValueError(f"{path}: references must stay one level deep")
    linked: set[Path] = set()
    for path in [skill_md, *paths]:
        if path not in bundle_files:
            raise ValueError(f"{path}: resource is not in the tracked bundle inventory")
        for target in markdown_links(path.read_text(encoding="utf-8")):
            parts = urlsplit(target)
            if parts.scheme == "file" or re.match(r"^[A-Za-z]:[/\\]", unquote(target)):
                raise ValueError(f"{path}: local link {target!r} must use a relative path")
            if parts.scheme or parts.netloc:
                continue
            local_path = Path(unquote(parts.path))
            if local_path.is_absolute():
                raise ValueError(f"{path}: local link {target!r} must use a relative path")
            candidate = path.parent / local_path if parts.path else path
            # Check the spelled path before resolving it: an unshipped symlink
            # can otherwise make a local-only alias look like a bundled target.
            if any(part.is_symlink() for part in (candidate, *candidate.parents)):
                raise ValueError(f"{path}: local link {target!r} uses a symlink")
            resolved = candidate.resolve()
            if not resolved.is_relative_to(root):
                raise ValueError(f"{path}: link {target!r} escapes the standalone skill")
            if not resolved.is_file():
                raise ValueError(f"{path}: broken local link {target!r}")
            if resolved not in bundle_files:
                raise ValueError(
                    f"{path}: local link {target!r} is not in the tracked bundle inventory"
                )
            if parts.fragment and resolved.suffix == ".md":
                anchors = {h[3] for h in markdown_headings(resolved.read_text(encoding="utf-8"))}
                if unquote(parts.fragment) not in anchors:
                    raise ValueError(f"{path}: incorrect anchor in {target!r}")
            if path == skill_md:
                linked.add(resolved)
    for path in paths:
        if path.resolve() not in linked:
            raise ValueError(f"{path}: reference file is never linked directly from SKILL.md")
