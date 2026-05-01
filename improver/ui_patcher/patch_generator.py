from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from analyzer.failure_classifier import FailureReport
from tasks.models import TaskRecord


@dataclass
class UIPatch:
    component: str       # CSS selector or component name that was patched
    change_description: str
    diff: str            # unified diff or before/after snippet


def generate(report: FailureReport) -> UIPatch | None:
    """
    Given a site_ui FailureReport, propose a concrete UI patch.

    Should identify the problematic selector/component from report.suggested_fix_area
    and return a patch that makes the element more agent-accessible.
    """
    if report.failure_type != "site_ui":
        return None

    # Extract selector from evidence
    selector = None
    for evidence in report.evidence:
        if "Element not found" in evidence or "selector" in evidence.lower():
            # Try to extract selector from error message
            parts = evidence.split("'")
            if len(parts) >= 2:
                selector = parts[1]
                break

    if not selector:
        return None

    # Generate patch to improve element accessibility
    # Replace non-alphanumeric chars with underscore for data attribute
    safe_selector = ''.join(c if c.isalnum() else '_' for c in selector)
    
    patch_js = f"""
// Patch for selector: {selector}
(function() {{
    var elem = document.querySelector('{selector}');
    if (elem) {{
        // Ensure element is visible and accessible
        elem.style.visibility = 'visible';
        elem.style.opacity = '1';
        elem.style.display = 'block';
        elem.scrollIntoView({{behavior: 'smooth', block: 'center'}});
        
        // Add data-testid for better detection
        elem.setAttribute('data-qa-{safe_selector}', 'true');
    }}
}})();
"""

    return UIPatch(
        component=selector,
        change_description=f"Make {selector} visible and accessible to the agent",
        diff=patch_js,
    )


def apply(patch: UIPatch, task: TaskRecord) -> None:
    """Apply the patch to the target site (local build, staging, etc.)."""

    # For now, we'll store the patch and suggest it in the task
    # In a real environment, this would inject the JavaScript into the browser session

    task.improvement_history.append({
        "type": "ui_patch",
        "component": patch.component,
        "description": patch.change_description,
        "patch": patch.diff,
    })

    # Save patch to storage for reference
    storage_path = Path(__file__).parent.parent.parent / "storage" / "patches"
    storage_path.mkdir(parents=True, exist_ok=True)

    patch_file = storage_path / f"task_{task.id}_patch.json"
    patch_file.write_text(
        json.dumps({
            "task_id": task.id,
            "component": patch.component,
            "description": patch.change_description,
            "patch": patch.diff,
        }, indent=2)
    )
