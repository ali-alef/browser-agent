from __future__ import annotations

from dataclasses import dataclass

from analyzer.failure_classifier import FailureReport


@dataclass
class UIPatch:
    component: str       # CSS selector or component name that was patched
    change_description: str
    diff: str            # unified diff or before/after snippet


def generate(report: FailureReport) -> UIPatch:
    """
    Given a site_ui FailureReport, propose a concrete UI patch.

    Should identify the problematic selector/component from report.suggested_fix_area
    and return a patch that makes the element more agent-accessible.
    """
    raise NotImplementedError


def apply(patch: UIPatch) -> None:
    """Apply the patch to the target site (local build, staging, etc.)."""
    raise NotImplementedError
