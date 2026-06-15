"""Project Generator — generates and persists all files from a build plan.

Uses bundle generation (multiple files per Qwen call) with automatic
fallback to single-file generation when bundle validation fails.

Independent bundles (backend, frontend, database, docs) are executed
in parallel using a thread pool for I/O-bound LLM calls.

After initial generation, an auto-repair loop re-generates any files
that fail import, smoke, or requirement validation.
"""

import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from coding_agent.bundle_generator import generate_bundle_with_fallback, group_and_partition_files
from coding_agent.dependency_graph import validate_graph, validate_imports
from coding_agent.file_registry import register_file, save_registry
from coding_agent.file_writer import write_file
from coding_agent.metrics import get_metrics_collector
from coding_agent.prompt_builder import build_file_prompt
from coding_agent.requirement_validator import validate_requirements
from coding_agent.smoke_test import run_smoke_tests
from llm_client import CODER_MODEL, get_llm_response

logger = logging.getLogger(__name__)

MAX_REPAIR_ATTEMPTS = 0


def _run_bundle(
    bundle_name: str,
    file_blueprints: list,
    project_rules: dict,
    output_dir: str,
) -> tuple:
    """Execute a single bundle in isolation and return (written_metadata, local_registry).
    
    Files with static_content are written directly without LLM calls.
    """
    local_registry: dict = {}
    
    # Static template files — skip LLM entirely
    if all(bp.get("static_content") for bp in file_blueprints):
        written = []
        for bp in file_blueprints:
            content = bp["static_content"]
            meta = write_file({"path": bp["path"], "content": content}, output_dir)
            register_file(local_registry, bp, meta)
            written.append(meta)
            logger.info("Static file written: %s (%d bytes)", bp["path"], meta.get("size", 0))
        return written, local_registry
    
    written = generate_bundle_with_fallback(
        bundle_name, file_blueprints, project_rules, output_dir, local_registry,
    )
    return written, local_registry


# ---------------------------------------------------------------------------
# Auto-repair helpers
# ---------------------------------------------------------------------------


def _extract_file_from_import_error(error_msg: str) -> str | None:
    """Parse the file path from an import validation error message.

    Error format::

        Import Validation Failed

            src/controllers/workspaces.js

        references

            ../models/workspaces

        which was not generated.
    """
    lines = error_msg.strip().split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and lines[i - 1].strip() == "" if i > 0 else False:
            return stripped.replace("\\", "/")
    return None


def _extract_file_from_smoke_error(error_msg: str) -> str | None:
    """Parse a file path from a smoke-test error message.

    Matches patterns like: "JS syntax error in src/file.js: ..."
    """
    m = re.search(r"in\s+([^\s:]+):", error_msg)
    if m:
        return m.group(1).replace("\\", "/")
    return None


def _collect_repair_errors(build_plan: dict, project_rules: dict, output_dir: str) -> dict:
    """Run all post-generation validations and group errors by file path.

    Returns ``{file_path: [error_string, ...]}``.
    """
    errors_by_file: dict = {}

    # Import validation
    for err in validate_imports(build_plan, output_dir):
        file_path = _extract_file_from_import_error(err)
        if not file_path:
            file_path = "unknown"
        errors_by_file.setdefault(file_path, []).append(err)

    # Smoke tests
    for err in run_smoke_tests(output_dir, project_rules):
        file_path = _extract_file_from_smoke_error(err)
        if not file_path:
            file_path = "unknown"
        errors_by_file.setdefault(file_path, []).append(err)

    # Requirement coverage
    req_result = validate_requirements(output_dir, build_plan)
    if not req_result["success"]:
        for e in req_result["errors"]:
            file_path = e.get("file", "unknown")
            msg = f"Requirement '{e['requirement']}': {e['error']}"
            errors_by_file.setdefault(file_path, []).append(msg)

    return errors_by_file


def _build_repair_prompt(
    blueprint: dict,
    project_rules: dict,
    errors: list[str],
    attempt: int,
    all_blueprints: list = None,
) -> str:
    """Build a prompt that includes the original file context plus error feedback."""
    prompt = build_file_prompt(blueprint, project_rules, all_blueprints)
    prompt += (
        f"\n\nPREVIOUS GENERATION HAD VALIDATION ERRORS (attempt {attempt}):\n"
    )
    for err in errors:
        prompt += f"  - {err}\n"
    prompt += (
        "\nRegenerate the file above. Fix ALL errors listed. "
        "Return only the raw source code, no markdown or explanations."
    )
    return prompt


def _repair_failing_files(
    errors_by_file: dict,
    build_plan: dict,
    project_rules: dict,
    output_dir: str,
    written: list,
    registry: dict,
) -> tuple[list, dict]:
    """Regenerate each failing file with error context and return updated (written, registry)."""
    blueprints_by_path = {bp["path"]: bp for bp in build_plan.get("files", [])}

    for file_path, error_list in errors_by_file.items():
        bp = blueprints_by_path.get(file_path)
        if not bp:
            logger.warning("Repair: no blueprint for %s, skipping", file_path)
            continue

        logger.warning("Repairing %s (%d errors)", file_path, len(error_list))
        repair_prompt = _build_repair_prompt(bp, project_rules, error_list, MAX_REPAIR_ATTEMPTS, build_plan.get("files", []))
        content = get_llm_response(repair_prompt, model=CODER_MODEL)
        meta = write_file({"path": file_path, "content": content}, output_dir)
        register_file(registry, bp, meta)
        written = [w for w in written if w["path"] != file_path] + [meta]

    return written, registry


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_project(
    build_plan: dict,
    project_rules: dict,
    output_dir: str,
    max_repair_attempts: int = MAX_REPAIR_ATTEMPTS,
) -> dict:
    """Generate and write all files in a build plan to disk.

    Files are grouped into bundles (backend, frontend, database, docs)
    and generated in parallel. If a bundle fails validation, individual
    files fall back to single-file generation.

    After initial generation an auto-repair loop re-generates any files
    that fail import, smoke, or requirement validation (up to
    *max_repair_attempts* rounds).

    Args:
        build_plan: Output from build_plan.generate_build_plan() with key "files".
        project_rules: Output from rules_engine.build_project_rules().
        output_dir: Root directory for the generated project.
        max_repair_attempts: How many repair rounds before giving up (default 3).

    Returns:
        Dict with keys:
            files_generated (int): total files processed
            files_written (list[dict]): metadata from write_file() per file
            registry_path (str or None): path to saved .autodev_registry.json
            repair_attempts (int): how many repair rounds were executed
            all_validations_pass (bool): whether all post-gen checks passed
    """
    metrics = get_metrics_collector()
    files = build_plan.get("files", [])

    if max_repair_attempts > 0:
        logger.warning("Repair loops are currently enabled (max_repair_attempts=%d)", max_repair_attempts)

    metrics.start_pipeline(len(files))

    # Phase 1: Pre-generation dependency graph validation
    dep_errors = validate_graph(build_plan)
    if dep_errors:
        msg = "Dependency Validation Failed\n\n" + "\n".join(dep_errors)
        logger.error(msg)
        metrics.end_pipeline("Failed")
        raise ValueError(msg)

    registry: dict = {}
    written: list = []

    # Store full file inventory for prompt visibility
    project_rules = dict(project_rules)  # copy to avoid mutating caller's dict
    project_rules["all_files"] = files

    bundles = group_and_partition_files(files)
    logger.info(
        "Grouped %d files into %d bundles (max %d per bundle): %s",
        len(files), len(bundles), 6, list(bundles.keys()),
    )

    if not bundles:
        metrics.end_pipeline("Success")
        return {
            "files_generated": 0,
            "files_written": [],
            "registry_path": None,
            "repair_attempts": 0,
            "all_validations_pass": True,
        }

    with ThreadPoolExecutor(max_workers=min(4, len(bundles))) as executor:
        future_map = {
            executor.submit(
                _run_bundle, name, bundles[name], project_rules, output_dir,
            ): name
            for name in sorted(bundles.keys())
        }

        for future in as_completed(future_map):
            name = future_map[future]
            try:
                written_local, registry_local = future.result()
                logger.info("Bundle [%s] completed: %d files written", name, len(written_local))
                written.extend(written_local)
                registry.update(registry_local)
            except Exception:
                logger.exception("Bundle [%s] failed with exception", name)

    registry_path = None
    if registry:
        registry_path = save_registry(registry, output_dir)

    result = {
        "files_generated": len(files),
        "files_written": written,
        "registry_path": registry_path,
        "repair_attempts": 0,
        "all_validations_pass": True,
    }

    # Auto-repair loop
    for attempt in range(1, max_repair_attempts + 1):
        validation_start = time.perf_counter()
        errors_by_file = _collect_repair_errors(build_plan, project_rules, output_dir)
        validation_duration_ms = int((time.perf_counter() - validation_start) * 1000)
        metrics.record_validation_time(validation_duration_ms)

        if not errors_by_file:
            logger.info("All post-generation validations passed")
            result["repair_attempts"] = attempt - 1
            result["all_validations_pass"] = True
            post_process_generated_files(output_dir)
            metrics.end_pipeline("Success")
            return result

        logger.warning(
            "Repair attempt %d/%d: %d files with errors",
            attempt, max_repair_attempts, len(errors_by_file),
        )

        written, registry = _repair_failing_files(
            errors_by_file, build_plan, project_rules, output_dir,
            written, registry,
        )

        registry_path = save_registry(registry, output_dir)
        result["files_written"] = written
        result["registry_path"] = registry_path

    # Final validation after all repairs exhausted
    validation_start = time.perf_counter()
    final_errors = _collect_repair_errors(build_plan, project_rules, output_dir)
    validation_duration_ms = int((time.perf_counter() - validation_start) * 1000)
    metrics.record_validation_time(validation_duration_ms)

    result["repair_attempts"] = max_repair_attempts
    result["all_validations_pass"] = not final_errors
    if final_errors:
        total = sum(len(v) for v in final_errors.values())
        logger.warning(
            "Repair exhausted after %d attempts — %d remaining errors",
            max_repair_attempts, total,
        )

    post_process_generated_files(output_dir)
    metrics.end_pipeline("Success" if not final_errors else "Failed")
    return result


def post_process_generated_files(output_dir: str) -> None:
    """Fix common LLM code generation errors via string replacement.
    Runs after all files are written and before zipping.

    Fixes for Llama-3.1-8B known issues:
    - Markdown code fences (```jsx, ```javascript, ```)
    - React Router v5 useHistory / history.push → v6 useNavigate / navigate
    - CSS imports in page files (App.css import in pages/*.jsx)
    - Mongoose import paths in backend models
    """
    import glob as glob_mod
    import re

    root = output_dir.replace("\\", "/")

    # Fix all .js and .jsx files (skip node_modules)
    for filepath in glob_mod.glob(root + "/**/*.js*", recursive=True):
        if 'node_modules' in filepath:
            continue
        # Normalize path separators (Windows glob returns backslashes)
        norm_path = filepath.replace('\\', '/')
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        original = content

        # 1. Strip leading/trailing markdown code fences
        content = re.sub(
            r'^```(?:jsx|javascript|js|tsx|ts)\s*\n',
            '',
            content,
            count=1,
        )
        content = re.sub(
            r'\n```\s*$',
            '',
            content,
            count=1,
        )

        # 2. Replace useHistory → useNavigate, history.push → navigate
        content = content.replace('useHistory', 'useNavigate')
        content = content.replace('history.push', 'navigate')

        # 3. Strip CSS imports from page files only (pages/*.jsx)
        #    App.jsx and main.jsx legitimately import App.css; pages should not.
        if '/pages/' in norm_path and norm_path.endswith('.jsx'):
            content = re.sub(
                r"^import\s+['\"]?[^'\"\n]*\.css['\"]?\s*;?\s*$",
                '',
                content,
                flags=re.MULTILINE,
            )

        # 4. Fix mongoose import paths (backward compat for backend models)
        content = content.replace(
            "const mongoose = require('../config/database')",
            "const mongoose = require('mongoose')",
        )
        content = content.replace(
            "const mongoose = require('./config/database')",
            "const mongoose = require('mongoose')",
        )

        if content != original:
            logger.info("post_process: fixed %s", filepath)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
