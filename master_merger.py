"""Merge backend and frontend planning results into one final architecture payload.

No hardcoded JWT/auth integration assumptions.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def merge_backend_and_frontend(
    backend_result: Dict[str, Any],
    frontend_result: Dict[str, Any],
    validation_output: Dict[str, Any],
) -> Dict[str, Any]:
    backend_ok = _is_success(backend_result)
    frontend_ok = _is_success(frontend_result)

    if not backend_ok or not frontend_ok:
        failed_parts = []
        if not backend_ok:
            failed_parts.append(f"backend: {backend_result.get('error', backend_result.get('reasoning', 'unknown error'))}")
        if not frontend_ok:
            failed_parts.append(f"frontend: {frontend_result.get('error', frontend_result.get('reasoning', 'unknown error'))}")
        return {
            "status": "error",
            "reasoning": "; ".join(failed_parts) if failed_parts else "One or more planning pipelines failed",
            "validation": _build_validation_block(validation_output),
            "partial_results": {
                "backend": backend_result if backend_ok else None,
                "frontend": frontend_result if frontend_ok else None,
            },
        }

    backend_architecture = {
        "framework": backend_result.get("framework", "Unknown"),
        "language": backend_result.get("language", "Unknown"),
        "api_style": backend_result.get("api_style", "REST"),
        "authentication": backend_result.get("authentication", {}),
        "database": backend_result.get("database", {}),
        "suggested_endpoints": backend_result.get("suggested_endpoints", []),
        "folder_structure": backend_result.get("folder_structure", []),
        "dependencies": {
            "core_libraries": backend_result.get("core_libraries", []),
            "optional_libraries": backend_result.get("optional_libraries", {}),
            "design_patterns": backend_result.get("design_patterns", []),
        },
        "reasoning": backend_result.get("reasoning", ""),
    }

    frontend_architecture = {
        "framework": frontend_result.get("frontend_architecture", {}).get("framework", "React"),
        "language": frontend_result.get("frontend_architecture", {}).get("language", "TypeScript"),
        "styling": frontend_result.get("frontend_architecture", {}).get("styling", "tailwind"),
        "layout": frontend_result.get("layout", []),
        "components": frontend_result.get("components", []),
        "navigation": frontend_result.get("navigation", []),
        "mobile_menu": frontend_result.get("mobile_menu", "hamburger"),
        "total_routes": frontend_result.get("total_routes", 0),
        "animations": frontend_result.get("animations", []),
        "accessibility": frontend_result.get("accessibility", {}),
        "routing": frontend_result.get("routing", {}),
        "component_library": frontend_result.get("component_library", "shadcn/ui"),
        "reasoning": frontend_result.get("combined_reasoning", ""),
    }

    validation_block = _build_validation_block(validation_output)
    integration_points = _build_integration_points(backend_architecture, frontend_architecture)
    combined_reasoning = _combine_reasoning(backend_result, frontend_result, validation_block)
    recommendations = _build_recommendations(validation_block, backend_architecture, frontend_architecture)

    return {
        "status": "success",
        "validation": validation_block,
        "backend_architecture": backend_architecture,
        "frontend_architecture": frontend_architecture,
        "feedback": validation_block.get("feedback", ""),
        "recommendations": recommendations,
        "integration_points": integration_points,
        "combined_reasoning": combined_reasoning,
    }


def _is_success(result: Dict[str, Any]) -> bool:
    return isinstance(result, dict) and result.get("status") == "success"


def _build_validation_block(validation_output: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "project_type": validation_output.get("project_type", "unknown"),
        "complexity": validation_output.get("complexity", "intermediate"),
        "user_stack": validation_output.get("user_stack", {}),
        "missing_requirements": validation_output.get("missing_requirements", []),
        "alignment_score": validation_output.get("alignment_score"),
        "feedback": validation_output.get("feedback", ""),
        "reasoning": validation_output.get("reasoning", ""),
    }


def _build_recommendations(
    validation_block: Dict[str, Any],
    backend_architecture: Dict[str, Any],
    frontend_architecture: Dict[str, Any],
) -> list[str]:
    recommendations = []
    missing_requirements = validation_block.get("missing_requirements", []) or []
    recommendations.extend([f"Address validation gap: {item}" for item in missing_requirements])
    recommendations.append(
        f"Keep backend framework {backend_architecture.get('framework', 'Unknown')} aligned with frontend framework {frontend_architecture.get('framework', 'Unknown')}."
    )
    return recommendations


def _build_integration_points(
    backend_architecture: Dict[str, Any],
    frontend_architecture: Dict[str, Any],
) -> list[str]:
    points = [
        "Backend REST API endpoints match frontend API calls",
        "Shared validation stack informs both backend and frontend design decisions",
    ]

    if backend_architecture.get("api_style") == "REST":
        points.append("Frontend consumes REST resources with predictable request/response contracts")

    return points


def _combine_reasoning(
    backend_result: Dict[str, Any],
    frontend_result: Dict[str, Any],
    validation_block: Dict[str, Any],
) -> str:
    backend_reasoning = backend_result.get("reasoning", "").strip()
    frontend_reasoning = frontend_result.get("combined_reasoning", "").strip()
    project_type = validation_block.get("project_type", "unknown")

    parts = [
        f"Validated project type: {project_type}.",
        backend_reasoning,
        frontend_reasoning,
    ]
    return " ".join(part for part in parts if part)
