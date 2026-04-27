# orchestrator

Ties all parts together into a feedback loop: run → evaluate → analyze → improve → re-run.

- `pipeline.py` — main loop; controls retry count, wires runner/analyzer/improver together, halts on no-progress
- `reporter.py` — summarizes outcomes across tasks and improvement cycles
