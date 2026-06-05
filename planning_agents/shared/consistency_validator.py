"""Stack consistency validation and enforcement for planner outputs."""

from __future__ import annotations

from copy import deepcopy
import logging
from typing import Any, Dict, Iterable, List, Tuple

from .stack_rules import RuleManager


logger = logging.getLogger(__name__)


class ConsistencyValidator:
    """Inspect, validate, and enforce stack consistency on backend plans."""

    def __init__(self, validation_output: Dict[str, Any] | None = None):
        self.rules = RuleManager.from_validation_output(validation_output)

    def inspect_backend_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("CONSISTENCY VALIDATOR STARTED (inspect)")
        violations = self._collect_violations(plan)
        logger.info("CONFLICTS FOUND: %d", len(violations))
        return self._build_report(violations, corrections=[])

    def enforce_backend_plan(self, plan: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        logger.info("CONSISTENCY VALIDATOR STARTED (enforce)")
        sanitized_plan, corrections = self.rules.sanitize_backend_plan(deepcopy(plan or {}))
        violations = self._collect_violations(sanitized_plan)
        report = self._build_report(violations, corrections=corrections)

        logger.info("REPLACEMENTS APPLIED: %d", len(corrections))
        logger.info("FINAL CONSISTENCY SCORE: %d", report["consistency_score"])
        if violations:
            logger.warning("CONFLICTS FOUND: %d", len(violations))

        if not report["is_valid"]:
            return sanitized_plan, report

        sanitized_plan["consistency_score"] = report["consistency_score"]
        sanitized_plan["conflicts_found"] = []
        return sanitized_plan, report

    def validate_backend_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Convenience alias for direct inspection."""
        return self.inspect_backend_plan(plan)

    def _collect_violations(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = list(self.rules.validate_backend_plan(plan))
        violations.extend(self._scan_text_fields(plan))
        return self._dedupe_violations(violations)

    def _scan_text_fields(self, value: Any, path: str = "") -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []

        if path in {"framework", "language"}:
            return violations

        if isinstance(value, dict):
            for key, item in value.items():
                child_path = f"{path}.{key}" if path else str(key)
                violations.extend(self._scan_text_fields(item, child_path))
            return violations

        if isinstance(value, list):
            for index, item in enumerate(value):
                child_path = f"{path}[{index}]"
                violations.extend(self._scan_text_fields(item, child_path))
            return violations

        if not isinstance(value, str):
            return violations

        normalized = value.lower()
        for forbidden in self.rules.rules.get("disallowed", []):
            forbidden_key = str(forbidden).lower()
            if forbidden_key and forbidden_key in normalized:
                violations.append(
                    {
                        "field": path or "text",
                        "value": value,
                        "message": f"{forbidden} used in Spring ecosystem",
                    }
                )

        return violations

    @staticmethod
    def _dedupe_violations(violations: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        unique: List[Dict[str, Any]] = []
        for item in violations:
            marker = (
                str(item.get("field", "")),
                str(item.get("value", "")),
                str(item.get("message", "")),
            )
            if marker in seen:
                continue
            seen.add(marker)
            unique.append(item)
        return unique

    def _build_report(self, violations: List[Dict[str, Any]], corrections: List[str]) -> Dict[str, Any]:
        conflicts_found = [self._format_violation(item) for item in violations]
        score = 100 if not conflicts_found else max(0, 100 - (len(conflicts_found) * 20))
        return {
            "is_valid": not conflicts_found,
            "consistency_score": score,
            "conflicts_found": conflicts_found,
            "violations": violations,
            "corrections_made": corrections,
        }

    @staticmethod
    def _format_violation(item: Dict[str, Any]) -> str:
        field = item.get("field", "unknown field")
        value = item.get("value", "unknown technology")
        message = item.get("message")
        if message:
            return f"{field}: {message}"
        return f"{field}: {value}"
