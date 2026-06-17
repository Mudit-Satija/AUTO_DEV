"""Prompt Builder — converts file blueprints into deterministic prompts.

No hardcoded auth routes, no hardcoded framework templates.
Prompts are driven entirely by blueprint specs and SRS lineage.
"""

from typing import Any, Dict, List

from coding_agent.naming import entity_prop_name, entity_setter_name
from coding_agent.prompt_constraints import build_prompt_constraints


def _serialize_spec(spec: dict) -> List[str]:
    """Convert a blueprint spec into exact code template instructions."""
    lines: List[str] = []

    if "frontend_props" in spec:
        fp = spec["frontend_props"]
        lines.append("")
        lines.append(f"CRITICAL — COPY THIS EXACT FUNCTION SIGNATURE — do not change any prop name:")
        lines.append(f"  {fp['signature']}")
        lines.append("  If your component destructure differs, App.jsx will pass 'undefined' and the app will crash.")
        lines.append("")

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

    # Model files — must import mongoose from npm package, not from config
    if "/models/" in file_path and file_path.endswith(".js"):
        lines.append("")
        lines.append("- Import mongoose with: const mongoose = require('mongoose')")
        lines.append("- Do NOT import from config/database")

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

    # Page-specific code quality rules
    if file_type == "page":
        lines.append("")
        lines.append("CRITICAL PAGE CONSTRAINTS — violating these causes the app to crash:")
        lines.append("- This file is at frontend/src/pages/<name>.jsx. Any relative import path starts from frontend/src/pages/, NOT from frontend/src/.")
        lines.append("- CRITICAL: NEVER import any CSS file (no imports ending in .css, e.g. do NOT import './App.css' or './styles.css' or 'styles.css'). Global styles are automatically loaded.")
        lines.append("- CRITICAL: If this page receives entity data as props (e.g. 'books', 'readingEntries'), you MUST use those props directly for ALL rendering. Do NOT create independent useState copies of data that already exists in props. Compute derived values (counts, filtered lists, aggregates) from props in the render body — do not duplicate state.")
        lines.append("- CRITICAL: DO NOT import helper components, forms, cards, lists, modals, or page files (like './BudgetForm' or './BudgetList' or './Budget') from this pages directory. ALL sub-components, helper UI, forms, and dialogs MUST be defined inline as local functions/components inside this single page file.")
        lines.append("- In import statements, do NOT append file extensions (.js, .jsx, .ts, .tsx) to local imports. Use './Component' not './Component.jsx'. Vite resolves extensions automatically.")
        lines.append("- Every variable you use must be declared with useState or const. Never reference a variable that is not declared in this component.")
        lines.append("- Every function you call (like handleAddEvent, handleDelete) must be defined in this component before it is used.")
        lines.append("- Every onChange handler must reference a useState setter that is declared at the top of the component.")
        lines.append("- Before writing JSX, write all useState declarations first, then all handler functions, then return the JSX.")
        lines.append("- Never use <a href> for internal navigation — it causes a full page reload, breaks the SPA, and is considered a bug. Always use Link from react-router-dom for internal navigation.")
        lines.append("- Never use React.Fragment, React.Suspense, or any React.X property in JSX. If you need a fragment, use <>...</> shorthand, or use <div>. Import React as a default import only if you use React.X syntax.")
        lines.append("- Do NOT read localStorage or sessionStorage directly in the component function body. Any side effect (reading/writing localStorage, API calls, timers) must be wrapped in a useEffect hook.")
        lines.append("- Check your code mentally before returning: every identifier used in JSX must be defined above it.")

    bundle_type = file_blueprint.get("bundle", "frontend")
    lines.extend(build_prompt_constraints(project_rules, [file_blueprint], bundle_type))

    # seedData.js specific constraints — must export single default object
    if "seedData.js" in file_path:
        lines.append("")
        lines.append("CRITICAL SEEDDATA CONSTRAINTS — violating this causes import errors in all pages:")
        lines.append("- This file must export a SINGLE default export with this shape:")
        lines.append("  export default {")
        lines.append("    <entity1_plural>: [ ...array of entity1 objects... ],")
        lines.append("    <entity2_plural>: [ ...array of entity2 objects... ]")
        lines.append("  };")
        lines.append("- Do NOT use named exports (export const seedX = ...).")
        lines.append("- Use exactly ONE 'export default { ... }' statement.")

    # Page files in frontend-only projects: concrete props + data flow
    is_frontend_only = backend_fw in ("", "none", "frontend only")
    if file_type == "page" and is_frontend_only:
        # Derive props from source_entity (e.g., "Recipe; Favorite" -> recipes, favorites)
        if source_entity:
            entity_names = [e.strip() for e in source_entity.split(";") if e.strip()]
            prop_names = [entity_prop_name(e) for e in entity_names]
            setter_names = [entity_setter_name(e) for e in entity_names]
            props_str = ", ".join(f"{p}, {s}" for p, s in zip(prop_names, setter_names))
            lines.append("")
            lines.append(f"CRITICAL — App.jsx passes you these EXACT props: {{ {props_str} }}")
            lines.append(f"Your function signature MUST be: function {source_page.replace(' ', '')}({{ {props_str} }})")
            lines.append(f"CRITICAL — The entity for this page is '{source_entity}'. The data prop '{prop_names[0] if prop_names else 'data'}' IS the entity data. The setter '{setter_names[0] if setter_names else 'setData'}' IS the state updater. Do NOT substitute a different entity name.")
            lines.append("CRITICAL — Do NOT rename props. App.jsx will pass 'undefined' for any invented name, causing runtime crashes.")
            lines.append("Do NOT use useState for entity data — use the props directly.")
            lines.append("CRITICAL — Do NOT call localStorage.getItem or localStorage.setItem in this file. App.jsx is the SINGLE source of truth for all persistence. Only call the setter prop (e.g. setBooks) to update data. App.jsx watches state changes and persists automatically.")
            lines.append("Do NOT add useEffect for reading/writing localStorage. App.jsx handles all persistence in its own useEffect.")
            lines.append("Use crypto.randomUUID() for new item IDs.")
            lines.append("If your JSX uses <Link>, <NavLink>, or <Navigate>, you MUST import it from 'react-router-dom'.")
            if ";" in source_entity:
                lines.append("")
                lines.append(f"MULTI-ENTITY PAGE: This page receives props for MULTIPLE entities ({source_entity.replace(';', ',')}). You MUST define handlers (add/edit/delete) for EVERY entity you interact with. For each entity data prop, create matching add/delete handler functions. Do NOT leave any entity without handlers if you reference them in JSX.")
            # Input type guidance for date, number, and select fields
            lines.append("")
            lines.append("### INPUT FIELD TYPES:")
            lines.append("- For date fields (field name containing 'date' or 'Date'): use <input type=\"date\" ... />")
            lines.append("- For numeric fields (pages, count, amount, price, year): use <input type=\"number\" ... />")
            lines.append("- For type/category/status/currency/format fields: use <select> with <option> values")
            lines.append("- For all other text fields: use <input type=\"text\" ... /> (or just <input ... />)")
        # Simple state variable naming rule
        if source_entity and ";" not in source_entity:
            lines.append("")
            lines.append("### VARIABLE NAMING RULE:")
            lines.append("- Name every form state variable after the EXACT entity field name from ENTITY OBJECT SHAPES above.")
            lines.append("  Example: field 'author' → const [author, setAuthor] = useState('')")
            lines.append("- Do NOT invent field names not listed in ENTITY OBJECT SHAPES.")

    if spec:
        lines.append("")
        lines.append("File contract — generate exactly this:")
        lines.extend(_serialize_spec(spec))

    return "\n".join(lines)

