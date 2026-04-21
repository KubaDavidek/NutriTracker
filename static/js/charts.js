/**
 * charts.js – Chart.js helper funkce pro NutriTracker.
 *
 * Funkce jsou volány z Jinja šablon (dashboard.html, history.html).
 * Veškerá data přijímají jako JS objekty předané z Flask přes window.*.
 */

"use strict";

// ── Barvy (modrá paleta) ──────────────────────────────────────────────────────
const COLORS = {
  blue:    "rgba(13,  110, 253, 0.85)",
  blueS:   "rgba(13,  110, 253, 1)",
  cyan:    "rgba(13,  202, 240, 0.85)",
  cyanS:   "rgba(13,  202, 240, 1)",
  violet:  "rgba(124,  92, 252, 0.85)",
  violetS: "rgba(124,  92, 252, 1)",
  yellow:  "rgba(255, 193,   7, 0.85)",
  yellowS: "rgba(255, 193,   7, 1)",
  red:     "rgba(220,  53,  69, 0.85)",
  redS:    "rgba(220,  53,  69, 1)",
};

// ── Barvy závislé na tématu ───────────────────────────────────────────────────
function _isLight() {
  return document.documentElement.classList.contains('light-mode');
}
function _tickColor()  { return _isLight() ? '#4a5568'              : 'rgba(180,200,230,0.75)'; }
function _gridColor()  { return _isLight() ? 'rgba(0,0,0,0.18)'    : 'rgba(255,255,255,0.15)'; }
function _labelColor() { return _isLight() ? '#3a4455'              : 'rgba(180,200,230,0.80)'; }

// Úložiště instancí pro přebarvení při přepnutí tématu
const _ntCharts = [];

// Voláno z ntToggleTheme() v base.html
function ntUpdateChartTheme() {
  Chart.defaults.color       = _labelColor();
  Chart.defaults.borderColor = _gridColor();
  _ntCharts.forEach(function(chart) {
    Object.values(chart.options.scales || {}).forEach(function(scale) {
      if (scale.ticks) scale.ticks.color = _tickColor();
      if (scale.grid)  scale.grid.color  = _gridColor();
    });
    var leg = chart.options.plugins && chart.options.plugins.legend;
    if (leg) { leg.labels = leg.labels || {}; leg.labels.color = _tickColor(); }
    chart.update();
  });
}

// Nastavit výchozí barvy hned při načtení skriptu
Chart.defaults.color       = _labelColor();
Chart.defaults.borderColor = _gridColor();

// ── 2) Bilance Bar (dashboard) ────────────────────────────────────────────────
/**
 * @param {object} totals – { kcal, calories_burned, balance }
 */
function initBalanceChart(totals) {
  const ctx = document.getElementById("balanceChart");
  if (!ctx) return;

  const { kcal = 0, calories_burned = 0 } = totals;

  const balanceChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Příjem", "Výdej"],
      datasets: [{
        data:            [kcal, calories_burned],
        backgroundColor: [COLORS.blue, COLORS.cyan],
        borderColor:     [COLORS.blueS, COLORS.cyanS],
        borderWidth: 0,
        borderRadius: 6,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: { label: ctx => ` ${ctx.raw} kcal` },
        },
      },
      scales: {
        x: { grid: { color: _gridColor() }, ticks: { color: _tickColor() } },
        y: {
          beginAtZero: true,
          grid: { color: _gridColor() },
          ticks: { color: _tickColor(), callback: v => `${v}` },
        },
      },
    },
  });
  _ntCharts.push(balanceChart);
}

// ── 3) Historie Line/Bar (dashboard – 7 dní) ──────────────────────────────────
/**
 * Načte data z /api/history a vykreslí sloupcový graf.
 * @param {string} canvasId – id elementu <canvas>
 */
async function loadHistoryChart(canvasId) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  let data;
  try {
    const res = await fetch("/api/history?days=7");
    if (!res.ok) throw new Error("HTTP " + res.status);
    data = await res.json();
  } catch (e) {
    console.warn("loadHistoryChart: nelze načíst data", e);
    return;
  }

  const labels  = data.map(d => d.date.slice(5));   // MM-DD
  const intakes = data.map(d => d.totals.kcal);
  const burned  = data.map(d => d.totals.calories_burned);

  const histDashChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label:           "Příjem (kcal)",
          data:            intakes,
          backgroundColor: COLORS.blue,
          borderColor:     COLORS.blueS,
          borderWidth: 0,
          borderRadius: 4,
        },
        {
          label:           "Výdej (kcal)",
          data:            burned,
          backgroundColor: COLORS.cyan,
          borderColor:     COLORS.cyanS,
          borderWidth: 1,
          borderRadius: 3,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { position: "bottom", labels: { color: _tickColor() } } },
      scales: {
        x: { grid: { color: _gridColor() }, ticks: { color: _tickColor() } },
        y: {
          beginAtZero: true,
          grid: { color: _gridColor() },
          ticks: { color: _tickColor(), callback: v => `${v}` },
        },
      },
    },
  });
  _ntCharts.push(histDashChart);
}
