from __future__ import annotations

import json
import sys
from pathlib import Path

from ob_wiki.entries import load_all_entries, entry_to_dict
from ob_wiki.vault import wiki_root


def add_parser(sub):
    p = sub.add_parser("show", help="Display a wiki entry")
    p.add_argument("name", help="Entry name (case-insensitive, partial match ok)")
    p.add_argument("--json", dest="as_json", action="store_true",
                   help="Output as JSON")


def run(args, vault: Path) -> None:
    wiki = wiki_root(vault)
    entries = load_all_entries(wiki)

    query = args.name.lower()
    exact = [e for e in entries if e.name.lower() == query]
    if exact:
        matches = exact
    else:
        matches = [e for e in entries if query in e.name.lower()]

    if not matches:
        print(f"ob-wiki: entry not found: {args.name}", file=sys.stderr)
        sys.exit(1)

    if len(matches) > 1:
        print(f"ob-wiki: ambiguous name '{args.name}'. Matches:", file=sys.stderr)
        for m in matches:
            print(f"  {m.name}", file=sys.stderr)
        sys.exit(1)

    entry = matches[0]

    if args.as_json:
        print(json.dumps(entry_to_dict(entry, brief=False),
                         indent=2, ensure_ascii=False))
        return

    tags = ", ".join(entry.hyper_tags) if entry.hyper_tags else "—"
    print(f"# {entry.name}")
    print(f"type: {entry.entry_type}  |  hyper-tags: {tags}  |  updated: {entry.updated}")
    print()
    print(entry.body)
