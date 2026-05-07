# Browser Agent Test Framework

A framework for testing AI agents that perform browser automation tasks. This project automates the process of running agents on tasks, analyzing their performance, and iteratively improving them based on failure analysis.

## Purpose

The Browser Agent Test Framework enables:
- **Running AI agent tasks** - Execute automated browser tasks using the agent
- **Analyzing failures** - Identify why tasks fail by analyzing run logs
- **Improving automatically** - Generate improvements based on failure analysis:
  - Prompt refinement and optimization
  - Step-by-step guidance and hints
  - UI/UX improvement recommendations
- **Iterating** - Re-run improved tasks to verify fixes

## Project Workflow

```
Task Execution → Log Analysis → Failure Detection → Improvement → Re-run
```

1. **Task Execution**: Run a task with the AI agent using the browser automation SDK
2. **Log Analysis**: Analyze execution logs to determine success or failure
3. **Failure Detection**: Classify the type of failure and identify root causes
4. **Improvement Generation**: Use LLM to generate specific improvements
5. **Improvement Application**: Apply changes to prompts, hints, and guidance
6. **Re-run**: Test the improved task configuration

## Architecture

### Current Components

#### **Runner** (`runner/`)
Responsible for executing AI agent tasks:
- `agent_driver.py` - Orchestrates task execution with the agent, injects hints into prompts
- `models.py` - Data models for task execution and results
- `serializer.py` - Serializes/deserializes task data

#### **Analyzer** (`analyzer/`)
Analyzes execution logs and identifies failures:
- `failure_classifier.py` - Uses LLM to classify failures and suggest improvements
- `models.py` - Data models for analysis results

#### **Improver** (`improver/`)
Generates and applies improvements based on analysis:
- `improvement_engine.py` - Generates improvement plans using LLM
- `models.py` - Data models for improvement plans and recommendations
- Capabilities:
  - **Prompt Improvement**: Refines task prompts for clarity and specificity
  - **Hint Generation**: Creates step-by-step hints for the agent
  - **Step Guidance**: Provides detailed guidance for critical steps
  - **UI Recommendations**: Suggests UI/UX improvements

#### **Tasks** (`tasks/`)
Task registry and definitions:
- Task definitions with support for hints and guidance
- Registry for managing available tasks

#### **Storage** (`storage/`)
Stores logs, results, analysis, and improvement plans:
- Run records
- Analysis results
- Improvement plans
- Task versions

#### **ChatGPT API** (`chatgpt_api/`)
Integration with OpenAI APIs for agent intelligence
