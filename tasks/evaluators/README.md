# tasks/evaluators

Judges whether a completed run passed or failed.

`base.py` defines the `BaseEvaluator` protocol and `EvaluationResult`. Concrete evaluators (e.g. DOM-based, LLM-based) implement that protocol and live here as separate files.
