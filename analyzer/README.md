# analyzer

Determines *why* a task failed — site UI problem, agent reasoning problem, or environment issue.

- `failure_classifier.py` — entry point: takes a failed task and returns a `FailureReport` with a failure type, confidence score, and evidence
- `signals/` — individual detectors, one per failure category, each returning raw evidence from the step trace
