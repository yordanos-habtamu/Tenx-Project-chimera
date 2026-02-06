Logs: persisting and visualizing

- Persist new performance entries:

  ```bash
  python scripts/persist_logs.py \
    --category High_diligence --rating excellent \
    --summary "Short summary" --feedback "Nice work" \
    --meta '{"prompt_clarity_score":5,"context_coverage_score":5}'
  ```

- Visualize counts per category:

  ```bash
  pip install matplotlib   # if needed
  python scripts/visualize_logs.py
  ```

- Files created:
  - `scripts/persist_logs.py` — append structured entries to `logs/mcp_trace.json`
  - `scripts/visualize_logs.py` — simple bar chart saved to `logs/performance_category_counts.png`
