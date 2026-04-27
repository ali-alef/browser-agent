# runner

Drives the browser agent and records everything that happens.

- `agent_driver.py` — executes a single task using `browser_use.Agent`, populates the task's step trace and final output
- `session.py` — `Run` dataclass (richer run record for use by the analyzer)
- `llm/` — the custom LLM backend (Copilot CLI wrapper + message serializer)
