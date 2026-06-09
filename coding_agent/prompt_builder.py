"""Prompt Builder — converts file blueprints into deterministic prompts.

No hardcoded auth routes, no hardcoded framework templates.
Prompts are driven entirely by blueprint specs and SRS lineage.
"""

from typing import Any, Dict, List
from coding_agent.prompt_constraints import build_prompt_constraints


def _serialize_spec(spec: dict) -> List[str]:
    """Convert a blueprint spec into exact code template instructions."""
    lines: List[str] = []

    if "api_calls" in spec:
        lines.append("This page calls these exact API endpoints — use no other URLs:")
        for call in spec["api_calls"]:
            body = call.get("body")
            if body:
                lines.append(f"- {call['method']} {call['endpoint']} — body: {', '.join(body)}")
            else:
                lines.append(f"- {call['method']} {call['endpoint']}")

    if "endpoints" in spec:
        lines.append("The file must implement these endpoints:")
        for ep in spec["endpoints"]:
            lines.append(f"- {ep['method']} {ep['path']} — {ep.get('description', '')}")

    if "mounts" in spec:
        lines.append("Route aggregation instructions:")
        for mount in spec["mounts"]:
            base = mount["router"].lstrip("./")
            lines.append(f"- Import {base}Router from {mount['router']}.")
            lines.append(f"  Mount with: router.use('{mount['path']}', {base}Router)")
        lines.append("- Export the router as module.exports = router")

    return lines


def build_file_prompt(
    file_blueprint: dict,
    project_rules: dict,
    all_blueprints: List[Dict] = None,
) -> str:
    file_path = file_blueprint.get("path", "unknown")
    file_purpose = file_blueprint.get("purpose", "")
    file_type = file_blueprint.get("type", "")
    spec = file_blueprint.get("spec")
    reason = file_blueprint.get("reason_for_existence", "")
    source_req = file_blueprint.get("source_requirement", "")
    source_page = file_blueprint.get("source_page", "")
    source_entity = file_blueprint.get("source_entity", "")

    backend_fw = project_rules.get("backend_framework", "")
    frontend_fw = project_rules.get("frontend_framework", "")
    database = project_rules.get("database", "")
    srs = project_rules.get("srs", {})

    lines = [
        "You are a code generation assistant. Generate the content for a single file.",
        "",
        "Project context:",
        f"- Project: {srs.get('project_name', 'Untitled')}",
        f"- Description: {srs.get('project_description', '')}",
        f"- Backend: {backend_fw}",
        f"- Frontend: {frontend_fw}",
        f"- Database: {database}",
        "",
        "File to generate:",
        f"- Path: {file_path}",
        f"- Purpose: {file_purpose}",
        f"- Requirement lineage — {reason}",
    ]

    if source_page:
        lines.append(f"- SRS page: {source_page}")
    if source_entity:
        lines.append(f"- SRS entity: {source_entity}")

    entity_names = []
    for e in (srs.get("entities", []) or []):
        entity_names.append(e.get("name", ""))
    page_names = []
    for p in (srs.get("pages", []) or []):
        page_names.append(p.get("name", ""))

    lines.extend([
        "",
        f"- SRS entities: {', '.join(filter(None, entity_names)) or 'none'}",
        f"- SRS pages: {', '.join(filter(None, page_names)) or 'none'}",
        "",
        "Rules:",
        "- Return raw source code only.",
        "- No markdown code blocks.",
        "- No explanations or comments.",
        "- Generate only this file.",
        "- Code must be complete and functional.",
    ])

    # Add import constraints based on build plan dependencies
    if all_blueprints:
        bp_by_path = {bp["path"]: bp for bp in all_blueprints}
        deps = file_blueprint.get("depends_on", [])
        if deps:
            lines.append("")
            lines.append("Dependency exports:")
            for dep_path in deps:
                dep_bp = bp_by_path.get(dep_path)
                if dep_bp:
                    provides = dep_bp.get("provides", [])
                    if provides:
                        lines.append(f"- {dep_path} exports: {', '.join(provides)}")
                    else:
                        lines.append(f"- {dep_path}: {dep_bp.get('purpose', '')}")
                else:
                    lines.append(f"- {dep_path}")

    lines.extend(build_prompt_constraints(project_rules, [file_blueprint]))

    if spec:
        lines.append("")
        lines.append("File contract — generate exactly this:")
        lines.extend(_serialize_spec(spec))

    return "\n".join(lines)
