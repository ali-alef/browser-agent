# runner/llm

The LLM backend used by the agent.

- `copilot_model.py` — `ChatCopilotCLI`, a `browser_use` compatible model that calls the GitHub Copilot CLI subprocess
- `serializer.py` — converts `browser_use` message objects into the plain-text format the Copilot CLI expects
