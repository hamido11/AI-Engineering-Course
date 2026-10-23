# Release Checklist — any change to the tuple (model / prompt / index / config)

- [ ] `run_eval.py` passes with no regressions vs baseline
- [ ] Cost per request within budget (check cost_ledger.csv delta)
- [ ] p95 latency within budget on eval traffic
- [ ] Canary at 10% for 24h: pass rate and cost within 5% of control
- [ ] Version tuple recorded in the release log
- [ ] Rollback command tested (previous tuple restorable in one step)

# Incident Runbook — "the bot said something wrong"

1. Get the trace_id from the report (every answer is stamped).
2. `python trace.py <trace_id>` — replay against the current build.
3. Reproduces? -> diagnose layer by layer: retrieval hits -> prompt -> model.
4. Doesn't reproduce? -> diff the build tuples; a silent model/index change is the usual suspect.
5. Either way: add the case to `dataset.jsonl` so Lab 12 catches it forever.
