from __future__ import annotations

import re
from pathlib import Path

_WIKI_LINK_RE = re.compile(r"\[\[([^\]|#\n]+?)(?:\|[^\]]*?)?\]\]")
_RELATED_SECTION_RE = re.compile(
    r"^>\s*\[!related\]\+\s*Links\s*\n((?:>.*\n?)*)",
    re.IGNORECASE | re.MULTILINE,
)
_RELATED_LINE_RE = re.compile(
    r"^>\s*(Wiki|Clippings|Notes|Papers):\s*(.*)", re.IGNORECASE
)


def parse_frontmatter(text: str) -> dict:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    fm_lines: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        fm_lines.append(line)

    result: dict = {}
    current_list_key: str | None = None

    for line in fm_lines:
        if line.startswith("  - ") and current_list_key:
            result[current_list_key].append(line[4:].strip())
        elif ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val == "":
                result[key] = []
                current_list_key = key
            else:
                result[key] = val
                current_list_key = None
        else:
            current_list_key = None

    return result


def extract_body(text: str) -> str:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text
    end = 1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end = i + 1
            break
    return "".join(lines[end:]).lstrip("\n")


def extract_wiki_links(body: str) -> list[str]:
    seen: dict[str, None] = {}
    for m in _WIKI_LINK_RE.finditer(body):
        target = m.group(1).strip()
        seen[target] = None
    return list(seen)


def extract_related_block(body: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {
        "wiki": [], "clippings": [], "notes": [], "papers": []
    }
    m = _RELATED_SECTION_RE.search(body)
    if not m:
        return result

    for line in m.group(1).splitlines():
        lm = _RELATED_LINE_RE.match(line)
        if not lm:
            continue
        key = lm.group(1).lower()
        raw = lm.group(2).strip()
        links = [t.strip() for t in raw.split("·") if t.strip()]
        targets: list[str] = []
        for link in links:
            wm = _WIKI_LINK_RE.match(link.strip())
            if wm:
                targets.append(wm.group(1).strip())
            elif link:
                targets.append(link)
        result[key] = targets

    return result


def has_related_block(body: str) -> bool:
    return bool(_RELATED_SECTION_RE.search(body))


def parse_entry_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    body = extract_body(text)
    return {
        "name": path.stem,
        "path": str(path),
        "type": fm.get("type"),
        "status": fm.get("status", ""),
        "created": fm.get("created", ""),
        "updated": fm.get("updated", ""),
        "hyper_tags": fm.get("hyper_tags", []),
        "tags": fm.get("tags", []),
        "body": body,
        "wiki_links": extract_wiki_links(body),
        "related": extract_related_block(body),
        "has_related_block": has_related_block(body),
    }
