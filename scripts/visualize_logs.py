#!/usr/bin/env python3
"""
Simple visualization for `logs/mcp_trace.json`.
Generates a bar chart of counts per `performance_category`.
"""
import json
import os
import sys
from collections import Counter

LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'mcp_trace.json')

def load_logs(path):
    if not os.path.exists(path):
        print('No log file at', path)
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def plot_counts(counter):
    try:
        import matplotlib.pyplot as plt
    except Exception:
        print('matplotlib required. Install with: pip install matplotlib')
        return

    labels = list(counter.keys())
    values = [counter[k] for k in labels]
    plt.figure(figsize=(8,4))
    plt.bar(labels, values, color='tab:blue')
    plt.ylabel('Count')
    plt.title('Log entries per performance_category')
    plt.tight_layout()
    out = os.path.join(os.path.dirname(LOG_PATH), 'performance_category_counts.png')
    plt.savefig(out)
    print('Saved chart to', out)


def main():
    logs = load_logs(LOG_PATH)
    cats = [entry.get('performance_category','(unknown)') for entry in logs]
    c = Counter(cats)
    print('Counts:', c)
    plot_counts(c)

if __name__ == '__main__':
    main()
