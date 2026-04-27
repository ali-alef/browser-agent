# analyzer/signals

One module per failure category. Each exports a `detect(step_trace)` function that scans the raw step trace and returns a list of evidence strings.

- `ui_signals.py` — hidden elements, bad selectors, layout shifts, CAPTCHAs
- `llm_signals.py` — action loops, hallucinated selectors, wrong reasoning
- `env_signals.py` — network errors, auth walls, timeouts, third-party blocks
