# Wiki Conventions

`_Wiki/` is the compiled wiki layer of the vault. It should read like compact standalone entries, not like a tour of project notes.

## Structure

- Define your entry types in subdirectories (e.g. `topics/`, `methods/`). Add more as needed.
- Use `_Wiki/docs/` only for operating notes such as this file.
- Do not create separate source-summary pages.

## Frontmatter

Every entry should have:

```yaml
---
type: topic | method
status: active
created: YYYY-MM-DD
updated: YYYY-MM-DD
hyper_tags:
  - tag-a
tags:
  - tag-a
  - detail-tag-b
---
```

Rules:
- keep `created`
- update `updated` on real revisions
- keep `hyper_tags` for the top retrieval layer
- keep tags in frontmatter, plain and short
- `hyper_tags` must be lowercase kebab-case
- `hyper_tags` should describe the page object itself, not only one use case of it
- sync `hyper_tags` to the front of `tags`
- keep `tags` for finer-grained retrieval beneath the top layer
- do not encode page type in tags

Hyper-tag rules:
- use 1 to 2 `hyper_tags` in most cases
- define your registry in `spec/hyper-tags.yaml`
- add a hyper-tag only when it is intrinsic to the entry itself
- generic methods should keep only their own method-family hyper-tag
- maintain the registry in [[spec/hyper-tags.yaml]]

## Writing

- Start from the concept or method itself, not from the vault.
- First sentence defines the object.
- Prefer 1 to 3 short paragraphs plus one final links block.
- It is fine to compress or restate source-note content when that helps the page stand alone.
- Avoid rigid section templates unless a page clearly needs them.

## Formulas

- Add formulas only when they sharpen the definition of the object itself.
- Prefer 1 compact defining formula, or at most 2 to 3 short formulas.
- Do not turn wiki pages into math notes or derivations.
- In Obsidian, use `$$...$$` for block formulas and `$...$` for inline formulas.
- Keep formula-adjacent prose short and plain.

## Extraction standard

Extract something into `_Wiki/` when it is already a stable retrieval unit:
- it can be defined cleanly
- it connects multiple notes, or notes plus papers
- it links naturally to neighboring wiki entries
- it is likely to recur across your research

Do not extract something just because it appears in one note. Leave one-off details and narrow formulas in raw notes until they sharpen.

## Granularity

- Aim for medium granularity.
- Too small: individual variants of a concept when a single page covers both.
- Too large: broad research themes or full pipelines.

## Links

Use inline `[[...]]` links naturally in the summary. End every page with:

```md
> [!related]+ Links
> Wiki: [[...]]
> Clippings: [[...]]
> Notes: [[...]]
> Papers: [[...]]
```

- `Wiki:` nearby compiled entries in `_Wiki/`
- `Clippings:` source clips from your clippings folder
- `Notes:` raw notes, working notes, or literature notes
- `Papers:` notes linked to papers in your reference manager
- Omit any section that has no links; do not leave empty lines in the block

## Maintenance

- preserve summary-first prose
- keep the final links block
- update `updated` when content changes meaningfully
