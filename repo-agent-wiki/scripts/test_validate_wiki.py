"""Tests for validate_wiki.py. Run with: pytest repo-agent-wiki/scripts/"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import validate_wiki as vw  # noqa: E402


def write(root: Path, rel: str, text: str = "x\n") -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def wiki(tmp_path: Path) -> Path:
    root = tmp_path / "wiki_shop"
    for rel in vw.REQUIRED:
        write(root, rel)
    write(root, "01_MAP.md", "[ordering](domains/ordering.md)\n")
    write(root, "domains/ordering.md")
    write(root, "topics/decisions/0001-full-cancel.md")
    write(root, "topics/README.md", "[0001](decisions/0001-full-cancel.md)\n")
    return root


def test_minimal_wiki_passes(wiki: Path) -> None:
    assert vw.validate(wiki) == []


def test_unrouted_domain_fails(wiki: Path) -> None:
    write(wiki, "domains/billing.md")
    assert "Domain not linked from 01_MAP.md: billing" in vw.validate(wiki)


def test_unlisted_decision_fails(wiki: Path) -> None:
    write(wiki, "topics/decisions/0002-events.md")
    assert any("0002-events.md" in e for e in vw.check_topics_indexed(wiki))


def test_planning_folder_requires_hub_and_folder_index(wiki: Path) -> None:
    write(wiki, "meta/research/allocation.md")
    errors = vw.check_planning_hub(wiki)
    assert any("hub missing" in e for e in errors)
    assert "Missing meta/research/INDEX.md" in errors


def test_fully_indexed_planning_passes(wiki: Path) -> None:
    write(wiki, "01_MAP.md", "[ordering](domains/ordering.md)\n[hub](meta/INDEX.md)\n")
    write(wiki, "meta/INDEX.md", "[r](research/INDEX.md)\n[w](wayfinding/INDEX.md)\n")
    write(wiki, "meta/research/allocation.md")
    write(wiki, "meta/research/INDEX.md", "[Allocation](allocation.md)\n")
    write(wiki, "meta/wayfinding/partial/MAP.md")
    write(wiki, "meta/wayfinding/partial/tickets/0001-x.md")
    write(wiki, "meta/wayfinding/INDEX.md", "[Partial](partial/MAP.md)\n")
    assert vw.validate(wiki) == []


def test_unlisted_research_note_fails(wiki: Path) -> None:
    write(wiki, "meta/INDEX.md", "[r](research/INDEX.md)\n")
    write(wiki, "meta/research/INDEX.md", "nothing\n")
    write(wiki, "meta/research/allocation.md")
    assert "Not listed in meta/research/INDEX.md: meta/research/allocation.md" in vw.check_planning_hub(wiki)


def test_hub_must_be_routed_from_map(wiki: Path) -> None:
    write(wiki, "meta/INDEX.md", "[r](research/INDEX.md)\n")
    write(wiki, "meta/research/INDEX.md")
    assert "01_MAP.md does not link meta/INDEX.md" in vw.check_planning_hub(wiki)


def test_broken_link_fails_but_code_fences_are_ignored(wiki: Path) -> None:
    write(wiki, "domains/ordering.md", "[gone](../topics/missing.md)\n```\n[example](nowhere.md)\n```\n")
    assert vw.check_links(wiki) == ["Broken link in domains/ordering.md: ../topics/missing.md"]
