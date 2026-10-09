"""Tests for wayfinding.py. Run with: pytest wayfinder-wiki/scripts/"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import wayfinding as wf  # noqa: E402

MAP_TEMPLATE = """---
layer: meta
kind: wayfinder-map
effort: {slug}
status: {status}
parent: ../INDEX.md
---

# Partial cancellation

## Destination

A spec for cancelling single line items.

## Notes

Consult /domain-modeling-wiki.

## Decisions so far

{decisions}

## Not yet specified

{fog}

## Out of scope

{out_of_scope}
"""


def write_ticket(
    effort_dir: Path,
    ticket_id: int,
    title: str,
    *,
    ticket_type: str = "grilling",
    mode: str = "HITL",
    status: str = "open",
    assignee: str = "",
    blocked_by: Sequence[int] = (),
    resolution: str = "",
) -> Path:
    blockers = ", ".join(f'"{b:04d}"' for b in blocked_by)
    body = f"# {title}\n\n## Question\n\nWhat about {title}?\n"
    if resolution:
        body += f"\n## Resolution\n\n{resolution}\n"
    path = effort_dir / "tickets" / f"{ticket_id:04d}-{wf.slugify(title)}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\nlayer: meta\nkind: wayfinder-ticket\n"
        f"effort: {effort_dir.name}\nid: \"{ticket_id:04d}\"\ntype: {ticket_type}\nmode: {mode}\n"
        f"status: {status}\nassignee: {assignee}\nblocked_by: [{blockers}]\nparent: ../MAP.md\n---\n\n{body}",
        encoding="utf-8",
    )
    return path


def write_map(effort_dir: Path, *, status: str = "active", decisions: str = "", fog: str = "", out_of_scope: str = "") -> None:
    effort_dir.mkdir(parents=True, exist_ok=True)
    (effort_dir / "MAP.md").write_text(
        MAP_TEMPLATE.format(slug=effort_dir.name, status=status, decisions=decisions, fog=fog, out_of_scope=out_of_scope),
        encoding="utf-8",
    )


@pytest.fixture
def wiki(tmp_path: Path) -> Path:
    """A consistent wiki: one closed ticket, one open blocked, one open frontier."""
    wiki_dir = tmp_path / "wiki_shop"
    effort = wiki_dir / "meta" / "wayfinding" / "partial-cancel"
    write_map(effort, decisions="- [What is an order line](tickets/0001-what-is-an-order-line.md): a priced SKU row")
    write_ticket(effort, 1, "What is an order line", status="closed", resolution="A priced SKU row.")
    write_ticket(effort, 2, "Refund timing", blocked_by=[3])
    write_ticket(effort, 3, "Allocation granularity", ticket_type="research", mode="AFK", blocked_by=[1])
    wf.write_indexes(wiki_dir)
    return wiki_dir


def effort_of(wiki_dir: Path) -> Path:
    return wiki_dir / "meta" / "wayfinding" / "partial-cancel"


class TestFrontmatter:
    def test_parses_scalars_inline_lists_and_block_lists(self) -> None:
        fm = wf.parse_frontmatter('id: "0003"\nblocked_by: ["0001", 2]\nread_when:\n  - order\n  - cancel\nassignee:\n')
        assert wf.scalar(fm, "id") == "0003"
        assert wf.listing(fm, "blocked_by") == ["0001", "2"]
        assert wf.listing(fm, "read_when") == ["order", "cancel"]
        assert wf.scalar(fm, "assignee") == ""

    def test_strips_trailing_comments(self) -> None:
        assert wf.scalar(wf.parse_frontmatter("status: open  # charting soon"), "status") == "open"

    def test_rejects_garbage_line(self) -> None:
        with pytest.raises(wf.WayfindingError):
            wf.parse_frontmatter("this is not yaml")


class TestFrontier:
    def test_only_open_unblocked_unclaimed(self, wiki: Path) -> None:
        effort, _ = wf.load_effort(effort_of(wiki))
        assert [t.id for t in wf.frontier(effort.tickets)] == [3]

    def test_claimed_ticket_leaves_frontier(self, wiki: Path) -> None:
        wf.claim(effort_of(wiki), 3, "matu")
        effort, _ = wf.load_effort(effort_of(wiki))
        assert wf.frontier(effort.tickets) == []

    def test_out_of_scope_blocker_unblocks(self, tmp_path: Path) -> None:
        effort = tmp_path / "e"
        write_map(effort)
        write_ticket(effort, 1, "Storefront", status="out-of-scope", resolution="Beyond the destination.")
        write_ticket(effort, 2, "Depends on storefront", blocked_by=[1])
        loaded, _ = wf.load_effort(effort)
        assert [t.id for t in wf.frontier(loaded.tickets)] == [2]


class TestMutations:
    def test_next_id_starts_at_one(self, tmp_path: Path) -> None:
        assert wf.next_id(tmp_path) == 1

    def test_new_ticket_takes_next_id_and_wires_blockers(self, wiki: Path) -> None:
        path = wf.new_ticket(effort_of(wiki), "prototype", "Cancel button states", blocked_by=[2])
        ticket = wf.load_ticket(path)
        assert path.name == "0004-cancel-button-states.md"
        assert (ticket.id, ticket.mode, ticket.blocked_by, ticket.status) == (4, "HITL", (2,), "open")

    def test_new_ticket_rejects_unknown_blocker(self, wiki: Path) -> None:
        with pytest.raises(wf.WayfindingError, match="Unknown blocker"):
            wf.new_ticket(effort_of(wiki), "grilling", "X", blocked_by=[99])

    def test_new_ticket_rejects_research_in_hitl_mode(self, wiki: Path) -> None:
        with pytest.raises(wf.WayfindingError, match="cannot be HITL"):
            wf.new_ticket(effort_of(wiki), "research", "X", mode="HITL")

    def test_claim_refuses_someone_elses_ticket(self, wiki: Path) -> None:
        wf.claim(effort_of(wiki), 3, "matu")
        with pytest.raises(wf.WayfindingError, match="already claimed"):
            wf.claim(effort_of(wiki), 3, "other")

    def test_claim_refuses_blocked_unless_forced(self, wiki: Path) -> None:
        with pytest.raises(wf.WayfindingError, match="still blocked"):
            wf.claim(effort_of(wiki), 2, "matu")
        assert wf.claim(effort_of(wiki), 2, "matu", force=True).assignee == "matu"

    def test_claim_refuses_closed(self, wiki: Path) -> None:
        with pytest.raises(wf.WayfindingError, match="closed"):
            wf.claim(effort_of(wiki), 1, "matu")


class TestCheck:
    def test_consistent_wiki_passes(self, wiki: Path) -> None:
        errors, maps, tickets = wf.check_wiki(wiki)
        assert errors == []
        assert (maps, tickets) == (1, 3)

    def test_wiki_without_wayfinding_passes(self, tmp_path: Path) -> None:
        assert wf.check_wiki(tmp_path) == ([], 0, 0)

    def test_stale_index_after_claim(self, wiki: Path) -> None:
        wf.claim(effort_of(wiki), 3, "matu")
        assert any("stale" in e for e in wf.check_wiki(wiki)[0])

    def test_closed_ticket_must_be_in_decisions(self, wiki: Path) -> None:
        write_ticket(effort_of(wiki), 3, "Allocation granularity", ticket_type="research", mode="AFK",
                     status="closed", resolution="Order-level.")
        wf.write_indexes(wiki)
        assert any("missing from Decisions so far" in e for e in wf.check_wiki(wiki)[0])

    def test_open_ticket_listed_as_decision_fails(self, tmp_path: Path) -> None:
        effort = tmp_path / "w" / "meta" / "wayfinding" / "e"
        write_map(effort, decisions="- [Open one](tickets/0001-open-one.md): premature")
        write_ticket(effort, 1, "Open one")
        wf.write_indexes(tmp_path / "w")
        assert any("which is open" in e for e in wf.check_wiki(tmp_path / "w")[0])

    def test_settled_ticket_needs_resolution(self, wiki: Path) -> None:
        write_ticket(effort_of(wiki), 1, "What is an order line", status="closed")
        wf.write_indexes(wiki)
        assert any("need a ## Resolution" in e for e in wf.check_wiki(wiki)[0])

    def test_blocking_cycle_detected(self, wiki: Path) -> None:
        write_ticket(effort_of(wiki), 3, "Allocation granularity", ticket_type="research", mode="AFK", blocked_by=[2])
        wf.write_indexes(wiki)
        assert any("blocking cycle" in e for e in wf.check_wiki(wiki)[0])

    def test_wrong_mode_for_type(self, wiki: Path) -> None:
        write_ticket(effort_of(wiki), 2, "Refund timing", mode="AFK", blocked_by=[3])
        wf.write_indexes(wiki)
        assert any("must be HITL" in e for e in wf.check_wiki(wiki)[0])

    def test_broken_link_detected(self, wiki: Path) -> None:
        path = effort_of(wiki) / "tickets" / "0001-what-is-an-order-line.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nSee [note](../../../research/missing.md).\n", encoding="utf-8")
        assert any("broken link" in e for e in wf.check_wiki(wiki)[0])

    def test_cleared_map_cannot_have_open_tickets_or_fog(self, wiki: Path) -> None:
        write_map(effort_of(wiki), status="cleared", fog="- refunds interplay",
                  decisions="- [What is an order line](tickets/0001-what-is-an-order-line.md): a row")
        wf.write_indexes(wiki)
        errors = wf.check_wiki(wiki)[0]
        assert any("still open" in e for e in errors)
        assert any("still has fog" in e for e in errors)

    def test_handed_off_map_needs_existing_handoff(self, tmp_path: Path) -> None:
        effort = tmp_path / "w" / "meta" / "wayfinding" / "e"
        write_map(effort, status="handed-off")
        wf.write_indexes(tmp_path / "w")
        assert any("handoff" in e for e in wf.check_wiki(tmp_path / "w")[0])


class TestIndexes:
    def test_ticket_index_refers_by_name(self, wiki: Path) -> None:
        text = (effort_of(wiki) / "tickets" / "README.md").read_text(encoding="utf-8")
        assert "[Allocation granularity](0003-allocation-granularity.md)" in text
        assert "| [Refund timing](0002-refund-timing.md) | grilling | HITL | open | — | [Allocation granularity]" in text

    def test_wayfinding_index_lists_map_with_counts(self, wiki: Path) -> None:
        text = (wiki / "meta" / "wayfinding" / "INDEX.md").read_text(encoding="utf-8")
        assert "| [Partial cancellation](partial-cancel/MAP.md) | active | A spec for cancelling single line items. | 1 | 2 | 1 |" in text


def test_cli_frontier_and_check(wiki: Path, capsys: pytest.CaptureFixture) -> None:
    assert wf.main(["frontier", str(effort_of(wiki))]) == 0
    assert "Allocation granularity" in capsys.readouterr().out
    assert wf.main(["check", str(wiki)]) == 0
    assert wf.main(["claim", str(effort_of(wiki)), "2", "matu"]) == 1
