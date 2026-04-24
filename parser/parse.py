# EchoBoard - Log Parser
# Turns raw log lines into structured data (dictionaries) we can analyze.

import re
from datetime import datetime


def parse_log_line(raw_line):
    """
    Parses a single log line into a dictionary.

    Expected format:
    2024-01-15 08:00:01 SRC=192.168.1.10 DST=8.8.8.8 PORT=443 PROTO=TCP BYTES=1200 ACTION=ALLOW
    """
    try:
        # Use regex to extract each field
        pattern = (
            r"(?P<date>\d{4}-\d{2}-\d{2})\s+"
            r"(?P<time>\d{2}:\d{2}:\d{2})\s+"
            r"SRC=(?P<src_ip>[\d.]+)\s+"
            r"DST=(?P<dst_ip>[\d.]+)\s+"
            r"PORT=(?P<port>\d+)\s+"
            r"PROTO=(?P<proto>\w+)\s+"
            r"BYTES=(?P<bytes>\d+)\s+"
            r"ACTION=(?P<action>\w+)"
        )

        match = re.match(pattern, raw_line)
        if not match:
            return None  # line didn't match expected format

        data = match.groupdict()

        # Convert types
        data["port"] = int(data["port"])
        data["bytes"] = int(data["bytes"])
        data["timestamp"] = datetime.strptime(
            f"{data['date']} {data['time']}", "%Y-%m-%d %H:%M:%S"
        )

        return data

    except Exception as e:
        print(f"[WARN] Could not parse line: {raw_line} | Error: {e}")
        return None


def parse_all(raw_logs):
    """
    Parses a list of raw log lines into structured records.
    Skips any lines that fail to parse.
    """
    parsed = []
    for line in raw_logs:
        result = parse_log_line(line)
        if result:
            parsed.append(result)

    print(f"[INFO] Successfully parsed {len(parsed)} / {len(raw_logs)} log entries")
    return parsed


# --- Run this file directly to test it ---
if __name__ == "__main__":
    import sys
    sys.path.append("..")
    from collector.collect import load_logs

    logs = load_logs("../sample_logs/network.log")
    parsed = parse_all(logs)

    print("\n--- First parsed entry ---")
    for key, val in parsed[0].items():
        print(f"  {key}: {val}")
