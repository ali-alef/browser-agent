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

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

Dependencies:
- `browser-use==0.12.6` - Browser automation framework
- `browser-use-sdk==2.0.15` - SDK for browser operations

## Usage

### Basic: Run and Analyze

```bash
python main.py <task_id>
```

Runs a task and outputs analysis results.

### With Improvements

```bash
python main.py <task_id> --improve
```

Runs task, analyzes results, and generates improvement plan (for failed tasks).

### With Automatic Re-run

```bash
python main.py <task_id> --improve --rerun
```

Runs task, analyzes, generates improvements, applies them, and re-runs the improved task.

## How Improvements Work

### 1. Hints Injection

Hints and step guidance are automatically injected into the agent's task prompt:

```python
# In task definition (task_X.json)
{
    "id": 1,
    "prompt": "Find and click the login button",
    "hints": [
        "The login button is usually in the top-right corner",
        "Look for 'Sign In' or 'Login' text"
    ],
    "step_guidance": {
        "1": "First, take a screenshot to see the current page",
        "2": "Look for authentication-related elements"
    }
}
```

The runner automatically enriches the prompt:

```
[Original prompt text]

[HELPFUL HINTS]
- The login button is usually in the top-right corner
- Look for 'Sign In' or 'Login' text

[STEP-BY-STEP GUIDANCE]
Step 1: First, take a screenshot to see the current page
Step 2: Look for authentication-related elements
```

### 2. Improvement Generation

When a task fails, the improver generates specific improvements:

- **Prompt Improvement**: Clarifies ambiguous language, adds context
- **Hints**: Provides step-by-step guidance for decision points
- **Step Guidance**: Explicit expected behavior for critical steps
- **UI Recommendations**: Suggestions to improve target website UI

### 3. Automatic Re-run

Once improvements are generated and applied, the task is re-run with the enhanced prompt and hints.

## Example Improvement Plan Output

```
============================================================
📋 IMPROVEMENT PLAN
============================================================

✏️  PROMPT IMPROVEMENT
Reason: Original prompt was ambiguous about location of elements

Original:
  Find the search box and search for "laptops"...

Improved:
  Find the search box at the top of the page and search for "laptops"...

Changes:
  • Added location specificity ("at the top of the page")
  • Clarified UI element appearance

💡 HINTS
New Hints:
  • Search box usually has placeholder text "Search"
  • Press Enter after typing to perform search

🎯 OVERALL STRATEGY
Focus on specificity and UI element identification to help the agent
navigate the page more effectively.

============================================================
```

## Task Model Structure

```python
class TaskRecord(pydantic.BaseModel):
    id: int
    prompt: str
    level: Literal["easy", "medium", "hard", "very_hard"]
    hints: list[str] = []  # Step-by-step hints
    step_guidance: dict[int, str] = {}  # Guidance per step
```

## Configuration

- `settings.py` - Project configuration (API keys, model, proxy settings)
- `requirements.in` - Base dependencies
- `requirements.txt` - Locked dependency versions

## Directory Structure

```
browser-agent/
├── README.md                 # This file
├── main.py                   # Entry point with improvement workflow
├── settings.py               # Configuration
├── requirements.in           # Base dependencies
├── analyzer/                 # Failure analysis module
│   ├── failure_classifier.py # Analyzes task runs
│   ├── models.py
│   └── __init__.py
├── runner/                   # Task execution module
│   ├── agent_driver.py       # Executes tasks and injects hints
│   ├── models.py
│   ├── serializer.py
│   └── __init__.py
├── improver/                 # Improvement generation module
│   ├── improvement_engine.py # Generates improvements
│   ├── models.py             # Improvement data models
│   └── __init__.py
├── tasks/                    # Task definitions
│   ├── models.py             # TaskRecord with hints support
│   ├── registry.py
│   └── definitions/          # JSON task files
├── chatgpt_api/              # OpenAI API integration
├── storage/                  # Storage for all records
│   ├── runs/                 # Task run records
│   ├── analys/               # Analysis results
│   ├── improvements/         # Improvement plans
│   └── registry.py           # Storage operations
└── .venv/                    # Virtual environment
```

## Development

### Adding New Tasks

1. Create `tasks/definitions/task_X.json`:
```json
{
    "id": 1,
    "prompt": "Your task description",
    "level": "easy",
    "hints": ["optional hints"],
    "step_guidance": {}
}
```

2. Run with `python main.py 1`

### Iterative Improvement Workflow

1. Run task: `python main.py 1`
2. If it fails, generate improvements: `python main.py 1 --improve`
3. Review improvement plan
4. Auto re-run with improvements: `python main.py 1 --improve --rerun`
5. Repeat until task passes

### Analyzing Improvement Impact

Check storage for:
- `storage/runs/` - Execution records
- `storage/analys/` - Analysis results
- `storage/improvements/` - Generated improvement plans

## License

[Add appropriate license]

## Contributing

[Add contribution guidelines]
