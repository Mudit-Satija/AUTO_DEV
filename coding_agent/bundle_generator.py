"""Bundle Generator — groups files by their bundle assignment from the build plan.

Uses build plan's `bundle` field as the source of truth for classification.
Generates multiple files per LLM call using delimiter format.
"""

import logging
import re
from typing import Any, Dict, List, Tuple

from llm_client import CODER_MODEL, get_llm_response
from coding_agent.file_generator import generate_file as generate_single_file
from coding_agent.file_writer import write_file
from coding_agent.file_registry import register_file
from coding_agent.prompt_constraints import build_prompt_constraints
from coding_agent.metrics import get_metrics_collector

logger = logging.getLogger(__name__)

BUNDLE_NAMES = ("backend", "frontend", "database", "docs")
DEFAULT_MAX_BUNDLE_SIZE = 1


def group_files_by_bundle(file_blueprints: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    """Classify file blueprints into named bundles using the build plan's bundle field."""
    bundles: Dict[str, List[Dict[str, str]]] = {name: [] for name in BUNDLE_NAMES}

    for bp in file_blueprints:
        bundle = bp.get("bundle", "backend")
        if bundle in bundles:
            bundles[bundle].append(bp)
        else:
            bundles["backend"].append(bp)

    return {k: v for k, v in bundles.items() if v}


def partition_blueprints(
    blueprints: List[Dict[str, str]],
    max_size: int = DEFAULT_MAX_BUNDLE_SIZE,
) -> List[List[Dict[str, str]]]:
    sorted_bps = sorted(blueprints, key=lambda bp: bp.get("path", ""))

    if len(sorted_bps) <= max_size:
        return [sorted_bps]

    return [sorted_bps[i:i + max_size] for i in range(0, len(sorted_bps), max_size)]


def group_and_partition_files(
    file_blueprints: List[Dict[str, str]],
    max_size: int = DEFAULT_MAX_BUNDLE_SIZE,
) -> Dict[str, List[Dict[str, str]]]:
    bundles = group_files_by_bundle(file_blueprints)
    result: Dict[str, List[Dict[str, str]]] = {}

    for name, bps in sorted(bundles.items()):
        chunks = partition_blueprints(bps, max_size)
        if len(chunks) == 1:
            result[name] = chunks[0]
        else:
            for i, chunk in enumerate(chunks):
                result[f"{name}_{i + 1}"] = chunk

    return result


def build_bundle_prompt(
    bundle_name: str,
    file_blueprints: List[Dict[str, str]],
    project_rules: dict,
) -> str:
    backend_fw = project_rules.get("backend_framework", "Unknown")
    frontend_fw = project_rules.get("frontend_framework", "Unknown")
    database = project_rules.get("database", "Unknown")
    srs = project_rules.get("srs", {})

    lines = [
        f"You are a code generation assistant. Generate the following {len(file_blueprints)} files for the {bundle_name} of a project.",
        "",
        "Project context:",
        f"- Project: {srs.get('project_name', 'Untitled')}",
        f"- Description: {srs.get('project_description', '')}",
        f"- Backend framework: {backend_fw}",
        f"- Frontend framework: {frontend_fw}",
        f"- Database: {database}",
        f"- SRS entities: {', '.join(e.get('name', '') for e in (srs.get('entities', []) or [])) or 'none'}",
        f"- SRS pages: {', '.join(p.get('name', '') for p in (srs.get('pages', []) or [])) or 'none'}",
        "",
        "Use this exact delimiter format for each file (no JSON, no markdown, no explanations):",
        "",
        "===FILE: <path>===",
        "<file content here>",
        "===END===",
        "",
        "Files to generate:",
    ]

    is_frontend_only = (project_rules.get("backend_framework") or "").lower() in ("", "none", "frontend only")
    for i, bp in enumerate(file_blueprints, 1):
        bp_path = bp.get("path", "")
        purpose = bp.get("purpose", "")
        if is_frontend_only and "/pages/" in bp_path:
            bp_entity = (bp.get("source_entity") or "").strip()
            if bp_entity:
                e_names = [e.strip() for e in bp_entity.split(";") if e.strip()]
                p_names = [e[0].lower() + e[1:] + "s" for e in e_names]
                s_names = ["set" + e + "s" for e in e_names]
                props_str = ", ".join(f"{p}, {s}" for p, s in zip(p_names, s_names))
                lines.append(f"{i}. Path: {bp_path} — Purpose: {purpose}")
                lines.append(f"   CRITICAL — Props passed by App.jsx: {{{props_str}}}. Function signature MUST be: function {bp.get('source_page', 'Page').replace(' ', '')}({{{props_str}}}).")
                lines.append(f"   CRITICAL — Do NOT add useEffect or localStorage/seed data in this file. App.jsx handles all persistence. You only call setter props on mutations.")
                lines.append(f"   CRITICAL — Form <input> values MUST come from local useState, NOT from props. Use <select> for type/category/status/currency fields.")
                lines.append(f"   CRITICAL — Use crypto.randomUUID() for every new item id. Never use array[0] without checking .length first.")
            else:
                lines.append(f"{i}. Path: {bp_path} — Purpose: {purpose}")
        else:
            lines.append(f"{i}. Path: {bp_path} — Purpose: {purpose}")

    lines.extend([
        "",
        "Instructions:",
        "- Write file content with real newlines and real quotes.",
        "- Do NOT escape anything.",
        "- Do NOT wrap in markdown code blocks.",
        "- Do NOT add text before the first ===FILE or after the last ===END.",
        "- Generate ALL listed files — do not skip any.",
        "- The code must be complete, functional, and follow best practices.",
        "- Return ONLY the delimiter-formatted content.",
        "- Each file may only import from other files that are EXPLICITLY listed in this prompt. Never import from unlisted paths.",
    ])

    # ── App.jsx/main.jsx mounting contract (high visibility, near top of prompt) ──
    _APP_PATHS = {"frontend/src/App.jsx", "frontend/src/App.tsx", "frontend/src/App.vue"}
    if any(bp.get("path") in _APP_PATHS for bp in file_blueprints):
        lines.extend([
            "",
            "### CRITICAL — App.jsx MOUNTING CONTRACT:",
            " - main.jsx (already exists, you do not generate it) does:",
            "     import App from './App';",
            "     createRoot(document.getElementById('root')).render(<App />);",
            " - Therefore App.jsx MUST end with: export default App;",
            " - App.jsx MUST NOT import ReactDOM",
            " - App.jsx MUST NOT call ReactDOM.render() or createRoot()",
            " - App.jsx is a regular component — it returns JSX, nothing else",
            " - This is React 18. main.jsx handles all mounting.",
        ])

    # ── PROJECT FILE INVENTORY (so LLM knows what exists and what doesn't) ──
    all_files = project_rules.get("all_files", file_blueprints)
    if len(all_files) > len(file_blueprints):
        lines.append("")
        lines.append("### PROJECT FILE INVENTORY — these are ALL files in this project:")
        for f in all_files:
            marker = " ← YOU ARE GENERATING THIS" if f.get("path") in {bp["path"] for bp in file_blueprints} else ""
            lines.append(f"  {f.get('path', 'unknown')}{marker}")
        lines.append("")
        lines.append("You may ONLY import from files in the list above, or from standard npm packages")
        lines.append("(react, react-dom, react-router-dom, etc.).")
        lines.append("Do NOT invent imports from local paths like '../services/', '../components/', '../utils/'.")
        lines.append("Well-known npm packages (react, react-dom, react-router-dom, uuid) are fine if genuinely needed.")
        lines.append("These directories/files do not exist in this project and will cause build errors.")

    bundle_type = "frontend" if "frontend" in bundle_name else "backend" if "backend" in bundle_name else "database" if "database" in bundle_name else "docs"
    lines.extend(build_prompt_constraints(project_rules, file_blueprints, bundle_type))

    has_backend = (project_rules.get("backend_framework") or "").lower() not in ("", "none", "frontend only")
    if "frontend" in bundle_name:
        lines.append("- Use Vite environment variables (import.meta.env.VITE_*), not process.env.REACT_APP_*.")
        if has_backend:
            lines.append("- The api.js service: const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL }); export default api;")
            lines.append("- All page files must import api with: import api from '../services/api'")
            lines.append("- Pages use api directly: api.get('/products'), api.post('/products', body), api.put('/products/:id', body), api.delete('/products/:id')")
            lines.append("- Do NOT create named export wrappers like 'productApi' or 'orderApi' in api.js. Pages call api.get() directly with the endpoint path.")

    return "\n".join(lines)


DELIMITER_PATTERN = re.compile(
    r"===FILE:\s*(.+?)===\s*\n(.*?)\n===END===",
    re.DOTALL,
)


def parse_bundle_response(raw_text: str) -> Dict[str, str]:
    files = {}
    for match in DELIMITER_PATTERN.finditer(raw_text):
        path = match.group(1).strip()
        content = match.group(2)
        files[path] = content
    return files


def validate_bundle(parsed: Dict[str, str], expected_blueprints: List[Dict[str, str]]) -> Tuple[bool, List[str]]:
    expected_paths = {bp.get("path") for bp in expected_blueprints}
    present = set(parsed.keys())
    missing = sorted(expected_paths - present)
    return len(missing) == 0, missing


def generate_bundle(
    bundle_name: str,
    file_blueprints: List[Dict[str, str]],
    project_rules: dict,
) -> Dict[str, str]:
    metrics = get_metrics_collector()

    prompt = build_bundle_prompt(bundle_name, file_blueprints, project_rules)

    bundle_type = "backend" if "backend" in bundle_name else "frontend" if "frontend" in bundle_name else "database" if "database" in bundle_name else "docs"

    metrics.start_bundle(bundle_name, bundle_type, file_blueprints, CODER_MODEL)
    metrics.record_prompt(prompt)

    logger.info(
        "Bundle [%s] prompt: %d chars, %d files",
        bundle_name,
        len(prompt),
        len(file_blueprints),
    )

    raw = get_llm_response(prompt, model=CODER_MODEL)
    parsed = parse_bundle_response(raw)

    logger.info(
        "Bundle [%s] response: %d chars, %d files parsed of %d expected",
        bundle_name,
        len(raw),
        len(parsed),
        len(file_blueprints),
    )

    is_valid, missing = validate_bundle(parsed, file_blueprints)
    metrics.end_bundle(is_valid, missing)

    return parsed


def generate_bundle_with_fallback(
    bundle_name: str,
    file_blueprints: List[Dict[str, str]],
    project_rules: dict,
    output_dir: str,
    registry: dict,
) -> List[dict]:
    written: List[dict] = []

    # Separate static and dynamic blueprints
    static_bps = [bp for bp in file_blueprints if bp.get("static_content") is not None]
    dynamic_bps = [bp for bp in file_blueprints if bp.get("static_content") is None]

    # Process static blueprints immediately
    for bp in static_bps:
        path = bp.get("path", "unknown")
        content = bp.get("static_content", "")
        metadata = write_file({"path": path, "content": content}, output_dir)
        register_file(registry, bp, metadata)
        written.append(metadata)
        logger.info("Static file written: %s (%d bytes)", path, metadata.get("size", 0))

    if not dynamic_bps:
        return written

    parsed = generate_bundle(bundle_name, dynamic_bps, project_rules)
    is_valid, missing = validate_bundle(parsed, dynamic_bps)

    if is_valid:
        logger.info("Bundle [%s] valid — all %d dynamic files present", bundle_name, len(dynamic_bps))
        for bp in dynamic_bps:
            path = bp.get("path", "unknown")
            content = parsed.get(path, "")
            metadata = write_file({"path": path, "content": content}, output_dir)
            register_file(registry, bp, metadata)
            written.append(metadata)
        return written

    logger.warning(
        "Bundle [%s] validation failed — missing %d dynamic files. Falling back to per-file generation.",
        bundle_name,
        len(missing),
    )
    for bp in dynamic_bps:
        path = bp.get("path", "unknown")
        if path in parsed:
            content = parsed[path]
            logger.info("Bundle [%s] using bundled content for %s", bundle_name, path)
        else:
            logger.info("Bundle [%s] generating individually: %s", bundle_name, path)
            result = generate_single_file(bp, project_rules, file_blueprints)
            content = result.get("content", "")
        metadata = write_file({"path": path, "content": content}, output_dir)
        register_file(registry, bp, metadata)
        written.append(metadata)

    return written
