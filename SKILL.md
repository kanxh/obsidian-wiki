# ob-wiki skill

Use the `ob-wiki` CLI to manage an Obsidian `_Wiki/` research wiki. Invoke this
skill whenever the user asks about their wiki entries, wants to scaffold new
pages, check wiki health, search concepts, export content for writing, or track
which papers are cited across the wiki.

## Activation triggers

- "my wiki", "in my wiki", "list wiki entries", "wiki entries about…"
- "add a wiki entry", "scaffold a new topic/method page", "create a wiki page for…"
- "lint my wiki", "wiki health check", "check for orphan entries"
- "show me [entry name]" when the name sounds like a research concept
- "search the wiki for …"
- "export wiki context", "wiki entries for my paper", "paper writing context"
- "what papers are cited in the wiki", "which papers appear across entries"
- `/ob-wiki`

## Before you start

Verify the tool is installed and the vault is reachable:
```
which ob-wiki && ob-wiki stats
```
If `ob-wiki` is not found: `pip install git+https://github.com/kanxh/ob-wiki.git`

## Core patterns

### List and filter
```bash
ob-wiki list                                   # all entries
ob-wiki list --type method --json              # methods as JSON
ob-wiki list --hyper-tag statistics --since 2026-01-01
```

### Show a single entry
```bash
ob-wiki show HMM
ob-wiki show "thermal comfort" --json          # partial name match
```

### Stats
```bash
ob-wiki stats
ob-wiki stats --json
```

### Search
```bash
ob-wiki search "state space" --json
ob-wiki search climate --type topic
```

### Papers cited in wiki
```bash
ob-wiki papers --json                          # all cited papers
ob-wiki papers --hyper-tag statistics          # filtered by tag
```

### Export for paper writing
```bash
# Clean LLM-digestible context (strips LaTeX, wikilinks, callouts)
ob-wiki export --format bibtex-context --hyper-tag statistics

# Markdown export of recent entries
ob-wiki export --format md --since 2026-01-01 --output context.md

# Full JSON export
ob-wiki export --format json > wiki.json
```

### Lint / health check
```bash
ob-wiki lint
ob-wiki lint --json
```

### Scaffold a new entry
```bash
# Always use --dry-run first to preview
ob-wiki new "Gaussian Process" --type method --hyper-tag statistics --dry-run
ob-wiki new "Gaussian Process" --type method --hyper-tag statistics
```

### Refresh wiki-index.md
```bash
ob-wiki index
ob-wiki index --title "My Wiki" --subtitle "Research knowledge base"
```

## JSON output shapes

**list / search:**
```json
[{"name": "HMM", "type": "method", "hyper_tags": ["statistics"], "updated": "2026-04-09"}]
```

**show / export json:**
```json
{"name": "HMM", "type": "method", "hyper_tags": [...], "body": "...", "related": {...}}
```

**stats:**
```json
{"total_topics": 26, "total_methods": 24, "hyper_tag_counts": [...], "recently_updated": [...]}
```

**papers:**
```json
[{"paper": "sAMY 1.0", "cited_by": ["EPW weather file", "TMY"]}]
```

**lint:**
```json
[{"entry": "RC model", "check": "missing-related-block", "severity": "warning", "message": "..."}]
```

## Tips

- Always pass `--json` when you need structured output for further processing.
- Use `ob-wiki lint --json` before bulk operations to check wiki state.
- Use `--format bibtex-context` when building a "write related work" prompt — it
  produces clean paragraphs with no LaTeX or Obsidian syntax.
- `ob-wiki papers` is the fastest way to find entries sharing a literature
  foundation — useful for discovering implicit clusters.
- `--vault` overrides auto-detection; set `OB_WIKI_VAULT` in the environment to
  avoid passing it on every call.
