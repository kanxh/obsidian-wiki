from __future__ import annotations

import shutil
import sys
from datetime import date
from pathlib import Path

_ASSETS = Path(__file__).parent.parent / "assets"

_WIKI_INDEX_TEMPLATE = """\
---
type: topic
status: active
created: {today}
updated: {today}
tags:
---

```dataviewjs
await dv.view("_Wiki/views/wikiIndex", {{
  root: "_Wiki",
  title: "{title}",
  subtitle: "A compact map of topics, methods, and recent movement across the compiled wiki layer."
}})
```
"""

_README_TEMPLATE = """\
---
type: topic
status: active
created: {today}
updated: {today}
tags:
---

# {title}

This is the compiled wiki layer of the vault. Entries are stable retrieval
units: concepts or methods that appear across multiple notes, can be defined
cleanly, and link naturally to each other.

- Entry types live in `topics/` (concepts, phenomena, indices) and `methods/` (modeling, statistical, ML techniques)
- `hyper_tags` (1–2 per entry) define the top-level domain from `spec/hyper-tags.yaml`
- `tags` carry finer-grained labels for retrieval; `hyper_tags` are always synced to the front
- Every entry ends with a `> [!related]+ Links` block connecting wiki, notes, and papers

See [[spec/wiki-convention]] for the full writing and maintenance rules.
"""


def add_parser(sub):
    p = sub.add_parser("init", help="Scaffold a new _Wiki/ directory in a vault")
    p.add_argument("vault", help="Path to Obsidian vault root")
    p.add_argument("--title", default="Obsidian-Wiki",
                   help="Wiki title (default: Obsidian-Wiki)")
    p.add_argument("--force", action="store_true",
                   help="Overwrite files that already exist")


def run(args, _vault: Path) -> None:
    vault = Path(args.vault).expanduser().resolve()
    wiki = vault / "_Wiki"

    if wiki.exists() and not args.force:
        print(f"ob-wiki: {wiki} already exists. Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)

    today = date.today().isoformat()

    dirs = [
        wiki / "topics",
        wiki / "methods",
        wiki / "spec",
        wiki / "docs",
        wiki / "views" / "wikiIndex",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    _copy_asset("views/wikiIndex/view.js",  wiki / "views" / "wikiIndex" / "view.js",  args.force)
    _copy_asset("views/wikiIndex/view.css", wiki / "views" / "wikiIndex" / "view.css", args.force)
    _copy_asset("spec/hyper-tags.yaml",     wiki / "spec" / "hyper-tags.yaml",         args.force)
    _copy_asset("spec/wiki-convention.md",  wiki / "spec" / "wiki-convention.md",      args.force)

    _write_if(
        wiki / "wiki-index.md",
        _WIKI_INDEX_TEMPLATE.format(today=today, title=args.title),
        args.force,
    )
    _write_if(
        wiki / "README.md",
        _README_TEMPLATE.format(today=today, title=args.title),
        args.force,
    )

    print(f"Initialized _Wiki/ at {wiki}")
    print(f"  topics/  methods/  spec/  docs/  views/wikiIndex/")
    print()
    print("Next: open Obsidian, enable the Dataview plugin, then open wiki-index.md.")


def _copy_asset(rel: str, dest: Path, force: bool) -> None:
    src = _ASSETS / rel
    if not src.exists():
        print(f"ob-wiki: warning: missing asset {rel}", file=sys.stderr)
        return
    if dest.exists() and not force:
        return
    shutil.copy2(src, dest)
    print(f"  wrote {rel}")


def _write_if(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path.name}")
