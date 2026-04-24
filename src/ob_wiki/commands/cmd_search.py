from __future__ import annotations

import json
import sys
from pathlib import Path

from ob_wiki.entries import load_all_entries, filter_entries, entry_to_dict
from ob_wiki.vault import wiki_root

_EXCERPT_LEN = 120


def _score(entry, query: str) -> int:
    q = query.lower()
    score = 0
    if q in entry.name.lower():
        score += 10
    if any(q in t.lower() for t in entry.hyper_tags):
        score += 7
    if any(q in t.lower() for t in entry.tags):
        score += 5
    if q in entry.body.lower():
        score += 1
    return score


def _excerpt(body: str, query: str) -> str:
    q = query.lower()
    idx = body.lower().find(q)
    if idx == -1:
        return body[:_EXCERPT_LEN].replace("\n", " ").strip()
    start = max(0, idx - 40)
    snippet = body[start:start + _EXCERPT_LEN].replace("\n", " ").strip()
    return ("…" if start > 0 else "") + snippet


def add_parser(sub):
    p = sub.add_parser("search", help="Search entries by keyword or tag")
    p.add_argument("query", help="Search keyword")
    p.add_argument("--type", dest="entry_type", metavar="TYPE")
    p.add_argument("--hyper-tag", dest="hyper_tag", metavar="TAG")
    p.add_argument("--json", dest="as_json", action="store_true")


def run(args, vault: Path) -> None:
    wiki = wiki_root(vault)
    entries = load_all_entries(wiki)
    entries = filter_entries(entries,
                             entry_type=args.entry_type,
                             hyper_tag=args.hyper_tag)

    scored = [(e, _score(e, args.query)) for e in entries]
    scored = [(e, s) for e, s in scored if s > 0]
    scored.sort(key=lambda x: (-x[1], x[0].name.lower()))

    if not scored:
        print(f"No results for: {args.query}")
        return

    if args.as_json:
        out = []
        for e, s in scored:
            d = entry_to_dict(e, brief=True)
            d["score"] = s
            out.append(d)
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    for e, s in scored:
        tags = ", ".join(e.hyper_tags) if e.hyper_tags else "—"
        print(f"{e.name}  [{e.entry_type}]  {tags}")
        print(f"  {_excerpt(e.body, args.query)}")
