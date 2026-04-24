from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from ob_wiki.vault import wiki_root, load_hyper_tags, entry_dirs


def _render_template(title: str, entry_type: str,
                     hyper_tags: list[str], today: str) -> str:
    ht_lines = "".join(f"  - {t}\n" for t in hyper_tags) if hyper_tags else "  - \n"
    tag_lines = (
        "".join(f"  - {t}\n" for t in hyper_tags) + "  - \n"
        if hyper_tags else "  - \n"
    )
    related_lines = "> Wiki: \n> Notes: \n"
    return (
        f"---\n"
        f"type: {entry_type}\n"
        f"status: active\n"
        f"created: {today}\n"
        f"updated: {today}\n"
        f"hyper_tags:\n{ht_lines}"
        f"tags:\n{tag_lines}"
        f"---\n\n"
        f"<!-- Write 1-3 paragraphs. First sentence defines the object. -->\n\n"
        f"> [!related]+ Links\n"
        f"{related_lines}"
    )


def _title_to_filename(title: str) -> str:
    illegal = r'/\:*?"<>|'
    return "".join(c for c in title if c not in illegal) + ".md"


def add_parser(sub):
    p = sub.add_parser("new", help="Scaffold a new wiki entry")
    p.add_argument("title", help="Entry title (used as filename)")
    p.add_argument("--type", dest="entry_type", required=True, metavar="TYPE",
                   help="Entry type (e.g. topic, method — must match a subdirectory name in _Wiki/)")
    p.add_argument("--hyper-tag", dest="hyper_tags", metavar="TAG",
                   action="append", default=[])
    p.add_argument("--dry-run", action="store_true",
                   help="Print template without writing")


def run(args, vault: Path) -> None:
    wiki = wiki_root(vault)
    tag_registry = load_hyper_tags(wiki)

    for ht in args.hyper_tags:
        if ht not in tag_registry:
            print(f"ob-wiki: warning: '{ht}' not in hyper-tags registry "
                  f"(known: {', '.join(tag_registry)})", file=sys.stderr)

    # Find the subdirectory whose name matches the given type (plural form, e.g. "topics" for "topic")
    dirs = entry_dirs(wiki)
    directory = next(
        (d for d in dirs if d.name == args.entry_type or d.name == args.entry_type + "s"),
        wiki / (args.entry_type + "s"),  # create new dir if type is novel
    )
    filename = _title_to_filename(args.title)
    dest = directory / filename

    if dest.exists() and not args.dry_run:
        print(f"ob-wiki: entry already exists: {dest}", file=sys.stderr)
        sys.exit(1)

    today = date.today().isoformat()
    content = _render_template(args.title, args.entry_type, args.hyper_tags, today)

    if args.dry_run:
        print(content)
        return

    directory.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    print(f"Created: {dest}")
