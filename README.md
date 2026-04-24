# ob-wiki

Manage an Obsidian research wiki from the command line — list and search
entries, scaffold new pages with schema-compliant frontmatter, run health
checks, export content as context for paper writing, and track which papers are
cited across your knowledge base.

Designed for researchers who maintain a structured personal wiki on top of their
literature notes and project notes in Obsidian.

> Inspired by Andrej Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
> pattern: instead of re-deriving knowledge on every query, an LLM incrementally
> builds and maintains a persistent, interlinked collection of markdown files that
> sits between you and your raw sources.

## Wiki Schema

The schema that `ob-wiki` reads is a deliberate balance between two organizational
philosophies:

```
type → hyper_tags → tags → [[wikilinks]]
 │          │         │          │
tree      sparse    dense      network
(coarse)  skeleton  fabric    (full graph)
```

**`type`** is the coarsest structural layer. Each entry belongs to one type,
stored in a matching subdirectory (`topics/`, `methods/`, or any other
user-defined folder). Types impose the minimal folder hierarchy — just enough
to separate fundamentally different kinds of knowledge objects (e.g., domain
concepts vs. modeling techniques). `ob-wiki` discovers types from your vault's
subdirectory layout; none are hardcoded into the tool.

**`hyper_tags`** (1–2 per entry, from a registry in `spec/hyper-tags.yaml`)
define the minimal branching structure above individual entries. Think of them
as the top-level chapters of a textbook: few enough to stay meaningful, stable
enough to use as a navigation skeleton. They form the sparse tree that makes
the wiki browsable without imposing rigid hierarchy everywhere.

**`tags`** are the dense fabric. Finer-grained, unconstrained, many per entry.
Where hyper_tags provide the skeleton, tags capture the actual conceptual
neighborhood of each entry. They drive search, filtering, and discovery.
By convention, `hyper_tags` are always copied to the front of `tags` so both
fields remain consistent.

**`[[wikilinks]]`** complete the network. They express direct conceptual
dependencies between entries — the edges that turn the tree structure into a
true knowledge graph. The `papers` command exploits this layer to surface which
papers are cited across multiple entries, revealing implicit literature clusters.

The result is not a pure hierarchy (too rigid for research concepts that span
multiple domains) nor a pure tag cloud (too flat to browse). It is a tree
skeleton with a network overlaid on top.

## Core Capabilities

- List wiki entries with filters by type, hyper-tag, and date
- Search by keyword or tag with relevance scoring
- Scaffold new entries with correct frontmatter in one command
- Health-check the wiki for orphans, missing link blocks, and schema violations
- Export entries as clean prose context for LLM paper-writing prompts
- Aggregate paper citations across wiki entries to surface shared literature
- Regenerate `wiki-index.md` frontmatter in place
- Install as a skill for Claude Code, OpenCode, and Codex

## Installation

> macOS — requires Python 3.8+ (ships with macOS) or use `uv`

```bash
# uv (recommended — installs in an isolated environment)
uv tool install git+https://github.com/kanxh/ob-wiki.git

# pip
pip install git+https://github.com/kanxh/ob-wiki.git
```

After installation, register the skill with your AI tools:

```bash
ob-wiki setup
```

This installs `SKILL.md` to:

| Tool | Path |
|---|---|
| Claude Code | `~/.claude/skills/ob-wiki/SKILL.md` |
| OpenCode | `~/.config/opencode/skills/ob-wiki/SKILL.md` |
| Codex | `~/.codex/skills/ob-wiki/SKILL.md` |

Any tool detected on your system is installed automatically.

## Quick Start

```bash
# Show wiki statistics
ob-wiki stats

# List all method entries
ob-wiki list --type method

# Show a specific entry
ob-wiki show HMM

# Search for entries related to "thermal comfort"
ob-wiki search "thermal comfort" --json

# Check wiki health
ob-wiki lint

# Export context for writing a related work section
ob-wiki export --format bibtex-context --hyper-tag statistics

# Scaffold a new entry
ob-wiki new "Gaussian Process" --type method --hyper-tag statistics --dry-run
ob-wiki new "Gaussian Process" --type method --hyper-tag statistics
```

## Commands

| Command | Description | Key flags |
|---|---|---|
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

The tool reads entry types from your vault's subdirectory structure — no types
are hardcoded. Any subdirectory of `_Wiki/` that contains `.md` files (excluding
`spec/`, `docs/`, `views/`) is treated as a type namespace. The standard layout
uses `topics/` and `methods/`, but you can define your own.

## Notes

- All commands except `new`, `index`, and `setup` are read-only.
- `new --dry-run` prints the template without writing — always preview first.
- Zero external dependencies — pure Python stdlib, works with Python 3.8+.
- Works directly against the vault filesystem; the Obsidian app does not need
  to be running.

## License

MIT
