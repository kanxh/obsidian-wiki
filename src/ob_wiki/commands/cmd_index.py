from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

from ob_wiki.vault import wiki_root, wiki_index_path

_DV_VIEW_RE = re.compile(
    r'dv\.view\(["\']_Wiki/views/wikiIndex["\'],\s*\{(.*?)\}\s*\)',
    re.DOTALL,
)
_TITLE_RE    = re.compile(r'title:\s*["\']([^"\']*)["\']')
_SUBTITLE_RE = re.compile(r'subtitle:\s*["\']([^"\']*)["\']')
_CREATED_RE  = re.compile(r'^created:\s*(.+)$', re.MULTILINE)


def _build_index(created: str, today: str, title: str, subtitle: str) -> str:
    return (
        f"---\n"
        f"type: topic\n"
        f"status: active\n"
        f"created: {created}\n"
        f"updated: {today}\n"
        f"tags:\n"
        f"---\n\n"
        f"```dataviewjs\n"
        f"await dv.view(\"_Wiki/views/wikiIndex\", {{\n"
        f"  root: \"_Wiki\",\n"
        f"  title: \"{title}\",\n"
        f"  subtitle: \"{subtitle}\"\n"
        f"}})\n"
        f"```\n"
    )


def add_parser(sub):
    p = sub.add_parser("index", help="Regenerate wiki-index.md frontmatter")
    p.add_argument("--title", default=None,
                   help="Override the index title")
    p.add_argument("--subtitle", default=None,
                   help="Override the index subtitle")


def run(args, vault: Path) -> None:
    wiki = wiki_root(vault)
    idx_path = wiki_index_path(wiki)

    created = "2026-04-08"
    title   = "Obsidian-Wiki"
    subtitle = (
        "A concise cover for the current wiki layer: "
        "topics, methods, and the top-level hyper-tags that organize them."
    )

    if idx_path.exists():
        existing = idx_path.read_text(encoding="utf-8")
        m = _CREATED_RE.search(existing)
        if m:
            created = m.group(1).strip()
        dv_m = _DV_VIEW_RE.search(existing)
        if dv_m:
            block = dv_m.group(1)
            tm = _TITLE_RE.search(block)
            sm = _SUBTITLE_RE.search(block)
            if tm:
                title = tm.group(1)
            if sm:
                subtitle = sm.group(1)

    if args.title:
        title = args.title
    if args.subtitle:
        subtitle = args.subtitle

    today = date.today().isoformat()
    content = _build_index(created, today, title, subtitle)

    tmp = idx_path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(idx_path)
    print(f"Updated: {idx_path}")
