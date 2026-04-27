# tasks

Defines what the agent should do and judges whether it succeeded.

- `models.py` — `TaskRecord` data model (prompt, status, step trace, etc.)
- `registry.py` — load and save tasks from disk
- `definitions/` — task JSON files (the actual task prompts and metadata)
- `evaluators/` — logic to decide pass/fail after a run completes
