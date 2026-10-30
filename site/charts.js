// Chart.js helpers shared by the charts and Financial Time pages. Colours come
// from the CSS variables, so charts follow the light/dark mode; pages redraw
// their charts whenever the mode changes.

function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function palette() {
  return {
    ink: cssVar("--ink"),
    ink2: cssVar("--ink-2"),
    grid: cssVar("--grid"),
    paper: cssVar("--paper-2"),
    series1: cssVar("--series-1"),
    series2: cssVar("--series-2"),
  };
}

function formatCompact(value) {
  return new Intl.NumberFormat(locale(), { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

// Ticks for a logarithmic axis: only the powers of ten, in compact notation.
const logTicks = {
  callback: (value) => (Number.isInteger(Math.log10(value)) ? formatCompact(value) : ""),
  autoSkip: true,
  maxTicksLimit: 10,
};

// (Re)draws a chart on a canvas with the newspaper look.
function drawChart(canvas, config) {
  Chart.getChart(canvas)?.destroy();
  const c = palette();
  Chart.defaults.font.family = "'Libre Caslon Text', Georgia, serif";
  Chart.defaults.font.size = 12;
  Chart.defaults.color = c.ink2;
  Chart.defaults.borderColor = c.grid;
  const options = config.options || {};
  const plugins = options.plugins || {};
  return new Chart(canvas, {
    ...config,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      interaction: { mode: "nearest", intersect: false },
      ...options,
      plugins: {
        ...plugins,
        legend: {
          position: "top",
          align: "start",
          ...plugins.legend,
          labels: { color: c.ink, usePointStyle: true, boxWidth: 8, boxHeight: 8, padding: 14, ...(plugins.legend || {}).labels },
        },
        tooltip: {
          backgroundColor: c.paper,
          titleColor: c.ink,
          bodyColor: c.ink,
          borderColor: c.ink,
          borderWidth: 1,
          cornerRadius: 0,
          padding: 10,
          boxPadding: 4,
          titleFont: { family: "'Playfair Display', Georgia, serif", weight: "700", size: 13 },
          ...plugins.tooltip,
        },
      },
    },
  });
}

// Hours since midnight in Belgium, e.g. 14.5 for 14:30.
function hourOfDay(isoDateTime) {
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Europe/Brussels", hour: "numeric", minute: "numeric", hourCycle: "h23",
  }).formatToParts(new Date(isoDateTime));
  const get = (type) => Number(parts.find((p) => p.type === type).value);
  return get("hour") + get("minute") / 60;
}
