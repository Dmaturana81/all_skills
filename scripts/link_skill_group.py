#!/usr/bin/env python3
"""Symlink curated skill groups into ./.cursor/skills (or --dir).

Pass groups, aliases, and/or individual skill ids. Overlaps are unioned.
The link directory is created if it is missing. Group definitions live in
scripts/skill-groups.md.

  link-skills dev-wiki
  link-skills dev-docs
  link-skills dev
  link-skills productivity trello
  link-skills productivity to-questionnaire
  link-skills tdd code-review graphify
  link-skills --file .skill-groups
  link-skills grill-wiki spec-ship --write-file .skill-groups
  link-skills --list
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ALL = REPO
EXTRA_ROOTS = [
    Path("/Users/matu/Xcode/daniel-career/.cursor/skills"),
    Path.home() / ".cursor" / "skills",
]
DEFAULT_MANIFEST = ".skill-groups"
DEFAULT_LINK_DIR = Path(".cursor") / "skills"
SKIP_PARTS = {".venv", "node_modules", "agents", "wayfinder-wiki-workspace"}

# Keep in sync with scripts/skill-groups.md
# Atomic groups: name -> (one-line definition, skill ids)
GROUPS: dict[str, tuple[str, tuple[str, ...]]] = {
    "grill-docs": (
        "Grill in a git repo; CONTEXT.md + ADRs.",
        ("grilling", "grill-with-docs", "wait-what", "domain-modeling"),
    ),
    "grill-wiki": (
        "Grill against wiki_*/ (requires repo-agent-wiki first).",
        (
            "grilling",
            "grilling-wiki",
            "domain-modeling-wiki",
            "repo-agent-wiki",
            "grill-with-wiki",
            "wait-what",
        ),
    ),
    "grill-stateless": (
        "Grill with no repo / no wiki.",
        ("grilling", "grill-me"),
    ),
    "spec-ship": (
        "Spec → tickets → implement (TDD + code-review).",
        ("to-spec", "to-tickets", "implement", "tdd", "code-review"),
    ),
    "spec-ship-wiki": (
        "Spec → tickets → implement (TDD-wiki + code-review) for wiki_*/ repos.",
        (
            "to-spec",
            "to-tickets",
            "implement-wiki",
            "tdd-wiki",
            "code-review",
        ),
    ),
    "wiki": (
        "Every wiki_* skill: scaffold, grill, wayfinding, research, prototype, spec, implement.",
        (
            "repo-agent-wiki",
            "grilling",
            "grilling-wiki",
            "domain-modeling-wiki",
            "grill-with-wiki",
            "wayfinder-wiki",
            "research-wiki",
            "prototype",
            "prototype-wiki",
            "to-spec-wiki",
            "implement-wiki",
            "tdd-wiki",
            "code-review",
        ),
    ),
    "inbox": (
        "Incoming bugs/requests → agent-ready issues.",
        ("triage",),
    ),
    "fog": (
        "Multi-session decision map; hands off to to-spec.",
        ("wayfinder", "ask-matt"),
    ),
    "debug": (
        "Hard-bug loop (red command first).",
        ("diagnosing-bugs",),
    ),
    "design": (
        "Architecture survey, deep modules, throwaway prototype.",
        (
            "improve-codebase-architecture",
            "codebase-design",
            "prototype",
            "handoff",
        ),
    ),
    "research": (
        "Background primary-source memo into the grill.",
        ("research",),
    ),
    "ask-others": (
        "Questionnaire for someone else.",
        ("to-questionnaire",),
    ),
    "productivity": (
        "Daily non-code workflow. Add trello and/or to-questionnaire as extra skills.",
        ("grilling", "grill-me", "wait-what", "handoff"),
    ),
    "human-ops": (
        "Only a human can click / provision.",
        ("wizard", "teach"),
    ),
    "manifest": (
        "Execution Manifest pipeline (no scope creep).",
        (
            "blueprint-planner",
            "restricted-coder",
            "adversarial-reviewer",
            "shepherd-agent",
            "agent-journaler",
        ),
    ),
    "linkedin": (
        "AINNOVA/personal LinkedIn comments + posts.",
        ("linkedin-comment-discuss", "linkedin-writer"),
    ),
    "brand": (
        "Visual theme / brand chrome.",
        ("brand-guidelines", "theme-factory"),
    ),
    "geo": (
        "Full GEO suite — orchestrator needs all children.",
        (
            "geo",
            "geo-audit",
            "geo-citability",
            "geo-crawlers",
            "geo-llmstxt",
            "geo-brand-mentions",
            "geo-platform-optimizer",
            "geo-schema",
            "geo-technical",
            "geo-content",
            "geo-report",
            "geo-report-pdf",
        ),
    ),
    "adk": (
        "Google ADK lifecycle (workflow re-reads every phase).",
        (
            "google-agents-cli-workflow",
            "google-agents-cli-scaffold",
            "google-agents-cli-adk-code",
            "google-agents-cli-eval",
            "google-agents-cli-observability",
            "google-agents-cli-deploy",
            "google-agents-cli-publish",
        ),
    ),
    "mcp": ("Author an MCP server.", ("mcp-builder",)),
    "frontend": (
        "UI, HTML artifacts, Playwright.",
        ("frontend-design", "web-artifacts-builder", "webapp-testing"),
    ),
    "github": ("GitHub + issues (Matt tracker option).", ("github", "gh-issues")),
    "graph": ("Codebase graph.", ("graphify",)),
    "skills-meta": ("Write new skills.", ("skill-creator",)),
    "claude-api": ("Anthropic API apps.", ("claude-api",)),
    "image": ("Gemini image gen.", ("nano-banana-pro",)),
    "science-common": (
        "Shared science uv/HTTP package (not invoked).",
        ("science_skills_common", "scienceskillscommon", "uv"),
    ),
    "science-lit": (
        "Literature search.",
        (
            "literature_search_arxiv",
            "literature_search_biorxiv",
            "literature_search_europepmc",
            "literature_search_openalex",
            "pubmed_database",
        ),
    ),
    "science-seq": (
        "Sequence / structure.",
        (
            "uniprot_database",
            "ncbi_sequence_fetch",
            "pdb_database",
            "protein_sequence_msa",
            "protein_sequence_similarity_search",
            "foldseek_structural_search",
            "pymol",
            "alphafold_database_fetch_and_analyze",
            "alphagenome_single_variant_analysis",
        ),
    ),
    "science-db": (
        "Chem / clinical / variant / ontology DBs.",
        (
            "chembl_database",
            "clinical_trials_database",
            "clinvar_database",
            "openfda_database",
            "opentargets_database",
            "gnomad_database",
            "dbsnp_database",
            "ensembl_database",
            "encode_ccres_database",
            "embl_ebi_ols",
            "gtex_database",
            "human_protein_atlas_database",
            "interpro_database",
            "jaspar_database",
            "pubchem_database",
            "quickgo_database",
            "reactome_database",
            "string_database",
            "ucsc_conservation_and_tfbs",
            "unibind_database",
        ),
    ),
    "slides": ("PowerPoint.", ("pptx",)),
    "sheets": ("Spreadsheets.", ("xlsx",)),
    "docs-write": (
        "Human docs + agent-facing prose.",
        ("doc-coauthoring", "writing-for-agents"),
    ),
}

# Group → other groups that must be linked (see Skill Groups.md).
NEEDS: dict[str, tuple[str, ...]] = {
    "inbox": ("spec-ship",),
    "fog": ("spec-ship",),
    "debug": ("design",),
    "science-lit": ("science-common",),
    "science-seq": ("science-common",),
    "science-db": ("science-common",),
    "slides": ("brand",),
}

_SHIP = ("spec-ship", "inbox", "debug", "design", "research", "github")
_SHIP_WIKI = ("spec-ship-wiki", "inbox", "debug", "design", "research", "github")

ALIASES: dict[str, tuple[str, tuple[str, ...]]] = {
    "engineering": (
        "Matt flow + CONTEXT.md repos (same as engineering-docs / dev-docs)",
        ("grill-docs", *_SHIP),
    ),
    "engineering-docs": (
        "All developing using docs (CONTEXT.md + ADRs)",
        ("grill-docs", *_SHIP),
    ),
    "dev-docs": (
        "All developing using docs (CONTEXT.md + ADRs)",
        ("grill-docs", *_SHIP),
    ),
    "engineering-wiki": (
        "All developing using wiki_*/ (grill-wiki + ship pipeline)",
        ("grill-wiki", *_SHIP_WIKI),
    ),
    "dev-wiki": (
        "All developing using wiki_*/ (grill-wiki + ship pipeline)",
        ("grill-wiki", *_SHIP_WIKI),
    ),
    "engineering-plain": (
        "All developing without wiki and without docs (grill-me only)",
        ("grill-stateless", *_SHIP),
    ),
    "dev": (
        "All developing without wiki and without docs (grill-me only)",
        ("grill-stateless", *_SHIP),
    ),
    "coding": (
        "Implement-only; plan already exists",
        ("spec-ship", "debug"),
    ),
    "manifest-ship": (
        "Strict manifest pipeline",
        ("manifest",),
    ),
    "marketing": (
        "AINNOVA site + LinkedIn",
        ("linkedin", "geo", "brand"),
    ),
    "docs": (
        "Decks and docs",
        ("slides", "sheets", "docs-write", "brand"),
    ),
    "science": (
        "Full science suite",
        ("science-common", "science-lit", "science-seq", "science-db"),
    ),
}

WEB_GROUPS = {"geo", "marketing", "frontend"}


def index_skills() -> dict[str, list[Path]]:
    found: dict[str, list[Path]] = {}
    if ALL.is_dir():
        for skill_md in ALL.rglob("SKILL.md"):
            if any(p in skill_md.parts for p in SKIP_PARTS):
                continue
            found.setdefault(skill_md.parent.name, []).append(skill_md.parent)
    for extra in EXTRA_ROOTS:
        if not extra.is_dir():
            continue
        for skill_md in extra.glob("*/SKILL.md"):
            found.setdefault(skill_md.parent.name, []).append(skill_md.parent)
    return found


def resolve_skill_id(name: str, index: dict[str, list[Path]]) -> str | None:
    """Match a skill folder name; try hyphen/underscore variants."""
    if name in index:
        return name
    hyphen = name.replace("_", "-")
    if hyphen in index:
        return hyphen
    under = name.replace("-", "_")
    if under in index:
        return under
    return None


def expand_names(
    names: list[str], index: dict[str, list[Path]]
) -> tuple[list[str], list[str], list[str]]:
    """Return (atomic groups, extra skill ids, unknown names). Pulls NEEDS."""
    atomic: list[str] = []
    extra: list[str] = []
    unknown: list[str] = []
    seen_groups: set[str] = set()
    seen_skills: set[str] = set()

    def add_atomic(name: str) -> None:
        if name not in seen_groups:
            seen_groups.add(name)
            atomic.append(name)
            for dep in NEEDS.get(name, ()):
                if dep == "spec-ship" and "spec-ship-wiki" in seen_groups:
                    continue
                add_atomic(dep)

    def add_skill(skill_id: str) -> None:
        if skill_id not in seen_skills:
            seen_skills.add(skill_id)
            extra.append(skill_id)

    for raw in names:
        name = raw.strip()
        if not name or name.startswith("#"):
            continue
        if name in GROUPS:
            add_atomic(name)
        elif name in ALIASES:
            for child in ALIASES[name][1]:
                add_atomic(child)
        else:
            skill_id = resolve_skill_id(name, index)
            if skill_id:
                add_skill(skill_id)
            else:
                unknown.append(name)
    return atomic, extra, unknown


def skills_for(atomic_groups: list[str]) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    for g in atomic_groups:
        for skill_id in GROUPS[g][1]:
            if skill_id not in seen:
                seen.add(skill_id)
                ids.append(skill_id)
    return ids


def pick_path(skill_id: str, paths: list[Path], atomic_groups: list[str]) -> Path:
    if len(paths) == 1:
        return paths[0]
    prefer_web = any(g in WEB_GROUPS for g in atomic_groups)
    web = [p for p in paths if "web" in p.parts]
    rootish = [p for p in paths if "web" not in p.parts]
    if prefer_web and web:
        return web[0]
    if rootish:
        return rootish[0]
    return paths[0]


def read_manifest(path: Path) -> list[str]:
    names: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        names.extend(line.replace(",", " ").split())
    return names


def write_manifest(
    path: Path, atomic_groups: list[str], extra_skills: list[str]
) -> None:
    lines = [
        "# Skill groups for this repo (link-skills --file)",
        "# Atomic groups and individual skill ids — scripts/skill-groups.md",
        "",
        *atomic_groups,
    ]
    if extra_skills:
        lines.extend(["", "# Individual skills", *extra_skills])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def list_groups(index: dict[str, list[Path]]) -> None:
    print("Atomic groups (include a list of these in a repo):\n")
    width = max(len(n) for n in GROUPS)
    for name, (defn, ids) in GROUPS.items():
        missing = [i for i in ids if i not in index]
        print(f"  {name:<{width}}  {len(ids):2}  {defn}")
        print(f"  {'':{width}}      {', '.join(ids)}")
        deps = NEEDS.get(name)
        if deps:
            print(f"  {'':{width}}      needs: {', '.join(deps)}")
        if missing:
            print(f"  {'':{width}}      missing: {', '.join(missing)}")
        print()
    print("Aliases (expand to atomic groups):\n")
    aw = max(len(n) for n in ALIASES)
    for name, (defn, children) in ALIASES.items():
        print(f"  {name:<{aw}}  {defn}")
        print(f"  {'':{aw}}  → {', '.join(children)}")
        print()
    print("Examples:")
    print("  link-skills dev-wiki")
    print("  link-skills dev-docs")
    print("  link-skills dev")
    print("  link-skills productivity trello")
    print("  link-skills productivity to-questionnaire")
    print("  link-skills tdd graphify")
    print("  link-skills linkedin geo --write-file .skill-groups")
    print("  link-skills --file .skill-groups")
    print("  Groups: scripts/skill-groups.md")
    print("  Links land in ./.cursor/skills unless --dir is set.")
    print()
    print("Individual skills: any folder name under all_skills (or extra roots).")
    print("  Group names win if they collide with a skill id (research, github, geo).")


def apply_links(
    skill_ids: list[str],
    dest: Path,
    atomic_groups: list[str],
    *,
    force: bool,
    dry_run: bool,
    unlink: bool,
) -> int:
    index = index_skills()
    dest = dest.resolve()
    if not dry_run:
        dest.mkdir(parents=True, exist_ok=True)
    errors = 0

    for skill_id in skill_ids:
        link = dest / skill_id
        paths = index.get(skill_id, [])
        if unlink:
            if link.is_symlink() or link.is_file():
                print(f"  rm  {skill_id}")
                if not dry_run:
                    link.unlink()
            elif link.exists():
                print(f"  skip {skill_id} (not a symlink)", file=sys.stderr)
                errors += 1
            else:
                print(f"  --  {skill_id}")
            continue

        if not paths:
            print(f"  !!  {skill_id} — not found", file=sys.stderr)
            errors += 1
            continue

        source = pick_path(skill_id, paths, atomic_groups).resolve()
        if link.exists() or link.is_symlink():
            if link.is_symlink() and link.resolve() == source:
                print(f"  ok  {skill_id}")
                continue
            if not force:
                print(f"  skip {skill_id} — exists. Use --force.", file=sys.stderr)
                errors += 1
                continue
            print(f"  replace {skill_id}")
            if not dry_run:
                link.unlink()
        else:
            print(f"  ln   {skill_id}  →  {source}")
        if not dry_run:
            link.symlink_to(source, target_is_directory=True)

    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Symlink one or more skill groups into ./.cursor/skills (or --dir)."
    )
    parser.add_argument(
        "groups",
        nargs="*",
        help="Groups, aliases, and/or individual skill ids (repeatable)",
    )
    parser.add_argument("--list", action="store_true", help="List groups and exit")
    parser.add_argument(
        "--file",
        type=Path,
        metavar="PATH",
        help=f"Read group names from a file (default name {DEFAULT_MANIFEST})",
    )
    parser.add_argument(
        "--write-file",
        type=Path,
        nargs="?",
        const=Path(DEFAULT_MANIFEST),
        metavar="PATH",
        help=f"Write the resolved atomic groups to a manifest (default {DEFAULT_MANIFEST})",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=None,
        help="Link directory (default: ./.cursor/skills, created if missing)",
    )
    parser.add_argument("--force", action="store_true", help="Replace existing links")
    parser.add_argument("--dry-run", action="store_true", help="Print only")
    parser.add_argument("--unlink", action="store_true", help="Remove links for these groups")
    args = parser.parse_args()

    if args.list:
        list_groups(index_skills())
        return 0

    names = list(args.groups)
    if args.file:
        if not args.file.is_file():
            print(f"Manifest not found: {args.file}", file=sys.stderr)
            return 2
        names.extend(read_manifest(args.file))

    if not names:
        list_groups(index_skills())
        print("\nPass groups or --file .skill-groups", file=sys.stderr)
        return 2

    index = index_skills()
    atomic, extra_skills, unknown = expand_names(names, index)
    if unknown:
        print(f"Unknown group(s) or skill(s): {', '.join(unknown)}", file=sys.stderr)
        print("Use --list to see groups; skill ids are folder names under all_skills.", file=sys.stderr)
        return 2

    skill_ids = skills_for(atomic)
    seen = set(skill_ids)
    for skill_id in extra_skills:
        if skill_id not in seen:
            seen.add(skill_id)
            skill_ids.append(skill_id)
    link_dir = args.dir if args.dir is not None else Path.cwd() / DEFAULT_LINK_DIR
    action = "Unlink" if args.unlink else "Link"
    print(f"{action} groups: {', '.join(atomic) if atomic else '(none)'}")
    if extra_skills:
        print(f"Extra skills: {', '.join(extra_skills)}")
    print(f"Skills ({len(skill_ids)}): {', '.join(skill_ids)}")
    print(f"Target: {link_dir.resolve()}\n")

    code = apply_links(
        skill_ids,
        link_dir,
        atomic,
        force=args.force,
        dry_run=args.dry_run,
        unlink=args.unlink,
    )

    if args.write_file and not args.unlink and not args.dry_run:
        dest = args.write_file
        if not dest.is_absolute():
            dest = link_dir.resolve() / dest
        write_manifest(dest, atomic, extra_skills)
        print(f"\nWrote manifest: {dest}")

    if args.dry_run:
        print("\nDry run — no changes written.")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
