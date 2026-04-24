from __future__ import annotations

import shutil
import sys
from pathlib import Path


def _template_path() -> Path:
    return Path(__file__).parent.parent / "templates" / "SKILL.md"


def run() -> None:
    template = _template_path()
    if not template.exists():
        print("ob-wiki: SKILL.md template not found in package", file=sys.stderr)
        sys.exit(1)

    targets = [
        {
            "name": "Claude Code",
            "dest": Path.home() / ".claude" / "skills" / "ob-wiki" / "SKILL.md",
            "detect": lambda: (Path.home() / ".claude").is_dir(),
        },
        {
            "name": "OpenCode",
            "dest": Path.home() / ".config" / "opencode" / "skills" / "ob-wiki" / "SKILL.md",
            "detect": lambda: bool(shutil.which("opencode")),
        },
        {
            "name": "Codex",
            "dest": Path.home() / ".codex" / "skills" / "ob-wiki" / "SKILL.md",
            "detect": lambda: bool(shutil.which("codex")),
        },
    ]

    installed = False
    for t in targets:
        if t["detect"]():
            dest: Path = t["dest"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(template, dest)
            print(f"Installed SKILL.md ({t['name']}) → {dest}")
            installed = True

    if not installed:
        print("ob-wiki: no supported AI tool detected (Claude Code / OpenCode / Codex).")
        print("  Install manually: copy SKILL.md to the skills directory of your AI tool.")
        sys.exit(1)
