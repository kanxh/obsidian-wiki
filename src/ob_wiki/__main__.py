from __future__ import annotations

import argparse
import sys

from ob_wiki import __version__
from ob_wiki.vault import resolve_vault
from ob_wiki.commands import (
    cmd_list, cmd_show, cmd_stats,
    cmd_search, cmd_papers, cmd_export,
    cmd_lint, cmd_new, cmd_index, cmd_setup,
)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        cmd_setup.run()
        return

    parser = argparse.ArgumentParser(
        prog="ob-wiki",
        description="Obsidian wiki CLI — manage _Wiki/ from the terminal",
    )
    parser.add_argument(
        "--vault", default=None,
        help="Path to Obsidian vault root (default: auto-detect from cwd or OB_WIKI_VAULT)",
    )
    parser.add_argument("--version", action="version", version=f"ob-wiki {__version__}")

    sub = parser.add_subparsers(dest="command", metavar="COMMAND", required=True)

    cmd_list.add_parser(sub)
    cmd_show.add_parser(sub)
    cmd_stats.add_parser(sub)
    cmd_search.add_parser(sub)
    cmd_papers.add_parser(sub)
    cmd_export.add_parser(sub)
    cmd_lint.add_parser(sub)
    cmd_new.add_parser(sub)
    cmd_index.add_parser(sub)

    args = parser.parse_args()

    try:
        vault = resolve_vault(args.vault)
    except FileNotFoundError as exc:
        print(f"ob-wiki: {exc}", file=sys.stderr)
        sys.exit(1)

    dispatch = {
        "list":   cmd_list.run,
        "show":   cmd_show.run,
        "stats":  cmd_stats.run,
        "search": cmd_search.run,
        "papers": cmd_papers.run,
        "export": cmd_export.run,
        "lint":   cmd_lint.run,
        "new":    cmd_new.run,
        "index":  cmd_index.run,
    }
    dispatch[args.command](args, vault)


if __name__ == "__main__":
    main()
