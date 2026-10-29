// Shared helpers for the index and history pages.

const numberFormat = new Intl.NumberFormat("en-GB", { maximumFractionDigits: 2 });

function formatNumber(value) {
  return numberFormat.format(value);
}

// Today's date in Belgium as YYYY-MM-DD; days before it are complete.
function todayInBrussels() {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Brussels" }).format(new Date());
}

function formatDay(isoDate, options = { weekday: "long", day: "numeric", month: "long", year: "numeric" }) {
  const [y, m, d] = isoDate.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString("en-GB", { ...options, timeZone: "UTC" });
}

function formatTime(isoDateTime) {
  return new Date(isoDateTime).toLocaleTimeString("en-GB", {
    hour: "2-digit", minute: "2-digit", timeZone: "Europe/Brussels",
  });
}

async function loadJson(path) {
  const response = await fetch(path, { cache: "no-cache" });
  if (!response.ok) throw new Error(`${path}: ${response.status}`);
  return response.json();
}

function loadSummary() {
  return loadJson("data/summary.json");
}

function loadDay(isoDate) {
  return loadJson(`data/days/${isoDate.slice(0, 4)}/${isoDate}.json`);
}

// Small DOM builder: el("a", { href: "x", class: "y" }, "text", child)
function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value === undefined || value === null || value === false) continue;
    if (key === "class") node.className = value;
    else node.setAttribute(key, value === true ? "" : value);
  }
  node.append(...children.filter((c) => c !== undefined && c !== null));
  return node;
}
