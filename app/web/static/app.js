// Wilayah Indonesia demo. Everything on the page is driven by the public API; nothing is precomputed here.

const $ = (selector, root = document) => root.querySelector(selector);
const number = new Intl.NumberFormat("en-US");

/** Create an element. Text children are set as text, never parsed as HTML. */
function h(tag, props = {}, ...children) {
  const element = document.createElement(tag);
  for (const [key, value] of Object.entries(props)) {
    if (value === undefined || value === null || value === false) continue;
    if (key.startsWith("on")) element.addEventListener(key.slice(2), value);
    else if (key.startsWith("--")) element.style.setProperty(key, value);
    else if (key === "className") element.className = value;
    else element.setAttribute(key, value === true ? "" : value);
  }
  return fill(element, ...children);
}

/** Replace an element's children, skipping empty values so conditional parts can be written inline. */
function fill(element, ...children) {
  element.replaceChildren(...children.flat(Infinity).filter((child) => child !== null && child !== undefined && child !== false));
  return element;
}

// Levels come from the server-rendered form, so labels live in one place (app/web/pages.py).
const fields = [...document.querySelectorAll(".field[data-level]")];
const TYPES = fields.map((field) => field.dataset.type);
const LABELS = Object.fromEntries(fields.map((field) => [field.dataset.type, field.dataset.label]));
const PLURALS = Object.fromEntries(fields.map((field) => [field.dataset.type, field.dataset.plural]));
const lower = (type) => LABELS[type].toLowerCase();
const COMPOSITIONS = [
  { title: "Regencies and cities", keys: ["regency", "city"], below: 2 },
  { title: "Village status", keys: ["rural_village", "urban_village", "customary_village"], below: 4 },
];
// API kind keys: English name first, the official Indonesian term beside it.
const KIND_LABELS = {
  regency: ["Regency", "kabupaten"],
  city: ["City", "kota"],
  rural_village: ["Rural village", "desa"],
  urban_village: ["Urban village", "kelurahan"],
  customary_village: ["Customary village", "desa adat"],
};
const RANK_LIMIT = 12;

/* ---------- API client with a visible request log ---------- */

const cache = new Map();
const log = [];
let shown = null;

function request(path) {
  if (!cache.has(path)) cache.set(path, send(path));
  return cache.get(path);
}

async function send(path) {
  const started = performance.now();
  let entry;
  try {
    // Revalidate so a response cached by an older release never meets newer page code.
    const response = await fetch(path, { cache: "no-cache", headers: { Accept: "application/json" } });
    entry = { path, status: response.status, body: await response.json() };
  } catch (error) {
    cache.delete(path);
    entry = { path, status: 0, body: { success: false, error: { code: "NETWORK_ERROR", message: String(error), hint: "Check your connection and try again." } } };
  }
  entry.ms = Math.round(performance.now() - started);
  log.unshift(entry);
  log.length = Math.min(log.length, 20);
  renderLog();
  return entry;
}

function show(entry) {
  shown = entry;
  $("#response-path").textContent = `GET ${entry.path} · ${entry.status || "failed"} · ${entry.ms} ms`;
  $("#response-body").innerHTML = highlight(entry.body);
  renderLog();
}

function highlight(value) {
  const escaped = JSON.stringify(value, null, 2).replace(/[&<>]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" })[char]);
  return escaped.replace(
    /("(?:\\.|[^"\\])*")(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?/g,
    (match, string, colon, literal) => {
      if (string) return colon ? `<span class="j-key">${string}</span>${colon}` : `<span class="j-str">${string}</span>`;
      return `<span class="${literal ? "j-lit" : "j-num"}">${match}</span>`;
    },
  );
}

function renderLog() {
  $("#console-count").textContent = log.length ? `${log.length} sent, newest first` : "";
  fill($("#log"),
    ...log.map((entry) =>
      h("li", {},
        h("button", { type: "button", "aria-current": entry === shown ? "true" : null, onclick: () => show(entry) },
          h("span", { className: entry.body.success ? "status-ok" : "status-error" }, String(entry.status || "ERR")),
          h("span", { className: "path" }, entry.path),
          h("span", { className: "ms" }, `${entry.ms} ms`),
        ),
      ),
    ),
  );
}

/* ---------- Combobox (ARIA 1.2 pattern, list autocomplete) ---------- */

class Combobox {
  constructor(field, onChoose) {
    this.input = $("input", field);
    this.list = $("[role=listbox]", field);
    this.onChoose = onChoose;
    this.items = [];
    this.matches = [];
    this.selected = null;
    this.active = -1;

    this.input.addEventListener("focus", () => this.open(""));
    this.input.addEventListener("click", () => this.list.hidden && this.open(""));
    this.input.addEventListener("input", () => this.open(this.input.value));
    this.input.addEventListener("blur", () => this.close());
    this.input.addEventListener("keydown", (event) => this.onKey(event));
    // Keep focus in the input while an option is pressed, so blur does not close the list first.
    this.list.addEventListener("pointerdown", (event) => event.preventDefault());
    this.list.addEventListener("click", (event) => {
      const option = event.target.closest("[role=option]");
      if (option) this.choose(this.matches[Number(option.dataset.index)]);
    });
  }

  load(items, placeholder) {
    this.items = items;
    this.input.disabled = items.length === 0;
    this.input.placeholder = placeholder;
    this.select(null);
  }

  select(item) {
    this.selected = item;
    this.input.value = item ? item.name : "";
  }

  open(query) {
    const needle = query.trim().toLowerCase();
    this.matches = needle
      ? this.items.filter((item) => item.name.toLowerCase().includes(needle) || item.short_code.startsWith(needle) || String(item.code).startsWith(needle))
      : this.items;
    this.active = Math.max(this.matches.indexOf(this.selected), 0);
    fill(this.list,
      ...(this.matches.length
        ? this.matches.map((item, index) => this.option(item, index, needle))
        : [h("li", { className: "option-empty", role: "presentation" }, "No match")]),
    );
    this.list.hidden = false;
    this.input.setAttribute("aria-expanded", "true");
    this.paint();
  }

  option(item, index, needle) {
    const at = needle ? item.name.toLowerCase().indexOf(needle) : -1;
    const name = at < 0
      ? item.name
      : [item.name.slice(0, at), h("mark", {}, item.name.slice(at, at + needle.length)), item.name.slice(at + needle.length)];
    return h("li", { id: `${this.list.id}-${item.code}`, role: "option", "data-index": index, "aria-selected": String(item === this.selected) },
      h("span", {}, name),
      h("span", { className: "option-code" }, item.short_code),
    );
  }

  close() {
    this.list.hidden = true;
    this.input.setAttribute("aria-expanded", "false");
    this.input.removeAttribute("aria-activedescendant");
    this.input.value = this.selected ? this.selected.name : "";
  }

  choose(item) {
    this.selected = item;
    this.close();
    this.onChoose(item);
  }

  paint() {
    const options = this.list.querySelectorAll("[role=option]");
    options.forEach((option, index) => option.classList.toggle("is-active", index === this.active));
    const current = options[this.active];
    if (current) {
      this.input.setAttribute("aria-activedescendant", current.id);
      current.scrollIntoView({ block: "nearest" });
    }
  }

  onKey(event) {
    const isOpen = !this.list.hidden;
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      if (!isOpen) return this.open("");
      const count = this.matches.length;
      if (count) this.active = (this.active + (event.key === "ArrowDown" ? 1 : -1) + count) % count;
      this.paint();
    } else if (event.key === "Enter" && isOpen && this.matches[this.active]) {
      event.preventDefault();
      this.choose(this.matches[this.active]);
    } else if (event.key === "Escape" && isOpen) {
      event.preventDefault();
      this.close();
    }
  }
}

/* ---------- Explorer state ---------- */

const pickers = fields.map((field, index) => new Combobox(field, (item) => navigate([...path.slice(0, index), item])));
const withParent = $("#with-parent");
let path = []; // Selected regions, province first.
let version = 0; // Discards responses that arrive after a newer selection.

const listPath = (regions) => (regions.length ? `/api/${regions.map((region) => region.code).join("/")}` : "/api/0");
const lookupPath = (region) => `/api/code/${region.code}?parent=${withParent.checked}`;

async function navigate(regions) {
  path = regions;
  const current = ++version;
  const url = new URL(location.href);
  url.searchParams.delete("kode"); // Older links used ?kode=.
  if (path.length) url.searchParams.set("code", path.at(-1).code);
  else url.searchParams.delete("code");
  history.replaceState(null, "", url);

  renderTrail();
  renderDetail();

  const last = path.at(-1);
  const loads = pickers.map((picker, index) => {
    if (index > path.length || (index === path.length && last && !last.has_children)) {
      picker.load([], `Select ${lower(TYPES[index - 1])} first`);
      return null;
    }
    return loadPicker(index, current);
  });
  await Promise.all(loads);
  if (current !== version) return;
  if (last) show(await request(lookupPath(last)));
  renderAnalytics(current);
}

async function loadPicker(index, current) {
  const entry = await request(listPath(path.slice(0, index)));
  if (current !== version) return;
  const items = entry.body.success ? entry.body.data.items : [];
  pickers[index].load(items, `Select ${lower(TYPES[index])} (${items.length})`);
  pickers[index].select(items.find((item) => item.code === path[index]?.code) ?? null);
  if (!path.length && index === 0) show(entry);
}

/** Resolve any lookup URL into a chain of regions, then select it. Returns the lookup entry. */
async function openLookup(lookupUrl) {
  const entry = await request(lookupUrl);
  show(entry);
  if (!entry.body.success) return entry;
  const chain = [];
  for (let node = entry.body.data; node; node = node.parent) chain.unshift({ ...node, has_children: node.has_children ?? true });
  await navigate(chain);
  return entry;
}

function renderTrail() {
  const crumbs = [{ name: "Indonesia" }, ...path];
  fill($("#trail"),
    ...crumbs.flatMap((region, index) => [
      index ? h("span", { className: "sep", "aria-hidden": "true" }, "/") : null,
      index === crumbs.length - 1
        ? h("span", { "aria-current": "location" }, region.name)
        : h("button", { type: "button", onclick: () => navigate(path.slice(0, index)) }, region.name),
    ]),
  );
}

function renderDetail() {
  const region = path.at(-1);
  if (!region) {
    fill($("#detail"), h("p", { className: "empty" }, "Nothing selected yet. Choose a province to start, or open any row in the analytics below."));
    return;
  }
  const parent = path.at(-2);
  const calls = [
    [`/api/code/${region.code}?parent=true`, "Lookup with the full parent chain"],
    [`/api/s/${region.short_code}`, "Same region through the shorthand route"],
    region.has_children && [`${listPath(path)}?parent=true`, `List every ${lower(TYPES[region.depth])} inside`],
    region.has_children && [`/api/stats/${region.code}`, "Descendant totals used by the analytics"],
  ].filter(Boolean);

  fill($("#detail"),
    h("p", { className: "detail-kind" }, `${LABELS[region.type]} · level ${region.depth} of 4`),
    h("h3", { className: "detail-name" }, region.name),
    h("dl", { className: "facts" },
      fact("Code", h("span", { className: "mono" }, String(region.code))),
      fact("Short code", h("span", { className: "mono" }, region.short_code)),
      fact("Type", region.type),
      fact("Parent", parent ? parent.name : "Indonesia"),
    ),
    h("ul", { className: "calls", "aria-label": "Try these requests" },
      calls.map(([url, label]) =>
        h("li", {},
          h("button", { type: "button", onclick: async () => show(await request(url)) },
            h("code", {}, `GET ${url}`),
            h("span", { className: "help" }, label),
          ),
        ),
      ),
    ),
  );
}

const fact = (term, value) => h("div", {}, h("dt", {}, term), h("dd", {}, value));

/* ---------- Analytics ---------- */

let metric = "village";
let expanded = false;
let rankedScope = null; // "Show all" resets when the scope changes.

async function renderAnalytics(current) {
  const scopeIndex = path.findLastIndex((region) => region.depth < 4);
  const scopePath = path.slice(0, scopeIndex + 1);
  const scope = scopePath.at(-1);
  const depth = scope ? scope.depth : 0;
  const statsUrl = `/api/stats/${scope ? scope.code : 0}`;
  const entry = await request(statsUrl);
  if (current !== version) return;
  if (statsUrl !== rankedScope) [rankedScope, expanded] = [statsUrl, false];

  $("#scope-name").textContent = scope ? scope.name : "Indonesia";
  $("#scope-path").textContent = statsUrl;
  const body = $("#analytics-body");
  if (!entry.body.success) {
    fill(body, h("p", { className: "field-error" }, entry.body.error.message));
    return;
  }

  const { levels, kinds, children } = entry.body.data;
  const metrics = TYPES.slice(depth + 1);
  if (!metrics.includes(metric)) metric = metrics.at(-1);

  fill(body,
    h("dl", { className: "figures" }, TYPES.slice(depth).map((type) => fact(PLURALS[type], number.format(levels[type])))),
    h("div", { className: "splits" },
      COMPOSITIONS.filter((composition) => depth < composition.below).map((composition) => split(composition, kinds)),
    ),
    metrics.length ? ranking(children, depth, metrics, scopePath, current) : null,
  );
}

function split({ title, keys }, kinds) {
  const parts = keys.map((key, index) => ({ key, value: kinds[key], color: `var(--series-${index + 1})` })).filter((part) => part.value);
  const total = parts.reduce((sum, part) => sum + part.value, 0);
  const share = (value) => `${((value / total) * 100).toFixed(value / total < 0.01 ? 2 : 1)}%`;
  return h("figure", {},
    h("figcaption", {}, h("h3", {}, title)),
    h("div", { className: "split-bar", role: "img", "aria-label": parts.map((part) => `${KIND_LABELS[part.key][0]} ${number.format(part.value)}`).join(", ") },
      parts.map((part) => h("span", { "--value": part.value, "--color": part.color, title: `${KIND_LABELS[part.key].join(", ")}: ${number.format(part.value)} (${share(part.value)})` })),
    ),
    h("ul", { className: "legend" },
      parts.map((part) =>
        h("li", {},
          h("span", { className: "swatch", "--color": part.color, "aria-hidden": "true" }),
          `${KIND_LABELS[part.key][0]} `,
          h("i", { lang: "id", className: "term" }, KIND_LABELS[part.key][1]),
          " ",
          h("span", { className: "value" }, `${number.format(part.value)} · ${share(part.value)}`),
        ),
      ),
    ),
  );
}

function ranking(children, depth, metrics, scopePath, current) {
  const rows = [...children].sort((a, b) => b.levels[metric] - a.levels[metric]);
  const max = rows[0]?.levels[metric] || 1;
  const visible = expanded ? rows : rows.slice(0, RANK_LIMIT);
  const rerender = () => renderAnalytics(current);

  return h("div", {},
    h("div", { className: "ranking-head" },
      h("h3", {}, `${PLURALS[TYPES[depth]]} ranked by ${lower(metric)} count`),
      metrics.length > 1 && h("fieldset", { className: "segmented" },
        h("legend", { className: "sr-only" }, "Rank by"),
        metrics.map((type) =>
          h("label", {},
            h("input", { type: "radio", name: "metric", value: type, checked: type === metric, onchange: () => { metric = type; rerender(); } }),
            h("span", {}, PLURALS[type]),
          ),
        ),
      ),
    ),
    h("ol", { className: "bars" },
      visible.map(({ region, levels }) =>
        h("li", { title: metrics.map((type) => `${PLURALS[type]}: ${number.format(levels[type])}`).join("\n") },
          h("button", { className: "bar-name", type: "button", onclick: () => navigate([...scopePath, region]) }, region.name),
          h("span", { className: "bar-track", "aria-hidden": "true" }, h("span", { className: "bar-fill", "--share": `${(levels[metric] / max) * 100}%` })),
          h("span", { className: "bar-value" }, number.format(levels[metric])),
        ),
      ),
    ),
    rows.length > RANK_LIMIT && h("button", { className: "button-quiet more", type: "button", onclick: () => { expanded = !expanded; rerender(); } },
      expanded ? "Show top 12" : `Show all ${rows.length}`),
  );
}

/* ---------- Jump to code ---------- */

function jumpUrl(raw) {
  const value = raw.trim();
  if (/^\d+$/.test(value)) return `/api/code/${value}?parent=true`;
  const segments = value.split(/[./\s-]+/).filter(Boolean);
  if (segments.length && segments.length <= 4 && segments.every((segment) => /^\d+$/.test(segment))) {
    return `/api/s/${segments.map(Number).join("/")}?parent=true`;
  }
  return null;
}

$("#jump").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = $("#jump-input");
  const message = $("#jump-error");
  const url = jumpUrl(input.value);
  const entry = url && (await openLookup(url));
  const error = url ? !entry.body.success && entry.body.error : { message: "Enter digits, optionally split by slashes or dots." };

  input.setAttribute("aria-invalid", String(Boolean(error)));
  message.hidden = !error;
  fill(message,
    ...(error ? [error.code ? `${error.code}: ` : "", `${error.message} `, error.hint ?? "", " ", error.docs ? h("a", { href: error.docs }, "Details") : ""] : []),
  );
  if (!error) $("#explorer").scrollIntoView({ block: "start" });
});

/* ---------- Page wiring ---------- */

withParent.addEventListener("change", async () => {
  const last = path.at(-1);
  if (last) show(await request(lookupPath(last)));
});

document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-copy]");
  if (!button) return;
  const label = button.textContent;
  try {
    await navigator.clipboard.writeText($(button.dataset.copy).textContent);
    button.textContent = "Copied";
  } catch {
    button.textContent = "Copy failed";
  }
  setTimeout(() => { button.textContent = label; }, 1500);
});

const params = new URLSearchParams(location.search);
const initialCode = params.get("code") ?? params.get("kode");
if (!initialCode || (await openLookup(`/api/code/${encodeURIComponent(initialCode)}?parent=true`)).body.success === false) {
  navigate([]);
}
