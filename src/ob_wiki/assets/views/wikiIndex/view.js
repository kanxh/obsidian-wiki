const {
  root = "_Wiki",
  title = "Obsidian-Wiki",
  subtitle = "A compact map of topics, methods, and recent movement across the compiled wiki layer."
} = input;

const hyperTagConfigPath = `${root}/spec/hyper-tags.yaml`;
const fallbackHyperTagOrder = [];

function parseHyperTagRegistry(yamlText) {
  const lines = String(yamlText ?? "").split("\n");
  const registryIndex = lines.findIndex(line => line.trim() === "registry:");
  if (registryIndex === -1) return [];

  const keys = [];
  for (let i = registryIndex + 1; i < lines.length; i += 1) {
    const line = lines[i];
    if (!line.trim()) continue;
    if (!/^\s+/.test(line)) break;

    const match = line.match(/^\s*-\s+key:\s*([a-z0-9-]+)\s*$/);
    if (match) keys.push(match[1]);
  }

  return keys;
}

async function loadHyperTagOrder() {
  try {
    const yamlText = await app.vault.adapter.read(hyperTagConfigPath);
    const parsed = parseHyperTagRegistry(yamlText);
    if (parsed.length) return parsed;
  } catch (_) {
    // Fall through to the baked-in default if the config file cannot be read.
  }

  return fallbackHyperTagOrder;
}

const hyperTagOrder = await loadHyperTagOrder();

const hyperTagSet = new Set(hyperTagOrder);

const _nonEntryDirs = new Set(["spec", "docs", "views"]);

const allEntries = dv.pages(`"${root}"`)
  .where(p => {
    const parts = p.file.path.split("/");
    const subdir = parts[parts.indexOf("_Wiki") + 1];
    return subdir && !_nonEntryDirs.has(subdir) && p.type;
  })
  .sort(p => p.file.name, "asc")
  .array();

const typeOrder = [...new Set(allEntries.map(p => p.type))].sort();

const byType = {};
typeOrder.forEach(t => {
  byType[t] = allEntries.filter(p => p.type === t);
});

const recent = [...allEntries]
  .filter(p => p.updated)
  .sort((a, b) => String(b.updated).localeCompare(String(a.updated)))
  .slice(0, 6);

function toArray(value) {
  if (!value) return [];
  if (Array.isArray(value)) return value;
  if (typeof value.array === "function") return value.array();
  return [value];
}

function getHyperTags(page) {
  const explicit = toArray(page.hyper_tags).filter(Boolean);
  const base = explicit.length
    ? explicit
    : toArray(page.tags).filter(tag => hyperTagSet.has(tag));
  const seen = new Set();
  const ordered = base
    .filter(tag => hyperTagSet.has(tag))
    .filter(tag => {
      if (seen.has(tag)) return false;
      seen.add(tag);
      return true;
    });

  return ordered.sort((a, b) => hyperTagOrder.indexOf(a) - hyperTagOrder.indexOf(b));
}

const allHyperTags = allEntries.flatMap(getHyperTags);
const uniqueHyperTags = [...new Set(allHyperTags)];
const latestUpdated = allEntries
  .map(p => p.updated)
  .filter(Boolean)
  .sort((a, b) => String(b).localeCompare(String(a)))[0] ?? "—";

const host = dv.el("div", "", { cls: "wikiIndex" });

function text(el, tag, value, cls) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  node.textContent = value;
  el.appendChild(node);
  return node;
}

function formatDate(value) {
  if (!value) return "—";
  if (typeof value === "string") return value.slice(0, 10);
  if (typeof value.toFormat === "function") return value.toFormat("yyyy-MM-dd");
  if (value.ts) return window.moment(value.ts).format("YYYY-MM-DD");
  return String(value).slice(0, 10);
}

function link(el, page, cls = "") {
  const wrap = document.createElement("div");
  if (cls) wrap.className = cls;
  const a = document.createElement("a");
  a.className = "internal-link";
  a.href = page.file.path;
  a.dataset.href = page.file.path;
  a.textContent = page.file.name;
  wrap.appendChild(a);
  el.appendChild(wrap);
  return a;
}

function iconPathLink(el, path, name, symbol, cls = "") {
  const wrap = document.createElement("a");
  wrap.className = `internal-link ${cls}`.trim();
  wrap.href = path;
  wrap.dataset.href = path;
  wrap.title = name;

  const icon = document.createElement("span");
  icon.className = "wikiIndex-navIconGlyph";
  icon.textContent = symbol;
  wrap.appendChild(icon);

  el.appendChild(wrap);
  return wrap;
}

function hyperTagPills(el, tags = []) {
  if (!tags.length) return;
  const row = document.createElement("div");
  row.className = "wikiIndex-hyperTags";
  el.appendChild(row);
  tags.forEach(tag => {
    const pill = document.createElement("span");
    pill.className = `wikiIndex-hyperTag wikiIndex-hyperTag--${tag}`;
    pill.textContent = tag;
    row.appendChild(pill);
  });
}

function listSection(titleText, pages) {
  const section = document.createElement("section");
  section.className = "wikiIndex-section";
  host.appendChild(section);

  const heading = document.createElement("div");
  heading.className = "wikiIndex-sectionHead";
  section.appendChild(heading);
  text(heading, "h2", titleText, "wikiIndex-sectionTitle");
  text(heading, "span", `${pages.length}`, "wikiIndex-count");

  const list = document.createElement("div");
  list.className = "wikiIndex-list";
  section.appendChild(list);

  pages.forEach(page => {
    const row = document.createElement("article");
    row.className = "wikiIndex-row wikiIndex-entry";
    list.appendChild(row);

    const main = document.createElement("div");
    main.className = "wikiIndex-entryMain";
    row.appendChild(main);
    link(main, page, "wikiIndex-link");

    const meta = document.createElement("div");
    meta.className = "wikiIndex-rowMeta";
    row.appendChild(meta);
    hyperTagPills(meta, getHyperTags(page));
    if (page.updated) {
      text(meta, "span", formatDate(page.updated), "wikiIndex-date");
    }
  });
}

function simpleList(titleText, pages) {
  const section = document.createElement("section");
  section.className = "wikiIndex-section wikiIndex-sectionCompact";
  host.appendChild(section);

  text(section, "h2", titleText, "wikiIndex-sectionTitle");

  const list = document.createElement("div");
  list.className = "wikiIndex-list";
  section.appendChild(list);

  pages.forEach(page => {
    const row = document.createElement("article");
    row.className = "wikiIndex-row wikiIndex-entry";
    list.appendChild(row);

    const main = document.createElement("div");
    main.className = "wikiIndex-entryMain";
    row.appendChild(main);
    link(main, page, "wikiIndex-link");

    const meta = document.createElement("div");
    meta.className = "wikiIndex-rowMeta";
    row.appendChild(meta);
    hyperTagPills(meta, getHyperTags(page));
    if (page.updated) {
      text(meta, "span", formatDate(page.updated), "wikiIndex-date");
    }
  });
}

const hero = document.createElement("section");
hero.className = "wikiIndex-hero";
host.appendChild(hero);

text(hero, "div", "Compiled layer", "wikiIndex-kicker");
text(hero, "h1", title, "wikiIndex-title");
text(hero, "p", subtitle, "wikiIndex-subtitle");

const stats = document.createElement("div");
stats.className = "wikiIndex-stats";
hero.appendChild(stats);

const statsData = [
  ...typeOrder.map(t => [t.charAt(0).toUpperCase() + t.slice(1) + "s", String(byType[t].length)]),
  ["Hyper-tags", String(uniqueHyperTags.length)],
  ["Updated", formatDate(latestUpdated)],
];

statsData.forEach(([label, value]) => {
  const stat = document.createElement("div");
  stat.className = "wikiIndex-stat";
  stats.appendChild(stat);
  text(stat, "span", label, "wikiIndex-statLabel");
  text(stat, "strong", value, "wikiIndex-statValue");
});

const nav = document.createElement("div");
nav.className = "wikiIndex-nav";
hero.appendChild(nav);
[
  { path: `${root}/README.md`, name: "README", symbol: "⌂" },
  { path: `${root}/spec/wiki-convention.md`, name: "Conventions", symbol: "≡" }
].forEach(item => {
  iconPathLink(nav, item.path, item.name, item.symbol, "wikiIndex-navIcon");
});

typeOrder.forEach(t => {
  const label = t.charAt(0).toUpperCase() + t.slice(1) + "s";
  listSection(label, byType[t]);
});
simpleList("Recent", recent);
