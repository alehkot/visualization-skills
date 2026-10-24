"""Validate contained local reference links."""
from pathlib import Path
import re
import string
import unicodedata
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt


_HEADING_MARKDOWN = MarkdownIt("commonmark").enable("strikethrough")


def _heading_text(title: str) -> str:
    """Read inline text without confusing emphasis with literal underscores."""
    def collect(tokens):
        return "".join(
            collect(token.children) if token.children else token.content
            for token in tokens
            if token.type in {"text", "code_inline", "image"}
        )

    return collect(_HEADING_MARKDOWN.parseInline(title)[0].children or [])


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
        plain = _heading_text(title).lower()
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


def _inline_destination(line: str, start: int) -> tuple[str, int] | None:
    """Read a single-line inline destination and its optional title."""
    index = start
    while index < len(line) and line[index] in " \t":
        index += 1
    angle = index < len(line) and line[index] == "<"
    if angle:
        index += 1
    target = []
    depth = 0
    while index < len(line):
        char = line[index]
        if char == "\\" and index + 1 < len(line) and line[index + 1] in string.punctuation:
            target.append(line[index + 1])
            index += 2
            continue
        if angle:
            if char == ">":
                index += 1
                break
            if char == "<":
                return None
        else:
            if char in " \t" or (char == ")" and depth == 0):
                break
            if ord(char) < 32 or ord(char) == 127:
                return None
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
        target.append(char)
        index += 1
    else:
        return None
    if depth:
        return None
    before_space = index
    while index < len(line) and line[index] in " \t":
        index += 1
    if index < len(line) and line[index] == ")":
        return "".join(target), index + 1
    # A title must be separated from the destination by whitespace.
    if index == before_space or index >= len(line) or line[index] not in "\"'(":
        return None
    opener = line[index]
    closer = ")" if opener == "(" else opener
    index += 1
    while index < len(line):
        char = line[index]
        if char == "\\" and index + 1 < len(line) and line[index + 1] in string.punctuation:
            index += 2
            continue
        if char == closer:
            index += 1
            break
        if opener == "(" and char == "(":
            return None
        index += 1
    else:
        return None
    while index < len(line) and line[index] in " \t":
        index += 1
    if index < len(line) and line[index] == ")":
        return "".join(target), index + 1
    return None


def markdown_links(text: str) -> list[str]:
    """Read single-line inline links, including balanced labels/destinations."""
    result = []
    for _, line in unfenced_lines(text):
        # Code spans are examples, not resource links.
        line = re.sub(r"(`+)(.*?)\1", lambda m: " " * len(m[0]), line)
        brackets: list[tuple[bool, bool]] = []
        index = 0
        while index < len(line):
            char = line[index]
            if char == "\\" and index + 1 < len(line) and line[index + 1] in string.punctuation:
                index += 2
                continue
            if char == "[":
                brackets.append((index > 0 and line[index - 1] == "!", False))
            elif char == "]" and brackets:
                image, contains_link = brackets.pop()
                if (image or not contains_link) and line[index + 1:index + 2] == "(":
                    parsed = _inline_destination(line, index + 2)
                    if parsed is not None:
                        target, index = parsed
                        result.append(target)
                        if not image:
                            # Ordinary links cannot contain another link; images can.
                            brackets = [(is_image, True) for is_image, _ in brackets]
                        continue
            index += 1
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
