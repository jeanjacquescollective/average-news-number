// Shared helpers and translations for the index and history pages.

const STRINGS = {
  nl: {
    brand: "Gemiddeld Nieuwsgetal",
    historyLink: "Geschiedenis →",
    backLink: "← Terug",
    switchTo: "EN",
    switchLabel: "Switch to English",
    loading: "Laden…",
    noData: "Nog geen gegevens.",
    labelToday: "Dagelijks gemiddeld nieuwsgetal",
    labelYesterday: () => "Dagelijks gemiddeld nieuwsgetal · gisteren",
    labelDay: (day) => `Dagelijks gemiddeld nieuwsgetal · ${day}`,
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
  },
  en: {
    brand: "Average News Number",
    historyLink: "History →",
    backLink: "← Back",
    switchTo: "NL",
    switchLabel: "Schakel naar Nederlands",
    loading: "Loading…",
    noData: "No data yet.",
    labelToday: "Daily average news number",
    labelYesterday: () => "Daily average news number · yesterday",
    labelDay: (day) => `Daily average news number · ${day}`,
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

// Fills every [data-i18n] element and wires up the language switch; `render`
// redraws the page's dynamic parts after a switch.
function setupLanguage(render) {
  const button = document.getElementById("lang");
  const apply = () => {
    document.documentElement.lang = lang;
    for (const node of document.querySelectorAll("[data-i18n]")) node.textContent = t(node.dataset.i18n);
    for (const node of document.querySelectorAll("[data-i18n-label]")) {
      node.setAttribute("aria-label", t(node.dataset.i18nLabel));
      node.title = t(node.dataset.i18nLabel);
    }
    button.textContent = t("switchTo");
    button.setAttribute("aria-label", t("switchLabel"));
  };
  button.onclick = () => {
    lang = lang === "nl" ? "en" : "nl";
    try {
      localStorage.setItem("lang", lang);
    } catch {}
    apply();
    render();
  };
  apply();
  render();
}
