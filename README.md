# obsidian-wiki

Manage an Obsidian research wiki from the command line — list and search
entries, scaffold new pages with schema-compliant frontmatter, run health
checks, export content as context for paper writing, and track which papers are
cited across your knowledge base.

Designed for researchers who maintain a structured personal wiki on top of their
literature notes and project notes in Obsidian.

> Inspired by Andrej Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
> pattern: instead of re-deriving knowledge on every query, an LLM incrementally
> builds and maintains a persistent, interlinked collection of markdown files
> that sits between you and your raw sources.

## Wiki Schema

```
type → hyper_tags → tags → [[wikilinks]]
 │          │         │          │
tree      sparse    dense      network
```

The schema is a deliberate balance: `type` and `hyper_tags` define a minimal
tree skeleton for browsability; `tags` and `[[wikilinks]]` build the richer
network on top.

**`type`** — the entry's category, stored as a subdirectory name (`topics/`,
`methods/`, or any user-defined folder). `ob-wiki` discovers types from your
vault layout — none are hardcoded in the tool.

**`hyper_tags`** — 1–2 per entry, drawn from a registry in
`spec/hyper-tags.yaml`. The sparse top-level branching: few enough to stay
stable, just enough to make the wiki browsable by domain.

**`tags`** — fine-grained, many per entry. The dense fabric that drives search
and filtering. `hyper_tags` are always copied to the front of `tags` to keep
both fields in sync.

**`[[wikilinks]]`** — direct edges between entries. The network layer: they
turn the tag skeleton into a traversable knowledge graph, and the `papers`
command uses them to surface shared literature across entries.

## Core Capabilities

- List wiki entries with filters by type, hyper-tag, and date
- Search by keyword or tag with relevance scoring
- Scaffold new entries with correct frontmatter in one command
- Health-check the wiki for orphans, missing link blocks, and schema violations
- Export entries as clean prose context for LLM paper-writing prompts
- Aggregate paper citations across wiki entries to surface shared literature
- Scaffold a complete `_Wiki/` structure in a new vault with `init`
- Install as a skill for Claude Code, OpenCode, and Codex

## Installation

> macOS — requires Python 3.8+

```bash
# uv (recommended)
uv tool install git+https://github.com/kanxh/obsidian-wiki.git

# pip
pip install git+https://github.com/kanxh/obsidian-wiki.git
```

Register the skill with your AI tools:

```bash
ob-wiki setup
```

Installs `SKILL.md` to:

| Tool | Path |
|---|---|
| Claude Code | `~/.claude/skills/ob-wiki/SKILL.md` |
| OpenCode | `~/.config/opencode/skills/ob-wiki/SKILL.md` |
| Codex | `~/.codex/skills/ob-wiki/SKILL.md` |

## Quick Start

```bash
# Bootstrap a new vault
ob-wiki init ~/Documents/my-vault

# Verify
ob-wiki stats
```

Then ask your AI assistant to extract wiki entries from your vault:

> *I just initialized a `_Wiki/` in my Obsidian vault. Extract stable concepts and methods from the vault into wiki entries, following the convention in `_Wiki/spec/wiki-convention.md`. Use `ob-wiki new` to scaffold each entry, then fill in the body from the source notes.*

```bash
# Day-to-day usage
ob-wiki list --type method
ob-wiki show HMM
ob-wiki search "thermal comfort" --json
ob-wiki lint
ob-wiki export --format bibtex-context --hyper-tag statistics
ob-wiki new "Gaussian Process" --type method --hyper-tag statistics --dry-run
```

## Commands

| Command | Description | Key flags |
|---|---|---|
| `init <vault>` | Scaffold a new `_Wiki/` with views and spec files | `--title`, `--force` |
| `list` | List all entries | `--type`, `--hyper-tag`, `--since`, `--json` |
| `show <name>` | Display entry content | `--json` |
| `stats` | Entry counts, tag distribution, recent updates | `--json` |
| `search <query>` | Search by keyword or tag | `--type`, `--hyper-tag`, `--json` |
| `papers` | Aggregate paper citations across entries | `--entry`, `--hyper-tag`, `--json` |
| `export` | Export entries in multiple formats | `--format`, `--type`, `--hyper-tag`, `--since`, `--output` |
| `lint` | Health-check: orphans, missing blocks, schema issues | `--json` |
| `new <title>` | Scaffold a new entry from template | `--type` (required), `--hyper-tag`, `--dry-run` |
| `index` | Regenerate `wiki-index.md` frontmatter | `--title`, `--subtitle` |
| `setup` | Install SKILL.md for Claude Code / OpenCode / Codex | — |

### Export formats

| `--format` | Output | Use case |
|---|---|---|
| `json` | Full entry objects | Programmatic processing |
| `md` | Markdown with headers | Human reading or diffing |
| `bibtex-context` | Clean prose, no LaTeX or wikilinks | LLM paper-writing prompts |

## Configuration

`ob-wiki` resolves the vault root in this order:

1. `--vault PATH` flag
2. `OB_WIKI_VAULT` environment variable
3. Walk up from the current working directory until a `_Wiki/` directory is found

Entry types are discovered from subdirectory names — any folder inside `_Wiki/`
containing `.md` files (excluding `spec/`, `docs/`, `views/`) is a valid type
namespace. The standard layout uses `topics/` and `methods/`.

## Notes

- All commands except `init`, `new`, `index`, and `setup` are read-only.
- `new --dry-run` prints the template without writing — always preview first.
- Zero external dependencies — pure Python stdlib, works with Python 3.8+.
- Works directly against the vault filesystem; Obsidian does not need to be running.
- `wiki-index.md` requires the [Dataview](https://github.com/blacksmithgu/obsidian-dataview)
  plugin to render inside Obsidian.

## License

MIT
