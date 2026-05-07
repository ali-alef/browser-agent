# Browser Agent Test Framework

A framework for testing AI agents that perform browser automation tasks. This project automates the process of running agents on tasks, analyzing their performance, and iteratively improving them based on failure analysis.

## Purpose

The Browser Agent Test Framework enables:
- **Running AI agent tasks** - Execute automated browser tasks using the agent
- **Analyzing failures** - Identify why tasks fail by analyzing run logs
- **Iterative improvement** - Progressively improve agent performance through:
  - Prompt refinement and optimization
  - Adding step-by-step guidance and hints
  - UI/UX improvements for better task clarity
  - Re-running tasks with improvements

## Project Workflow

```
Task Execution → Log Analysis → Failure Detection → Improvement → Re-run
```

1. **Task Execution**: Run a task with the AI agent using the browser automation SDK
2. **Log Analysis**: Analyze execution logs to determine success or failure
3. **Failure Detection**: Classify the type of failure (if any)
4. **Improvement**: Apply fixes based on failure analysis
5. **Re-run**: Test the improved task configuration

## Architecture

### Current Components

#### **Runner** (`runner/`)
Responsible for executing AI agent tasks:
- `agent_driver.py` - Orchestrates task execution with the agent
- `models.py` - Data models for task execution and results
- `serializer.py` - Serializes/deserializes task data

#### **Analyzer** (`analyzer/`)
Analyzes execution logs and identifies failures:
- `failure_classifier.py` - Classifies and analyzes task failures
- `models.py` - Data models for analysis results

#### **Tasks** (`tasks/`)
Task registry and definitions:
- Task definitions for testing the agent
- Registry for managing available tasks

#### **Storage** (`storage/`)
Stores logs, results, and task run records

#### **ChatGPT API** (`chatgpt_api/`)
Integration with OpenAI APIs for agent intelligence

### Missing Component

#### **Improver** (TODO)
The next component to implement:
- Automatic prompt optimization
- Step-by-step hint generation
- UI/UX improvement recommendations
- Orchestrating task re-runs with improvements
