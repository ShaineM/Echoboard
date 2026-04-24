// EchoBoard — Dashboard JavaScript
// Fetches data from the Flask API and renders charts + anomaly feed.

// ── Live Clock ──
function updateClock() {
  const el = document.getElementById("live-time");
  if (el) el.textContent = new Date().toISOString().replace("T", " ").slice(0, 19) + " UTC";
}
setInterval(updateClock, 1000);
updateClock();

// ── Chart defaults ──
Chart.defaults.color = "#4a6a7a";
Chart.defaults.borderColor = "#1a2a3a";
Chart.defaults.font.family = "'Share Tech Mono', monospace";

const ACCENT  = "#00d4ff";
const WARN    = "#ffb300";
const DANGER  = "#ff3d5a";
const MUTED   = "#1a3a4a";

// ── Fetch and render everything ──
async function loadDashboard() {
  try {
    const res = await fetch("/api/summary");
    const data = await res.json();

    // Stat cards
    document.getElementById("total-events").textContent  = data.total_events;
    document.getElementById("anomaly-count").textContent = data.anomaly_count;
    document.getElementById("blocked-count").textContent = data.blocked_count;
    document.getElementById("top-ip").textContent =
      data.top_source_ips.length ? data.top_source_ips[0][0] : "N/A";

    renderIpChart(data.top_source_ips);
    renderAnomalyChart(data.total_events, data.anomaly_count);
    renderAnomalyFeed(data.anomalies);

  } catch (err) {
    console.error("Failed to load summary:", err);
  }

  // Protocol chart needs all events
  try {
    const res2 = await fetch("/api/events");
    const events = await res2.json();
    renderProtoChart(events);
  } catch (err) {
    console.error("Failed to load events:", err);
  }
}

// ── Protocol pie chart ──
function renderProtoChart(events) {
  const counts = {};
  events.forEach(e => {
    counts[e.proto] = (counts[e.proto] || 0) + 1;
  });

  new Chart(document.getElementById("protoChart"), {
    type: "doughnut",
    data: {
      labels: Object.keys(counts),
      datasets: [{
        data: Object.values(counts),
        backgroundColor: [ACCENT, WARN, DANGER, "#7c3aed"],
        borderWidth: 0,
      }]
    },
    options: {
      plugins: { legend: { position: "bottom", labels: { padding: 16, font: { size: 11 } } } },
      cutout: "65%",
    }
  });
}

// ── Top IPs bar chart ──
function renderIpChart(topIps) {
  const labels = topIps.map(x => x[0]);
  const values = topIps.map(x => x[1]);

  new Chart(document.getElementById("ipChart"), {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Events",
        data: values,
        backgroundColor: ACCENT + "55",
        borderColor: ACCENT,
        borderWidth: 1,
        borderRadius: 4,
      }]
    },
    options: {
      indexAxis: "y",
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: "#1a2a3a" } },
        y: { grid: { display: false }, ticks: { font: { size: 10 } } }
      }
    }
  });
}

// ── Normal vs Anomalous donut ──
function renderAnomalyChart(total, anomalies) {
  const normal = total - anomalies;

  new Chart(document.getElementById("anomalyChart"), {
    type: "doughnut",
    data: {
      labels: ["Normal", "Anomalous"],
      datasets: [{
        data: [normal, anomalies],
        backgroundColor: [ACCENT + "55", DANGER + "99"],
        borderColor: [ACCENT, DANGER],
        borderWidth: 1,
      }]
    },
    options: {
      plugins: { legend: { position: "bottom", labels: { padding: 16, font: { size: 11 } } } },
      cutout: "65%",
    }
  });
}

// ── Anomaly Feed Table ──
function renderAnomalyFeed(anomalies) {
  const tbody = document.getElementById("anomaly-feed");
  const counter = document.getElementById("feed-count");

  counter.textContent = `${anomalies.length} events flagged`;

  if (anomalies.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" class="loading-row">No anomalies detected ✓</td></tr>`;
    return;
  }

  tbody.innerHTML = anomalies.map(a => {
    const scorePct = Math.min(100, Math.abs(a.anomaly_score) * 200).toFixed(0);
    const actionBadge = a.action === "BLOCK"
      ? `<span class="badge badge-block">BLOCK</span>`
      : `<span class="badge badge-allow">ALLOW</span>`;

    return `
      <tr>
        <td>${a.timestamp}</td>
        <td style="color:#00d4ff">${a.src_ip}</td>
        <td>${a.dst_ip}</td>
        <td>${a.port}</td>
        <td>${a.proto}</td>
        <td>${a.bytes.toLocaleString()}</td>
        <td>${actionBadge}</td>
        <td><span class="score-val">${a.anomaly_score}</span></td>
      </tr>
    `;
  }).join("");
}

// ── Boot ──
loadDashboard();
