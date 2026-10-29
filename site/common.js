// Shared helpers and translations for the index and history pages.

const STRINGS = {
  nl: {
    brand: "Gemiddeld Nieuwsgetal",
    historyLink: "Geschiedenis →",
    backLink: "← Terug naar het getal",
    switchTo: "EN",
    switchLabel: "Switch to English",
    loading: "Laden…",
    noData: "Nog geen gegevens. Kom terug na de eerste run.",
    footerSource: "Getallen uit de koppen en artikels van",
    labelToday: "Het gemiddelde getal in de koppen op de voorpagina van VRT NWS vandaag, tot nu toe",
    labelYesterday: (day) => `Het gemiddelde getal in de koppen op de voorpagina van VRT NWS gisteren, ${day}`,
    labelDay: (day) => `Het gemiddelde getal in de koppen op de voorpagina van VRT NWS op ${day}`,
    median: "mediaan",
    prevDay: "‹ vorige dag",
    nextDay: "volgende dag ›",
    otherDays: "Andere dagen",
    todaySoFar: "Vandaag tot nu toe: ",
    infoTitle: "Waar komt dit getal vandaan?",
    close: "Sluiten",
    lastUpdate: (when) => `Laatste update ${when}`,
    numbers: (n) => (n === 1 ? "1 getal" : `${formatNumber(n)} getallen`),
    noNumbers: "geen getallen",
    headlinesExplained: (partial, day) =>
      `Elke kop die ${partial ? "vandaag" : `op ${day}`} op de voorpagina van VRT NWS verscheen, telt één keer mee: ` +
      "op het moment dat hij voor het eerst opduikt. Liveblogs die dagenlang lopen, krijgen bij elke ontwikkeling " +
      "een nieuwe kop en tellen dan opnieuw mee. Elk getal in de kop telt: cijfers (12, 10.000, 3,5), " +
      "Nederlandse en Engelse getalwoorden (drie, tweeëntwintig, honderd, twenty-one) en bedragen zoals “2 miljard”. ",
    headlinesTotals: (numbers, count) => `${numbers} in ${formatNumber(count)} koppen`,
    statsSentence: (mean, median) => ` geven een gemiddelde (som ÷ aantal) van ${mean} en een mediaan (het middelste getal) van ${median}.`,
    headlinesHeading: "Koppen op de voorpagina",
    articlesHeading: "Volledige artikels",
    articlesExplained: (count, numbers, mean, median) =>
      `Ter vergelijking: de kop en volledige tekst van de ${formatNumber(count)} artikels die die dag verschenen, ` +
      `bevatten ${numbers}, met een gemiddelde van ${mean} en een mediaan van ${median}.`,
    articlesNone: "Voor deze dag zijn er geen artikels.",
    loadingDay: "Koppen en artikels laden…",
    loadError: "Kon de gegevens voor deze dag niet laden.",
    historyTitle: "Geschiedenis",
    historyLede: (numbers, count, since) => `${numbers} in ${formatNumber(count)} koppen op de voorpagina sinds ${since}.`,
    articlesLede: (numbers, count) =>
      `Het totaal: ${numbers} in de kop en volledige tekst van ${formatNumber(count)} artikels. Dit telt niet mee voor het getal op de voorpagina.`,
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
    recordsLater: "Records voor gemiddelde en mediaan verschijnen zodra de eerste volledige dag voorbij is.",
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
    backLink: "← Back to the number",
    switchTo: "NL",
    switchLabel: "Schakel naar Nederlands",
    loading: "Loading…",
    noData: "No data yet. Check back after the first run.",
    footerSource: "Numbers from the headlines and articles of",
    labelToday: "The average number in the headlines on the VRT NWS front page today, so far",
    labelYesterday: (day) => `The average number in the headlines on the VRT NWS front page yesterday, ${day}`,
    labelDay: (day) => `The average number in the headlines on the VRT NWS front page on ${day}`,
    median: "median",
    prevDay: "‹ previous day",
    nextDay: "next day ›",
    otherDays: "Other days",
    todaySoFar: "Today so far: ",
    infoTitle: "Where does this number come from?",
    close: "Close",
    lastUpdate: (when) => `Last update ${when}`,
    numbers: (n) => (n === 1 ? "1 number" : `${formatNumber(n)} numbers`),
    noNumbers: "no numbers",
    headlinesExplained: (partial, day) =>
      `Every headline that appeared on the VRT NWS front page ${partial ? "today" : `on ${day}`} counts once: ` +
      "the moment it first shows up. Liveblogs that run for days get a new headline with every development, " +
      "and each new headline counts again. Every number in a headline counts: digits (12, 10.000, 3,5), " +
      "Dutch and English number words (drie, tweeëntwintig, honderd, twenty-one) and amounts such as “2 miljard”. ",
    headlinesTotals: (numbers, count) => `${numbers} in ${formatNumber(count)} headlines`,
    statsSentence: (mean, median) => ` give a mean (sum ÷ count) of ${mean} and a median (the middle value) of ${median}.`,
    headlinesHeading: "Front page headlines",
    articlesHeading: "Full articles",
    articlesExplained: (count, numbers, mean, median) =>
      `For comparison: the headline and full text of the ${formatNumber(count)} articles published that day ` +
      `contain ${numbers}, with a mean of ${mean} and a median of ${median}.`,
    articlesNone: "There are no articles for this day.",
    loadingDay: "Loading headlines and articles…",
    loadError: "Could not load the data for this day.",
    historyTitle: "History",
    historyLede: (numbers, count, since) => `${numbers} in ${formatNumber(count)} front page headlines since ${since}.`,
    articlesLede: (numbers, count) =>
      `The total: ${numbers} in the headline and full text of ${formatNumber(count)} articles. This does not count towards the number on the front page.`,
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
    recordsLater: "Mean and median records appear once the first full day is done.",
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
