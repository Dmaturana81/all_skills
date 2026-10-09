#!/usr/bin/env python3
"""Structural checks for a layered agent wiki directory.

Checks that the layer files exist, every domain is routed from ``01_MAP.md``,
every topic and decision is listed in ``topics/README.md``, every planning
artifact under ``meta/`` is reachable from the ``meta/INDEX.md`` hub, and every
relative markdown link resolves.

Usage:
    validate_wiki.py <wiki_directory>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Sequence

REQUIRED = [
    "00_BOOT.md",
    "01_MAP.md",
    "README.md",
    "meta/AGENT_PROTOCOL.md",
    "meta/CHANGELOG.md",
    "meta/DRAFT_CURSOR_RULE.md",
    "topics/README.md",
    "reference/file-map.md",
]

PLANNING_DIRS = ("wayfinding", "sdlc-artifacts", "research", "prototypes")
BOOT_MAX_LINES = 120
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
FENCE_RE = re.compile(r"^```.*?^```", re.DOTALL | re.MULTILINE)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def link_targets(text: str) -> List[str]:
    """Relative link targets in markdown, ignoring code fences and comments."""
    scan = FENCE_RE.sub("", COMMENT_RE.sub("", text))
    return [
        t.split("#", 1)[0]
        for t in LINK_RE.findall(scan)
        if not re.match(r"^[a-z]+:", t) and not t.startswith("#")
    ]


def check_required(root: Path) -> List[str]:
    """Missing layer files and an empty ``domains/``."""
    errors = [f"Missing required file: {rel}" for rel in REQUIRED if not (root / rel).is_file()]
    domains = root / "domains"
    if not domains.is_dir():
        errors.append("Missing domains/")
    elif not list(domains.glob("*.md")):
        errors.append("domains/ has no .md files")
    return errors


def check_routing(root: Path) -> List[str]:
    """Every domain is linked from the L1 router, and L0 stays lean."""
    errors: List[str] = []
    map_text = _read(root / "01_MAP.md")
    for domain_file in sorted((root / "domains").glob("*.md")):
        if f"domains/{domain_file.stem}" not in map_text:
            errors.append(f"Domain not linked from 01_MAP.md: {domain_file.stem}")
    boot = root / "00_BOOT.md"
    if boot.is_file() and len(_read(boot).splitlines()) > BOOT_MAX_LINES:
        errors.append(f"00_BOOT.md may be too long (>{BOOT_MAX_LINES} lines) — keep L0 lean")
    return errors


def _unlisted(index: Path, files: Sequence[Path]) -> List[Path]:
    targets = {(index.parent / t).resolve() for t in link_targets(_read(index))}
    return [f for f in files if f.resolve() not in targets]


def check_topics_indexed(root: Path) -> List[str]:
    """Every L3 topic and decision record appears in ``topics/README.md``."""
    index = root / "topics" / "README.md"
    if not index.is_file():
        return []
    files = sorted(p for p in (root / "topics").rglob("*.md") if p.name != "README.md")
    return [f"Not listed in topics/README.md: {p.relative_to(root)}" for p in _unlisted(index, files)]


def check_planning_hub(root: Path) -> List[str]:
    """Planning artifacts under ``meta/`` are reachable from ``meta/INDEX.md``.

    Each planning folder needs its own ``INDEX.md`` listing its files; the hub
    links each folder index; ``01_MAP.md`` links the hub. Wayfinding indexes
    list maps only (tickets are indexed per map and checked by wayfinding.py).
    """
    meta = root / "meta"
    present = [d for d in PLANNING_DIRS if (meta / d).is_dir()]
    if not present:
        return []
    errors: List[str] = []
    hub = meta / "INDEX.md"
    if not hub.is_file():
        errors.append("meta/INDEX.md hub missing (planning artifacts exist under meta/)")
    elif "meta/INDEX.md" not in _read(root / "01_MAP.md"):
        errors.append("01_MAP.md does not link meta/INDEX.md")
    for name in present:
        folder = meta / name
        index = folder / "INDEX.md"
        if not index.is_file():
            errors.append(f"Missing meta/{name}/INDEX.md")
            continue
        if hub.is_file() and index.resolve() not in {(meta / t).resolve() for t in link_targets(_read(hub))}:
            errors.append(f"meta/INDEX.md does not link {name}/INDEX.md")
        pattern = "*/MAP.md" if name == "wayfinding" else "**/*.md"
        files = sorted(p for p in folder.glob(pattern) if p != index)
        errors += [f"Not listed in meta/{name}/INDEX.md: {p.relative_to(root)}" for p in _unlisted(index, files)]
    return errors


def check_links(root: Path) -> List[str]:
    """Relative links anywhere in the wiki resolve to an existing path."""
    errors: List[str] = []
    for page in sorted(root.rglob("*.md")):
        for target in link_targets(_read(page)):
            if target and not (page.parent / target).exists():
                errors.append(f"Broken link in {page.relative_to(root)}: {target}")
    return errors


def validate(root: Path) -> List[str]:
    """Run every check and return all errors."""
    return (
        check_required(root)
        + check_routing(root)
        + check_topics_indexed(root)
        + check_planning_hub(root)
        + check_links(root)
    )


def main(argv: Sequence[str]) -> int:
    if len(argv) != 2:
        print("Usage: validate_wiki.py <wiki_directory>", file=sys.stderr)
        return 2
    root = Path(argv[1]).resolve()
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 1
    errors = validate(root)
    if errors:
        print("Wiki validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    topics = [p for p in (root / "topics").rglob("*.md") if p.name != "README.md"]
    print(f"Wiki validation OK: {root}")
    print(f"  Domains: {len(list((root / 'domains').glob('*.md')))}")
    print(f"  Topics: {len(topics)}")
    print(f"  Planning folders: {', '.join(d for d in PLANNING_DIRS if (root / 'meta' / d).is_dir()) or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
