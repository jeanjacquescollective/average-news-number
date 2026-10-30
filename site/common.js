// Shared helpers and translations for the index and history pages.

const STRINGS = {
  nl: {
    brand: "Gemiddeld Nieuwsgetal",
    switchTo: "EN",
    switchLabel: "Switch to English",
    loading: "Laden…",
    noData: "Nog geen gegevens.",
    labelToday: "Dagelijks gemiddeld nieuwsgetal",
    labelYesterday: () => "Dagelijks gemiddeld nieuwsgetal · gisteren",
    labelDay: (day) => `Dagelijks gemiddeld nieuwsgetal · ${day}`,
    standfirst: (numbers, count) => `Het gemiddelde van ${numbers} in ${count === 1 ? "1 kop" : `${formatNumber(count)} koppen`} op de voorpagina.`,
    archived: "archief",
    median: "mediaan",
    prevDay: "‹ vorige dag",
    nextDay: "volgende dag ›",
    otherDays: "Andere dagen",
    todaySoFar: "Vandaag: ",
    infoTitle: "Waar komt dit getal vandaan?",
    close: "Sluiten",
    lastUpdate: (when) => `Update ${when}`,
    numbers: (n) => (n === 1 ? "1 getal" : `${formatNumber(n)} getallen`),
    noNumbers: "geen getallen",
    sourceBefore: "Alle getallen uit de koppen op de voorpagina van ",
    sourceAfter: (partial, day) =>
      `, ${partial ? "vandaag" : `op ${day}`}. Elke kop telt één keer; een liveblog telt opnieuw als zijn kop verandert. ` +
      "Cijfers, getalwoorden (drie, honderd, twenty-one) en bedragen (“2 miljard”) tellen mee. ",
    headlinesTotals: (numbers, count) => `${numbers} in ${count === 1 ? "1 kop" : `${formatNumber(count)} koppen`}`,
    statsSentence: (mean, median) => `: gemiddelde ${mean}, mediaan ${median}.`,
    headlinesHeading: "Koppen",
    articlesHeading: "Artikels (totaal)",
    articlesExplained: (count, numbers, mean, median) =>
      `Kop en tekst van ${count === 1 ? "1 artikel" : `${formatNumber(count)} artikels`}: ${numbers}, gemiddelde ${mean}, mediaan ${median}. ` +
      "Telt niet mee voor het nieuwsgetal.",
    articlesNone: "Geen artikels.",
    loadingDay: "Laden…",
    loadError: "Kon deze dag niet laden.",
    historyTitle: "Geschiedenis",
    historyLede: (numbers, count, since) => `${numbers} in ${count === 1 ? "1 kop" : `${formatNumber(count)} koppen`} sinds ${since}.`,
    articlesLede: (numbers, count) =>
      `${numbers} in ${count === 1 ? "1 artikel" : `${formatNumber(count)} artikels`} (kop en tekst). Telt niet mee voor het nieuwsgetal.`,
    colArticles: "Artikels",
    anArticle: "een artikel",
    highestMean: "Hoogste gemiddelde",
    lowestMean: "Laagste gemiddelde",
    highestMedian: "Hoogste mediaan",
    lowestMedian: "Laagste mediaan",
    biggest: "Grootste getal",
    smallest: "Kleinste getal",
    inHeadline: "in",
    aHeadline: "een kop",
    recordsLater: "Records volgen na de eerste volledige dag.",
    colDay: "Dag",
    colHeadlines: "Koppen",
    colNumbers: "Getallen",
    colMean: "Gemiddelde",
    colMedian: "Mediaan",
    colSmallest: "Kleinste",
    colBiggest: "Grootste",
    soFar: " (tot nu toe)",
    navLabel: "Rubrieken",
    navNumber: "Het getal",
    navCharts: "Grafieken",
    navMoney: "Financial Time",
    navHistory: "Geschiedenis",
    theme: { auto: "◐ Auto", light: "☀ Licht", dark: "☾ Donker" },
    themeLabel: "Kleurmodus: automatisch, licht of donker",
    chartsTitle: "Grafieken",
    chartsLede: "Elk getal van de dag, en hoe het nieuwsgetal evolueert.",
    scatterTitle: "Elk getal in de koppen",
    scatterNote: "Op het moment dat de kop verscheen. Logaritmische schaal.",
    scatterHidden: (n) => ` ${n} getal(len) van 0 of minder niet getoond.`,
    magnitudeTitle: "Hoe groot zijn de getallen?",
    magnitudeNote: "Aandeel van de getallen per grootteorde.",
    benfordTitle: "Het eerste cijfer",
    benfordNote: "In de artikels, naast de wet van Benford: in echte cijfers begint bijna een derde met een 1.",
    trendTitle: "Gemiddelde en mediaan per dag",
    trendNote: "Koppen op de voorpagina. Logaritmische schaal.",
    countTitle: "Getallen per dag",
    countNote: "In de koppen op de voorpagina.",
    seriesHeadlines: "Koppen",
    seriesArticles: "Artikels",
    seriesBenford: "Wet van Benford",
    seriesMean: "Gemiddelde",
    seriesMedian: "Mediaan",
    seriesLost: "Verloren",
    seriesGained: "Gewonnen",
    seriesBalance: "Saldo",
    notEnough: "Nog te weinig gegevens.",
    moneyTitle: "Financial Time",
    moneyLede:
      "Elk bedrag in de artikels: negatief als het geld verloren ging (gestolen, verlies, boete, kost…), " +
      "positief als het binnenkwam (winst, budget, in beslag genomen, gekregen…). Zonder signaalwoord in de zin " +
      "beslist de kop, dan het artikel; anders telt het als positief. Andere munten zijn bij benadering omgerekend naar euro.",
    howTitle: (kw) => `via de kop: “${kw}”`,
    howArticle: (kw) => `via het artikel: “${kw}”`,
    howDefault: "geen signaalwoord: telt als positief",
    lost: "Verloren",
    gained: "Gewonnen",
    net: "Saldo",
    amounts: (n) => (n === 1 ? "1 bedrag" : `${formatNumber(n)} bedragen`),
    neutralSummary: (n, total) => `Zonder richting: ${n}, samen ${total}`,
    noMoney: "Geen bedragen gevonden.",
    moneyChartTitle: "Verloren en gewonnen per dag",
    moneyChartNote: "In euro; verloren onder de lijn.",
    balanceTitle: "Saldo sinds de start",
    balanceNote: "Gewonnen min verloren, dag na dag opgeteld.",
  },
  en: {
    brand: "Average News Number",
    switchTo: "NL",
    switchLabel: "Schakel naar Nederlands",
    loading: "Loading…",
    noData: "No data yet.",
    labelToday: "Daily average news number",
    labelYesterday: () => "Daily average news number · yesterday",
    labelDay: (day) => `Daily average news number · ${day}`,
    standfirst: (numbers, count) => `The mean of ${numbers} in ${count === 1 ? "1 headline" : `${formatNumber(count)} headlines`} on the front page.`,
    archived: "archive",
    median: "median",
    prevDay: "‹ previous day",
    nextDay: "next day ›",
    otherDays: "Other days",
    todaySoFar: "Today: ",
    infoTitle: "Where does this number come from?",
    close: "Close",
    lastUpdate: (when) => `Updated ${when}`,
    numbers: (n) => (n === 1 ? "1 number" : `${formatNumber(n)} numbers`),
    noNumbers: "no numbers",
    sourceBefore: "All numbers in the headlines on the front page of ",
    sourceAfter: (partial, day) =>
      `, ${partial ? "today" : `on ${day}`}. Each headline counts once; a liveblog counts again when its headline changes. ` +
      "Digits, number words (drie, honderd, twenty-one) and amounts (“2 miljard”) all count. ",
    headlinesTotals: (numbers, count) => `${numbers} in ${count === 1 ? "1 headline" : `${formatNumber(count)} headlines`}`,
    statsSentence: (mean, median) => `: mean ${mean}, median ${median}.`,
    headlinesHeading: "Headlines",
    articlesHeading: "Articles (total)",
    articlesExplained: (count, numbers, mean, median) =>
      `Headline and text of ${count === 1 ? "1 article" : `${formatNumber(count)} articles`}: ${numbers}, mean ${mean}, median ${median}. ` +
      "Not part of the news number.",
    articlesNone: "No articles.",
    loadingDay: "Loading…",
    loadError: "Could not load this day.",
    historyTitle: "History",
    historyLede: (numbers, count, since) => `${numbers} in ${count === 1 ? "1 headline" : `${formatNumber(count)} headlines`} since ${since}.`,
    articlesLede: (numbers, count) =>
      `${numbers} in ${count === 1 ? "1 article" : `${formatNumber(count)} articles`} (headline and text). Not part of the news number.`,
    colArticles: "Articles",
    anArticle: "an article",
    highestMean: "Highest mean",
    lowestMean: "Lowest mean",
    highestMedian: "Highest median",
    lowestMedian: "Lowest median",
    biggest: "Biggest number",
    smallest: "Smallest number",
    inHeadline: "in",
    aHeadline: "a headline",
    recordsLater: "Records follow after the first full day.",
    colDay: "Day",
    colHeadlines: "Headlines",
    colNumbers: "Numbers",
    colMean: "Mean",
    colMedian: "Median",
    colSmallest: "Smallest",
    colBiggest: "Biggest",
    soFar: " (so far)",
    navLabel: "Sections",
    navNumber: "The number",
    navCharts: "Charts",
    navMoney: "Financial Time",
    navHistory: "History",
    theme: { auto: "◐ Auto", light: "☀ Light", dark: "☾ Dark" },
    themeLabel: "Colour mode: automatic, light or dark",
    chartsTitle: "Charts",
    chartsLede: "Every number of the day, and how the news number evolves.",
    scatterTitle: "Every number in the headlines",
    scatterNote: "At the moment the headline appeared. Logarithmic scale.",
    scatterHidden: (n) => ` ${n} number(s) of 0 or less not shown.`,
    magnitudeTitle: "How big are the numbers?",
    magnitudeNote: "Share of the numbers per order of magnitude.",
    benfordTitle: "The first digit",
    benfordNote: "In the articles, next to Benford’s law: in real-world figures almost a third start with a 1.",
    trendTitle: "Mean and median per day",
    trendNote: "Front page headlines. Logarithmic scale.",
    countTitle: "Numbers per day",
    countNote: "In the front page headlines.",
    seriesHeadlines: "Headlines",
    seriesArticles: "Articles",
    seriesBenford: "Benford’s law",
    seriesMean: "Mean",
    seriesMedian: "Median",
    seriesLost: "Lost",
    seriesGained: "Gained",
    seriesBalance: "Balance",
    notEnough: "Not enough data yet.",
    moneyTitle: "Financial Time",
    moneyLede:
      "Every amount in the articles: negative when the money was lost (stolen, loss, fine, cost…), " +
      "positive when it came in (profit, budget, seized, received…). Without a signal word in the sentence, " +
      "the headline decides, then the article; otherwise it counts as positive. Other currencies are converted to euro approximately.",
    howTitle: (kw) => `from the headline: “${kw}”`,
    howArticle: (kw) => `from the article: “${kw}”`,
    howDefault: "no signal word: counts as positive",
    lost: "Lost",
    gained: "Gained",
    net: "Balance",
    amounts: (n) => (n === 1 ? "1 amount" : `${formatNumber(n)} amounts`),
    neutralSummary: (n, total) => `Without a direction: ${n}, together ${total}`,
    noMoney: "No amounts found.",
    moneyChartTitle: "Lost and gained per day",
    moneyChartNote: "In euro; lost below the line.",
    balanceTitle: "Balance since the start",
    balanceNote: "Gained minus lost, added up day by day.",
  },
};

let lang = "nl";
try {
  if (localStorage.getItem("lang") === "en") lang = "en";
} catch {}

function t(key, ...args) {
  const value = STRINGS[lang][key];
  return typeof value === "function" ? value(...args) : value;
}

function locale() {
  return lang === "nl" ? "nl-BE" : "en-GB";
}

function formatNumber(value) {
  return new Intl.NumberFormat(locale(), { maximumFractionDigits: 2 }).format(value);
}

// Today's date in Belgium as YYYY-MM-DD; days before it are complete.
function todayInBrussels() {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Brussels" }).format(new Date());
}

function formatDay(isoDate, options = { weekday: "long", day: "numeric", month: "long", year: "numeric" }) {
  const [y, m, d] = isoDate.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString(locale(), { ...options, timeZone: "UTC" });
}

function formatTime(isoDateTime) {
  return new Date(isoDateTime).toLocaleTimeString(locale(), {
    hour: "2-digit", minute: "2-digit", timeZone: "Europe/Brussels",
  });
}

async function loadJson(path) {
  const response = await fetch(path, { cache: "no-cache" });
  if (!response.ok) throw new Error(`${path}: ${response.status}`);
  return response.json();
}

let summaryPromise;
function loadSummary() {
  summaryPromise ??= loadJson("data/summary.json");
  return summaryPromise;
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

function formatEuro(value) {
  return new Intl.NumberFormat(locale(), {
    style: "currency", currency: "EUR", notation: "compact", maximumFractionDigits: 1,
  }).format(value);
}

// The big value of a record card; --chars lets the CSS shrink long numbers to fit.
function recordValue(text) {
  return el("p", { class: "value", style: `--chars: ${Math.max(text.length, 4)}` }, text);
}

// The numbers found in a headline or article, as text with real separators so
// they never run together (also when copied).
function numberList(numbers) {
  if (!numbers.length) return el("p", { class: "nums none" }, t("noNumbers"));
  const line = el("p", { class: "nums" });
  numbers.forEach((n, i) => {
    if (i) line.append(el("span", { class: "sep" }, " · "));
    line.append(el("span", { class: "num", title: formatNumber(n.v) }, n.t));
  });
  return line;
}

// --- page setup: masthead, colour mode, language --------------------------------

const PAGES = [
  ["index", "./", "navNumber"],
  ["charts", "charts.html", "navCharts"],
  ["money", "financial-time.html", "navMoney"],
  ["history", "history.html", "navHistory"],
];
const THEMES = ["auto", "light", "dark"];

let theme = "auto";
try {
  if (THEMES.includes(localStorage.getItem("theme"))) theme = localStorage.getItem("theme");
} catch {}

function remember(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch {}
}

function applyTheme() {
  if (theme === "auto") delete document.documentElement.dataset.theme;
  else document.documentElement.dataset.theme = theme;
}

function renderMasthead(redraw) {
  const themeButton = el("button", { class: "control", type: "button", "aria-label": t("themeLabel"), title: t("themeLabel") },
    t("theme")[theme]);
  themeButton.onclick = () => {
    theme = THEMES[(THEMES.indexOf(theme) + 1) % THEMES.length];
    remember("theme", theme);
    applyTheme();
    redraw();
  };
  const langButton = el("button", { class: "control", type: "button", "aria-label": t("switchLabel"), lang: lang === "nl" ? "en" : "nl" },
    t("switchTo"));
  langButton.onclick = () => {
    lang = lang === "nl" ? "en" : "nl";
    remember("lang", lang);
    redraw();
  };
  const current = document.body.dataset.page;
  document.getElementById("masthead").replaceChildren(
    el("div", { class: "masthead-top" },
      el("span", { class: "dateline" }, formatDay(todayInBrussels())),
      el("div", { class: "controls" }, themeButton, langButton)),
    el("a", { class: "nameplate", href: "./" }, t("brand")),
    el("nav", { class: "sections", "aria-label": t("navLabel") },
      ...PAGES.map(([page, href, key]) => el("a", { href, "aria-current": page === current ? "page" : null }, t(key)))),
  );
}

// Draws the masthead and every [data-i18n] text, then calls `render` for the
// page's own content. Runs again after a language or colour mode switch, and when
// the system switches between light and dark (charts read their colours from CSS).
function setupPage(render) {
  const redraw = () => {
    document.documentElement.lang = lang;
    for (const node of document.querySelectorAll("[data-i18n]")) node.textContent = t(node.dataset.i18n);
    for (const node of document.querySelectorAll("[data-i18n-label]")) {
      node.setAttribute("aria-label", t(node.dataset.i18nLabel));
      node.title = t(node.dataset.i18nLabel);
    }
    renderMasthead(redraw);
    render();
  };
  applyTheme();
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => theme === "auto" && render());
  redraw();
}
