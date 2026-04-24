from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from ob_wiki.entries import load_all_entries
from ob_wiki.vault import wiki_root


def add_parser(sub):
    p = sub.add_parser("stats", help="Show wiki statistics")
    p.add_argument("--json", dest="as_json", action="store_true",
                   help="Output as JSON")


def run(args, vault: Path) -> None:
    wiki = wiki_root(vault)
    entries = load_all_entries(wiki)

    topics  = [e for e in entries if e.entry_type == "topic"]
    methods = [e for e in entries if e.entry_type == "method"]

    tag_counts: Counter = Counter()
    for e in entries:
        for t in e.hyper_tags:
            tag_counts[t] += 1

    dates = [e.updated for e in entries if e.updated]
    last_updated = max(dates) if dates else "—"

    recently = sorted(entries, key=lambda e: e.updated, reverse=True)[:5]

    stats = {
        "total_topics":      len(topics),
        "total_methods":     len(methods),
        "total_entries":     len(entries),
        "unique_hyper_tags": len(tag_counts),
        "last_updated":      last_updated,
        "hyper_tag_counts":  [
            {"tag": t, "count": c}
            for t, c in tag_counts.most_common()
        ],
        "recently_updated": [
            {"name": e.name, "type": e.entry_type, "updated": e.updated}
            for e in recently
        ],
    }

    if args.as_json:
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return

    print(f"  Topics   {stats['total_topics']:>4}")
    print(f"  Methods  {stats['total_methods']:>4}")
    print(f"  Total    {stats['total_entries']:>4}")
    print(f"  Updated  {last_updated}")
    print()
    print("Hyper-tag breakdown:")
    for item in stats["hyper_tag_counts"]:
        bar = "█" * item["count"]
        print(f"  {item['tag']:<20} {item['count']:>3}  {bar}")
    print()
    print("Recently updated:")
    for item in stats["recently_updated"]:
        print(f"  {item['updated']}  [{item['type']:<6}]  {item['name']}")
