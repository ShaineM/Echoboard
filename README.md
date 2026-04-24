# ◈ EchoBoard

> A lightweight, open-source network security SIEM dashboard with AI-powered anomaly detection.

EchoBoard ingests firewall and network traffic logs, runs an Isolation Forest machine learning model to detect unusual behavior, and displays everything on a clean real-time dashboard.

![EchoBoard Dashboard](docs/screenshot.png)

---

## Features

- **AI Anomaly Detection** — Uses scikit-learn's Isolation Forest to learn normal traffic patterns and flag outliers — no manual rules needed
- **Network Log Parsing** — Ingests standard firewall/network log formats
- **Live Dashboard** — Visual charts for protocol breakdown, top IPs, and normal vs anomalous traffic
- **Anomaly Feed** — Scrollable table of flagged events with anomaly scores
- **Lightweight** — Runs locally, no cloud dependency, no heavy stack required
- **Open Source** — MIT licensed, built for learning and contribution

---

## How It Works

```
Log File → Collector → Parser → Isolation Forest AI → Flask API → Dashboard
```

1. **Collector** reads your log file
2. **Parser** extracts structured fields (IP, port, bytes, protocol, etc.)
3. **Detector** trains an Isolation Forest model and scores each event
4. **Dashboard** serves a web UI with Chart.js visualizations

---

## Quickstart

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/echoboard.git
cd echoboard
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the dashboard
```bash
cd dashboard
python app.py
```

### 4. Open your browser
```
http://localhost:5000
```

The sample log file in `sample_logs/network.log` is loaded by default. Replace it with your own firewall logs!

---

## Project Structure

```
echoboard/
├── collector/       # Log file ingestion
│   └── collect.py
├── parser/          # Log line parsing & normalization
│   └── parse.py
├── detector/        # AI anomaly detection (Isolation Forest)
│   └── anomaly.py
├── dashboard/       # Flask web server + frontend
│   ├── app.py
│   ├── templates/
│   └── static/
├── sample_logs/     # Example network log data
├── docs/            # Screenshots and documentation
├── requirements.txt
└── README.md
```

---

## Customizing the AI

In `detector/anomaly.py`, you can tune the model:

```python
model = IsolationForest(
    contamination=0.1,  # Increase to flag more events, decrease for fewer
    n_estimators=100,   # More trees = more accurate but slower
)
```

---

## Adding Your Own Logs

EchoBoard expects logs in this format:
```
YYYY-MM-DD HH:MM:SS SRC=x.x.x.x DST=x.x.x.x PORT=N PROTO=TCP BYTES=N ACTION=ALLOW
```

You can modify `parser/parse.py` to support other log formats (Palo Alto, pfSense, iptables, etc.).

---

## Roadmap

- [ ] Real-time log tailing (live updates without page refresh)
- [ ] Support for multiple log formats (iptables, Palo Alto, Cisco ASA)
- [ ] GeoIP mapping of source IPs
- [ ] Alert export to CSV / JSON
- [ ] Email/webhook notifications on anomaly detection

---

## Contributing

Pull requests are welcome! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

---

## Disclaimer

EchoBoard is intended for **educational purposes and authorized network monitoring only**. Do not use on networks you do not own or have explicit permission to monitor.

---

## License

MIT — see [LICENSE](LICENSE)
