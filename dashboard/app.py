# EchoBoard - Dashboard Backend
# Flask web server that connects everything together and serves the dashboard.

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, jsonify
from collector.collect import load_logs
from parser.parse import parse_all
from detector.anomaly import detect_anomalies, get_summary
from collections import Counter

app = Flask(__name__)

# Path to your log file — change this if needed
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "sample_logs", "network.log")


def run_pipeline():
    """Runs the full EchoBoard pipeline and returns analyzed results."""
    raw = load_logs(LOG_FILE)
    parsed = parse_all(raw)
    analyzed = detect_anomalies(parsed)
    return analyzed


@app.route("/")
def index():
    """Serves the main dashboard page."""
    return render_template("index.html")


@app.route("/api/summary")
def api_summary():
    """Returns summary stats as JSON for the dashboard charts."""
    analyzed = run_pipeline()
    summary = get_summary(analyzed)

    # Format anomalies for JSON (convert datetime to string)
    anomalies_formatted = []
    for entry in summary["anomalous_entries"]:
        anomalies_formatted.append({
            "timestamp": entry["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
            "src_ip": entry["src_ip"],
            "dst_ip": entry["dst_ip"],
            "port": entry["port"],
            "proto": entry["proto"],
            "bytes": entry["bytes"],
            "action": entry["action"],
            "anomaly_score": entry["anomaly_score"],
        })

    return jsonify({
        "total_events": summary["total_events"],
        "anomaly_count": summary["anomaly_count"],
        "blocked_count": summary["blocked_count"],
        "top_source_ips": summary["top_source_ips"],
        "anomalies": anomalies_formatted,
    })


@app.route("/api/events")
def api_events():
    """Returns all events as JSON for the event feed."""
    analyzed = run_pipeline()

    events = []
    for entry in analyzed:
        events.append({
            "timestamp": entry["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
            "src_ip": entry["src_ip"],
            "dst_ip": entry["dst_ip"],
            "port": entry["port"],
            "proto": entry["proto"],
            "bytes": entry["bytes"],
            "action": entry["action"],
            "anomaly": entry["anomaly"],
            "anomaly_score": entry["anomaly_score"],
        })

    return jsonify(events)


if __name__ == "__main__":
    print("=" * 50)
    print("  EchoBoard SIEM Dashboard")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 50)
    app.run(debug=True, port=5000)
