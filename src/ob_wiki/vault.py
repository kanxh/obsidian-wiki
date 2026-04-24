from __future__ import annotations

import os
from pathlib import Path

WIKI_SUBDIR = "_Wiki"
HYPER_TAGS_PATH = "spec/hyper-tags.yaml"
CONVENTION_PATH = "spec/wiki-convention.md"

_FALLBACK_TAGS: list[str] = []


def resolve_vault(vault_arg: str | None) -> Path:
    if vault_arg:
        p = Path(vault_arg).expanduser().resolve()
        if not (p / WIKI_SUBDIR).is_dir():
            raise FileNotFoundError(
                f"No {WIKI_SUBDIR}/ directory found under: {p}"
            )
        return p

    env = os.environ.get("OB_WIKI_VAULT")
    if env:
        p = Path(env).expanduser().resolve()
        if not (p / WIKI_SUBDIR).is_dir():
            raise FileNotFoundError(
                f"OB_WIKI_VAULT is set but {WIKI_SUBDIR}/ not found: {p}"
            )
        return p

    # Walk up from cwd
    current = Path.cwd().resolve()
    for candidate in [current, *current.parents]:
        if (candidate / WIKI_SUBDIR).is_dir():
            return candidate

    raise FileNotFoundError(
        f"Could not find a vault with {WIKI_SUBDIR}/. "
        "Set --vault or OB_WIKI_VAULT, or run from inside your vault."
    )


def wiki_root(vault: Path) -> Path:
    return vault / WIKI_SUBDIR


def topics_dir(wiki: Path) -> Path:
    return wiki / "topics"


def methods_dir(wiki: Path) -> Path:
    return wiki / "methods"


def wiki_index_path(wiki: Path) -> Path:
    return wiki / "wiki-index.md"


def load_hyper_tags(wiki: Path) -> list[str]:
    yaml_path = wiki / HYPER_TAGS_PATH
    if not yaml_path.exists():
        return list(_FALLBACK_TAGS)

    tags: list[str] = []
    in_registry = False
    for line in yaml_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "registry:":
            in_registry = True
            continue
        if in_registry:
            if stripped.startswith("- key:"):
                tags.append(stripped[len("- key:"):].strip())
    return tags if tags else list(_FALLBACK_TAGS)


_NON_ENTRY_DIRS = {"spec", "docs", "views"}


def entry_dirs(wiki: Path) -> list[Path]:
    """Return subdirectories of the wiki root that contain .md entry files."""
    if not wiki.is_dir():
        return []
    result: list[Path] = []
    for sub in sorted(wiki.iterdir()):
        if (
            sub.is_dir()
            and not sub.name.startswith(".")
            and sub.name not in _NON_ENTRY_DIRS
            and any(sub.glob("*.md"))
        ):
            result.append(sub)
    return result


def load_entry_types(wiki: Path) -> list[str]:
    """Not used for filtering — kept for external callers that want type discovery."""
    return []
