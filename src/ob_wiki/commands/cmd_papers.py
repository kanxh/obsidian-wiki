from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from ob_wiki.entries import load_all_entries, filter_entries
from ob_wiki.vault import wiki_root


def add_parser(sub):
    p = sub.add_parser("papers", help="List papers cited across wiki entries")
    p.add_argument("--entry", metavar="NAME",
                   help="Limit to a single entry (case-insensitive)")
    p.add_argument("--type", dest="entry_type", metavar="TYPE")
    p.add_argument("--hyper-tag", dest="hyper_tag", metavar="TAG")
    p.add_argument("--json", dest="as_json", action="store_true")


def run(args, vault: Path) -> None:
    wiki = wiki_root(vault)
    entries = load_all_entries(wiki)
    entries = filter_entries(entries,
                             entry_type=args.entry_type,
                             hyper_tag=args.hyper_tag)

    if args.entry:
        q = args.entry.lower()
        entries = [e for e in entries if q in e.name.lower()]

    cited: dict[str, list[str]] = defaultdict(list)
    for e in entries:
        for paper in e.related.get("papers", []):
            cited[paper].append(e.name)

    if not cited:
        print("No papers found in related blocks.")
        return

    items = sorted(cited.items(), key=lambda x: (-len(x[1]), x[0]))

    if args.as_json:
        out = [{"paper": p, "cited_by": names} for p, names in items]
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    paper_w = max(len(p) for p, _ in items)
    for paper, names in items:
        print(f"{paper:<{paper_w}}  cited by: {', '.join(names)}")
