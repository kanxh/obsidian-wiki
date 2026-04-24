from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from ob_wiki.entries import load_all_entries, WikiEntry
from ob_wiki.vault import wiki_root, load_hyper_tags

_SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


@dataclass
class LintIssue:
    entry_name: str
    check: str
    severity: str
    message: str


def _build_inbound_index(entries: list[WikiEntry]) -> dict[str, list[str]]:
    name_map = {e.name.lower(): e.name for e in entries}
    inbound: dict[str, list[str]] = {e.name: [] for e in entries}
    for entry in entries:
        for link in entry.wiki_links:
            target = link.split("/")[-1].split("#")[0].strip()
            canonical = name_map.get(target.lower())
            if canonical and canonical != entry.name:
                inbound[canonical].append(entry.name)
    return inbound


def lint_all(entries: list[WikiEntry], tag_registry: list[str]) -> list[LintIssue]:
    issues: list[LintIssue] = []
    inbound = _build_inbound_index(entries)

    for e in entries:
        if not e.entry_type:
            issues.append(LintIssue(e.name, "missing-type", "error",
                                    "type field is missing or empty"))

        if not e.has_related_block:
            issues.append(LintIssue(e.name, "missing-related-block", "warning",
                                    "No [!related]+ Links block found"))

        if not e.hyper_tags:
            issues.append(LintIssue(e.name, "missing-hyper-tags", "warning",
                                    "hyper_tags field is empty"))
        else:
            for ht in e.hyper_tags:
                if ht not in tag_registry:
                    issues.append(LintIssue(e.name, "unrecognized-hyper-tag", "warning",
                                            f"'{ht}' not in hyper-tags registry"))

            for i, ht in enumerate(e.hyper_tags):
                if i >= len(e.tags) or e.tags[i] != ht:
                    issues.append(LintIssue(e.name, "hyper-tag-sync", "warning",
                                            "hyper_tags not synced to front of tags"))
                    break

        if not inbound[e.name]:
            issues.append(LintIssue(e.name, "orphan", "info",
                                    "No other wiki entries link to this page"))

        if e.has_related_block and not e.related.get("wiki"):
            issues.append(LintIssue(e.name, "empty-wiki-links", "info",
                                    "Related block has no Wiki: links"))

    return sorted(issues,
                  key=lambda x: (_SEVERITY_ORDER.get(x.severity, 9), x.entry_name))


def add_parser(sub):
    p = sub.add_parser("lint", help="Health-check wiki entries")
    p.add_argument("--json", dest="as_json", action="store_true")


def run(args, vault: Path) -> None:
    wiki = wiki_root(vault)
    entries = load_all_entries(wiki)
    tag_registry = load_hyper_tags(wiki)
    issues = lint_all(entries, tag_registry)

    if args.as_json:
        print(json.dumps(
            [{"entry": i.entry_name, "check": i.check,
              "severity": i.severity, "message": i.message}
             for i in issues],
            indent=2, ensure_ascii=False,
        ))
        return

    errors   = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    infos    = [i for i in issues if i.severity == "info"]

    labels = {"error": "ERROR", "warning": "WARN ", "info": "INFO "}

    for group in (errors, warnings, infos):
        for issue in group:
            label = labels[issue.severity]
            print(f"[{label}] {issue.entry_name}: {issue.message}")

    print()
    print(f"  {len(errors)} error(s)  {len(warnings)} warning(s)  {len(infos)} info(s)")

    if errors:
        sys.exit(1)
