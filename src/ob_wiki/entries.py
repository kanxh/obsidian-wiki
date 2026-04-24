from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ob_wiki.parser import parse_entry_file
from ob_wiki.vault import entry_dirs


@dataclass
class WikiEntry:
    name: str
    path: Path
    entry_type: Optional[str]
    status: str
    created: str
    updated: str
    hyper_tags: list[str]
    tags: list[str]
    body: str
    wiki_links: list[str]
    related: dict
    has_related_block: bool


def load_all_entries(wiki_root: Path) -> list[WikiEntry]:
    entries: list[WikiEntry] = []
    for directory in entry_dirs(wiki_root):
        for md in sorted(directory.glob("*.md")):
            data = parse_entry_file(md)
            if not data.get("type"):
                continue
            entries.append(WikiEntry(
                name=data["name"],
                path=Path(data["path"]),
                entry_type=data["type"],
                status=data["status"],
                created=data["created"],
                updated=data["updated"],
                hyper_tags=data["hyper_tags"],
                tags=data["tags"],
                body=data["body"],
                wiki_links=data["wiki_links"],
                related=data["related"],
                has_related_block=data["has_related_block"],
            ))
    return sorted(entries, key=lambda e: e.name.lower())


def filter_entries(
    entries: list[WikiEntry],
    entry_type: Optional[str] = None,
    hyper_tag: Optional[str] = None,
    since: Optional[str] = None,
    query: Optional[str] = None,
) -> list[WikiEntry]:
    result = entries
    if entry_type:
        result = [e for e in result if e.entry_type == entry_type]
    if hyper_tag:
        result = [e for e in result if hyper_tag in e.hyper_tags]
    if since:
        result = [e for e in result if e.updated >= since]
    if query:
        q = query.lower()
        result = [
            e for e in result
            if q in e.name.lower()
            or any(q in t.lower() for t in e.tags)
            or q in e.body.lower()
        ]
    return result


def entry_to_dict(entry: WikiEntry, brief: bool = False) -> dict:
    d: dict = {
        "name": entry.name,
        "type": entry.entry_type,
        "hyper_tags": entry.hyper_tags,
        "tags": entry.tags,
        "status": entry.status,
        "created": entry.created,
        "updated": entry.updated,
    }
    if not brief:
        d["body"] = entry.body
        d["wiki_links"] = entry.wiki_links
        d["related"] = entry.related
    return d
