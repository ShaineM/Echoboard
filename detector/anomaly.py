# EchoBoard - AI Anomaly Detector
# Uses Isolation Forest (a machine learning algorithm) to detect unusual network traffic.
# No prior ML experience needed — scikit-learn handles all the heavy lifting!

import numpy as np
from sklearn.ensemble import IsolationForest


def extract_features(parsed_logs):
    """
    Converts parsed log entries into numbers the AI model can understand.
    We pull out: bytes transferred, port number, and protocol (encoded as a number).
    """
    proto_map = {"TCP": 0, "UDP": 1, "ICMP": 2}  # convert protocol names to numbers

    features = []
    for log in parsed_logs:
        proto_num = proto_map.get(log["proto"], 3)  # unknown protocols get 3
        features.append([
            log["bytes"],    # how much data was transferred
            log["port"],     # which port was used
            proto_num,       # which protocol
        ])

    return np.array(features)


def detect_anomalies(parsed_logs, contamination=0.1):
    """
    Runs the Isolation Forest model to find anomalies.

    contamination=0.1 means we expect roughly 10% of traffic to be unusual.
    You can tune this — lower = fewer alerts, higher = more alerts.

    Returns the original logs with an 'anomaly' field added (True/False)
    and an 'anomaly_score' (lower = more suspicious).
    """
    if len(parsed_logs) < 5:
        print("[WARN] Not enough log entries to detect anomalies (need at least 5)")
        return parsed_logs

    features = extract_features(parsed_logs)

    # Train the model — Isolation Forest learns what "normal" looks like
    model = IsolationForest(
        n_estimators=100,       # number of trees in the forest
        contamination=contamination,
        random_state=42         # makes results repeatable
    )
    model.fit(features)

    # Predict: -1 = anomaly, 1 = normal
    predictions = model.predict(features)
    scores = model.score_samples(features)  # raw anomaly scores

    # Add results back to each log entry
    results = []
    for i, log in enumerate(parsed_logs):
        log_copy = log.copy()
        log_copy["anomaly"] = predictions[i] == -1  # True if anomalous
        log_copy["anomaly_score"] = round(float(scores[i]), 4)
        results.append(log_copy)

    anomaly_count = sum(1 for r in results if r["anomaly"])
    print(f"[INFO] Anomaly detection complete — {anomaly_count} anomalies found out of {len(results)} entries")

    return results


def get_summary(analyzed_logs):
    """
    Returns summary statistics for the dashboard.
    """
    total = len(analyzed_logs)
    anomalies = [l for l in analyzed_logs if l["anomaly"]]
    blocked = [l for l in analyzed_logs if l["action"] == "BLOCK"]

    # Top source IPs by event count
    from collections import Counter
    src_counts = Counter(l["src_ip"] for l in analyzed_logs)
    top_ips = src_counts.most_common(5)

    return {
        "total_events": total,
        "anomaly_count": len(anomalies),
        "blocked_count": len(blocked),
        "top_source_ips": top_ips,
        "anomalous_entries": anomalies,
    }


# --- Run this file directly to test it ---
if __name__ == "__main__":
    import sys
    sys.path.append("..")
    from collector.collect import load_logs
    from parser.parse import parse_all

    logs = load_logs("../sample_logs/network.log")
    parsed = parse_all(logs)
    analyzed = detect_anomalies(parsed)
    summary = get_summary(analyzed)

    print("\n--- Summary ---")
    print(f"Total Events : {summary['total_events']}")
    print(f"Anomalies    : {summary['anomaly_count']}")
    print(f"Blocked      : {summary['blocked_count']}")
    print(f"Top Source IPs: {summary['top_source_ips']}")

    print("\n--- Flagged Anomalies ---")
    for entry in summary["anomalous_entries"]:
        print(f"  {entry['timestamp']} | {entry['src_ip']} → {entry['dst_ip']}:{entry['port']} | {entry['bytes']} bytes | score: {entry['anomaly_score']}")
