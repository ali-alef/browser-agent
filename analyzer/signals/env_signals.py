from __future__ import annotations

from typing import Any


def detect(step_trace: list[dict[str, Any]]) -> list[str]:
    """
    Look for evidence of environment/infrastructure failures in the step trace.

    Examples to detect: network errors, authentication walls, third-party
    blocks, browser crashes, timeouts unrelated to the task itself.

    Returns a list of human-readable evidence strings.
    """
    evidence = []

    for i, step in enumerate(step_trace):
        error = str(step.get("error", "")).lower()
        status = str(step.get("status", "")).lower()
        content = str(step.get("content", "")).lower()

        # Network errors
        if any(
            keyword in error
            for keyword in ["network", "connection", "timeout", "econnrefused", "enotfound"]
        ):
            evidence.append(f"Step {i}: Network error - {step.get('error')}")

        # Authentication failures
        if any(
            keyword in error or keyword in content
            for keyword in ["auth", "login", "403", "401", "unauthorized", "forbidden"]
        ):
            evidence.append(f"Step {i}: Authentication/permission error")

        # Browser crashes or disconnects
        if any(
            keyword in error or keyword in content
            for keyword in ["crash", "disconnect", "browser", "closed", "crashed"]
        ):
            evidence.append(f"Step {i}: Browser crash or disconnect")

        # Third-party blocks (ads, cloudflare, etc)
        if any(
            keyword in content
            for keyword in ["cloudflare", "blocked", "bot", "challenge", "ddos", "403"]
        ):
            evidence.append(f"Step {i}: Third-party block detected (possibly Cloudflare/WAF)")

        # Rate limiting
        if any(
            keyword in error or keyword in content
            for keyword in ["429", "too many", "rate limit", "throttle"]
        ):
            evidence.append(f"Step {i}: Rate limit or throttling detected")

        # Page load failures
        if step.get("type") == "navigation" and status == "failed":
            evidence.append(f"Step {i}: Failed to navigate to URL - {step.get('error')}")

        # SSL/Certificate errors
        if any(
            keyword in error for keyword in ["ssl", "certificate", "tls", "peer"]
        ):
            evidence.append(f"Step {i}: SSL/Certificate error")

    return evidence
