# improver

Applies a targeted fix based on the `FailureReport` from the analyzer, then hands control back to the orchestrator to re-run.

- `router.py` — reads `failure_type` and dispatches to the right patcher
- `ui_patcher/` — fixes problems on the site side (component visibility, labels, selectors)
- `prompt_patcher/` — fixes problems on the agent side (clearer instructions, step-level hints)
