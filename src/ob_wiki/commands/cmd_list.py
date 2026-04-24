from __future__ import annotations

import json
import sys
from pathlib import Path

from ob_wiki.entries import load_all_entries, filter_entries, entry_to_dict
from ob_wiki.vault import wiki_root


def add_parser(sub):
    p = sub.add_parser("list", help="List wiki entries")
    p.add_argument("--type", dest="entry_type", choices=["topic", "method"],
                   help="Filter by entry type")
    p.add_argument("--hyper-tag", dest="hyper_tag", metavar="TAG",
                   help="Filter by hyper-tag")
    p.add_argument("--since", metavar="YYYY-MM-DD",
                   help="Only entries updated on or after this date")
    p.add_argument("--json", dest="as_json", action="store_true",
                   help="Output as JSON")


def run(args, vault: Path) -> None:
    wiki = wiki_root(vault)
    entries = load_all_entries(wiki)
    entries = filter_entries(
        entries,
        entry_type=args.entry_type,
        hyper_tag=args.hyper_tag,
        since=args.since,
    )

    if args.as_json:
        print(json.dumps([entry_to_dict(e, brief=True) for e in entries],
                         indent=2, ensure_ascii=False))
        return

    if not entries:
        print("No entries found.")
        return

    name_w = max(len(e.name) for e in entries)
    type_w = 6
    tag_w  = max((len(", ".join(e.hyper_tags)) for e in entries), default=10)

    header = f"{'Name':<{name_w}}  {'Type':<{type_w}}  {'Hyper-tags':<{tag_w}}  Updated"
    print(header)
    print("-" * len(header))
    for e in entries:
        tags = ", ".join(e.hyper_tags) if e.hyper_tags else "—"
        print(f"{e.name:<{name_w}}  {e.entry_type or '?':<{type_w}}  {tags:<{tag_w}}  {e.updated}")
