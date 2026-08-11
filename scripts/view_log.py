#!/usr/bin/env python
"""
Decision Log Viewer Script.
Pretty-prints the last N agent decisions from logs/decisions.jsonl in a readable terminal table.
"""

import os
import sys
import json
import argparse

# Ensure UTF-8 stdout formatting
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def view_logs(n: int = 10):
    log_file = os.path.join(os.path.dirname(__file__), "..", "logs", "decisions.jsonl")
    if not os.path.exists(log_file):
        print(f"No decision log found at {log_file}. Run the crew first to generate decision logs.")
        return 0

    lines = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    lines.append(json.loads(line.strip()))
                except Exception:
                    pass

    if not lines:
        print("Decision log is empty.")
        return 0

    recent = lines[-n:]

    print(f"\n==========================================================================================")
    print(f"                       LAST {len(recent)} AGENT DECISION LOGS                            ")
    print(f"==========================================================================================")
    print(f"{'Time':<12} {'Sender':<22} {'Subject':<28} {'Category':<16} {'Prio':<6} {'Action'}")
    print("-" * 105)

    for record in recent:
        ts = record.get("timestamp", "").split("T")[-1][:8] if "T" in record.get("timestamp", "") else record.get("timestamp", "")[:8]
        sender = (record.get("sender", "")[:20] + "..") if len(record.get("sender", "")) > 20 else record.get("sender", "")
        subject = (record.get("subject", "")[:26] + "..") if len(record.get("subject", "")) > 26 else record.get("subject", "")
        category = record.get("category", "")
        priority = record.get("priority", "")
        action = record.get("action", "")
        override = f" ({record.get('override_note')})" if record.get("override_note") else ""

        print(f"{ts:<12} {sender:<22} {subject:<28} {category:<16} {priority:<6} {action}{override}")

    print("-" * 105)
    print(f"Total decision records on file: {len(lines)}\n")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="View recent decision logs.")
    parser.add_argument("-n", "--number", type=int, default=10, help="Number of recent decisions to view (default: 10)")
    args = parser.parse_args()
    sys.exit(view_logs(args.number))
