# EchoBoard - Log Collector
# This module reads network/firewall log files and loads them for processing.

import os

def load_logs(filepath):
    """
    Reads a log file and returns a list of raw log lines.
    Each line in the file = one network event.
    """
    if not os.path.exists(filepath):
        print(f"[ERROR] Log file not found: {filepath}")
        return []

    logs = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if line:  # skip empty lines
                logs.append(line)

    print(f"[INFO] Loaded {len(logs)} log entries from {filepath}")
    return logs


# --- Run this file directly to test it ---
if __name__ == "__main__":
    sample_path = "../sample_logs/network.log"
    logs = load_logs(sample_path)

    print("\n--- First 3 log entries ---")
    for entry in logs[:3]:
        print(entry)
