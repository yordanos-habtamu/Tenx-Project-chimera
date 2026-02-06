#!/usr/bin/env python3
"""
Append a performance log entry into `logs/mcp_trace.json`.
Usage:
  python scripts/persist_logs.py \
    --category High_diligence --rating excellent \
    --summary "Short summary" --feedback "Optional feedback" --meta '{"prompt_clarity_score":5}'
"""
import argparse
import json
import os
from datetime import datetime

def get_log_path():
    root = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(root, 'logs', 'mcp_trace.json')

def load_logs(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return []

def save_logs(path, logs):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--category', required=True)
    p.add_argument('--rating', required=True)
    p.add_argument('--summary', required=True)
    p.add_argument('--feedback', default='')
    p.add_argument('--meta', default='{}', help='JSON string with extra numeric fields')
    args = p.parse_args()

    try:
        meta = json.loads(args.meta)
    except Exception:
        print('Warning: invalid --meta JSON, using empty object')
        meta = {}

    entry = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'performance_category': args.category,
        'performance_rating': args.rating,
        'performance_summary': args.summary,
        'performance_feedback': args.feedback,
        'meta': meta
    }

    path = get_log_path()
    logs = load_logs(path)
    logs.append(entry)
    save_logs(path, logs)
    print('Appended log to', path)

if __name__ == '__main__':
    main()
