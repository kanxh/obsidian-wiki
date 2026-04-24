from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from ob_wiki.entries import load_all_entries, filter_entries, entry_to_dict
from ob_wiki.vault import wiki_root

_MATH_BLOCK_RE = re.compile(r"\$\$.*?\$\$", re.DOTALL)
_MATH_INLINE_RE = re.compile(r"\$[^$\n]+?\$")
_WIKI_LINK_RE = re.compile(r"\[\[([^\]|#\n]+?)(?:\|([^\]]*?))?\]\]")
_CALLOUT_RE = re.compile(r"^>.*$", re.MULTILINE)
_MULTI_BLANK_RE = re.compile(r"\n{3,}")


def _strip_for_context(body: str) -> str:
    # Remove related block
    m = re.search(r"^>\s*\[!related\]\+\s*Links.*", body, re.IGNORECASE | re.MULTILINE)
    if m:
        body = body[: m.start()].rstrip()
    body = _MATH_BLOCK_RE.sub("[math]", body)
    body = _MATH_INLINE_RE.sub("[math]", body)
    body = _WIKI_LINK_RE.sub(lambda x: x.group(2) or x.group(1), body)
    body = _CALLOUT_RE.sub("", body)
    body = _MULTI_BLANK_RE.sub("\n\n", body)
    return body.strip()


def _format_bibtex_context(entry) -> str:
    domain = ", ".join(entry.hyper_tags) if entry.hyper_tags else "—"
    header = f"== {entry.name} [{entry.entry_type} / {domain}] =="
    cleaned = _strip_for_context(entry.body)
    wl = ", ".join(entry.wiki_links[:8]) if entry.wiki_links else "(none)"
    papers = ", ".join(entry.related.get("papers", [])) or "(none)"
    return f"{header}\n\n{cleaned}\n\nWiki links: {wl}\nPapers: {papers}"


def add_parser(sub):
    p = sub.add_parser("export", help="Export wiki entries")
    p.add_argument("--format", dest="fmt",
                   choices=["json", "md", "bibtex-context"],
                   default="json")
    p.add_argument("--type", dest="entry_type", metavar="TYPE")
    p.add_argument("--hyper-tag", dest="hyper_tag", metavar="TAG")
    p.add_argument("--since", metavar="YYYY-MM-DD")
    p.add_argument("--output", "-o", metavar="FILE", default="-",
                   help="Output file (default: stdout)")


def run(args, vault: Path) -> None:
    wiki = wiki_root(vault)
    entries = load_all_entries(wiki)
    entries = filter_entries(entries,
                             entry_type=args.entry_type,
                             hyper_tag=args.hyper_tag,
                             since=args.since)

    if not entries:
        print("No entries matched.", file=sys.stderr)
        return

    out = sys.stdout
    if args.output != "-":
        out = open(args.output, "w", encoding="utf-8")

    try:
        if args.fmt == "json":
            data = [entry_to_dict(e, brief=False) for e in entries]
            print(json.dumps(data, indent=2, ensure_ascii=False), file=out)

        elif args.fmt == "md":
            for e in entries:
                domain = ", ".join(e.hyper_tags) if e.hyper_tags else "—"
                print(f"---\n# {e.name}  [{e.entry_type} / {domain}]", file=out)
                print(e.body, file=out)

        elif args.fmt == "bibtex-context":
            blocks = [_format_bibtex_context(e) for e in entries]
            print("\n\n".join(blocks), file=out)
    finally:
        if args.output != "-":
            out.close()
