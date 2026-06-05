"""Bundle generation experiment v2 — delimiter-based format (no JSON escaping).

Compares against v1 to isolate whether the bottleneck is bundling
itself or JSON-in-JSON escaping.

Usage:
    python experiment_bundle_v2.py
"""

import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm_client import get_llm_response, CODER_MODEL

DELIMITER_PROMPT = """You are a code generation assistant. Generate the following 3 files for an Express.js project with PostgreSQL.

Use this exact delimiter format (no JSON, no markdown, no explanations):

===FILE: package.json===
<content here>
===END===

===FILE: src/app.js===
<content here>
===END===

===FILE: src/routes/projects.js===
<content here>
===END===

RULES:
- Each file must start with ===FILE: <path>=== on its own line.
- Each file must end with ===END=== on its own line.
- Write the file content as-is, with real newlines and real double quotes.
- Do NOT escape anything. Write raw file contents.
- Do NOT wrap the output in markdown code blocks.
- Do NOT add any text before the first ===FILE or after the last ===END.
- Return only the delimiter-formatted content, nothing else.

FILE 1 — package.json
- name: "project-api", version: "1.0.0"
- Dependencies: express, cors, helmet, dotenv, jsonwebtoken, bcryptjs, pg
- Dev dependencies: nodemon
- Scripts: "start": "node src/server.js", "dev": "nodemon src/server.js"

FILE 2 — src/app.js
- Express app setup
- Require and mount routes from ./routes/projects at /api/projects
- Middleware: cors(), helmet(), express.json()
- GET /api/health -> { status: "OK" }
- 404 handler
- Global error handler
- Use process.env.PORT or 5000
- module.exports = app (do NOT call app.listen)

FILE 3 — src/routes/projects.js
- Express Router
- Use pg Pool for PostgreSQL (require pg)
- Full CRUD endpoints:
  GET    /              -> SELECT all projects
  GET    /:id           -> SELECT project by id
  POST   /              -> INSERT new project (name, description, status)
  PUT    /:id           -> UPDATE project
  DELETE /:id           -> DELETE project
- Use parameterized queries ($1, $2, etc.) to prevent SQL injection
- No auth middleware (keep it simple)
- module.exports = router

Return ONLY the delimiter-formatted content. No explanations. No markdown."""


def parse_delimiter_output(text: str) -> dict:
    """Parse ===FILE: path=== ... ===END=== blocks into {path: content}."""
    files = {}
    pattern = re.compile(
        r"===FILE:\s*(.+?)===\s*\n(.*?)\n===END===",
        re.DOTALL,
    )
    for match in pattern.finditer(text):
        path = match.group(1).strip()
        content = match.group(2)
        files[path] = content
    return files


def main():
    os.makedirs("experiment_output", exist_ok=True)

    print("=" * 60)
    print("  BUNDLE EXPERIMENT V2 — DELIMITER FORMAT")
    print("=" * 60)
    print(f"  Model:            {CODER_MODEL}")
    print(f"  Files requested:  3")
    print()

    # --- Generate ---
    print("  [1/3] Sending delimiter-based prompt to Qwen...")
    start = time.perf_counter()
    raw_text = get_llm_response(DELIMITER_PROMPT, model=CODER_MODEL)
    elapsed = time.perf_counter() - start
    response_size = len(raw_text)
    print(f"  [2/3] Response in {elapsed:.2f}s ({response_size} chars)")

    # Save raw
    with open("experiment_output/raw_response_v2.txt", "w", encoding="utf-8") as f:
        f.write(raw_text)
    with open("experiment_output/raw_response_v2_preview.txt", "w", encoding="utf-8") as f:
        f.write(raw_text[:2000])

    # --- Parse ---
    print("  [3/3] Parsing delimiter blocks...")
    parsed = parse_delimiter_output(raw_text)
    file_count = len(parsed)

    parse_ok = file_count > 0
    print(f"  Parse result:      {'SUCCESS' if parse_ok else 'FAILED'} ({file_count} files)")

    # --- Validate ---
    print()
    print("  File validation:")
    file_details = {}

    for key in ["package.json", "src/app.js", "src/routes/projects.js"]:
        content = parsed.get(key)
        if content is None:
            print(f"    {key}: MISSING")
            file_details[key] = {"status": "missing", "chars": 0}
            continue

        problems = []

        if key == "package.json":
            try:
                json.loads(content)
                pkg_status = "valid JSON"
            except json.JSONDecodeError as e:
                pkg_status = f"invalid JSON: {e}"
                problems.append("not valid JSON")

        if key.endswith(".js"):
            if "module.exports" not in content:
                problems.append("missing module.exports")
            # Check for pg usage (PostgreSQL, not MongoDB)
            if "require('pg')" in content or 'require("pg")' in content or "from 'pg'" in content:
                pass  # OK
            elif "mongoose" in content.lower() or "mongodb" in content.lower():
                problems.append("uses MongoDB instead of PostgreSQL")

        status = "ok" if not problems else "; ".join(problems)
        print(f"    {key}: {len(content)} chars — {status}")
        file_details[key] = {"status": status, "chars": len(content)}

    # --- Summary ---
    print()
    print("-" * 60)
    print("  SUMMARY")
    print("-" * 60)
    print(f"  Generation time:     {elapsed:.2f}s")
    print(f"  Response size:       {response_size} chars")
    print(f"  Parse success:       {'YES' if parse_ok else 'NO'}")
    print(f"  Files returned:      {file_count} / 3")
    for key, info in file_details.items():
        print(f"    {key}: {info['status']}")

    # Compare with v1
    print()
    print("  V1 COMPARISON (JSON format vs Delimiter format)")
    print(f"    V1 (JSON):      37.83s — parse OK, package.json invalid")
    print(f"    V2 (delimiter): {elapsed:.2f}s — parse {'OK' if parse_ok else 'FAILED'}")

    # Sequential baseline
    print()
    print("  Measuring sequential baseline...")
    single_prompt = """You are a code generation assistant. Generate the content for a single file.

Context:
- Backend framework: Express.js
- Frontend framework: None
- Database: PostgreSQL
- Auth method: JWT

File to generate:
- Path: package.json
- Purpose: Node.js dependencies and scripts
- Type: config

Instructions:
- Return only the raw source code.
- Do NOT wrap the code in markdown code blocks.
- Do NOT include any explanations, commentary, or natural language.
- Generate only the requested file.
- The code must be complete, functional, and follow best practices."""

    s = time.perf_counter()
    get_llm_response(single_prompt, model=CODER_MODEL)
    seq_single = time.perf_counter() - s
    seq_3x = seq_single * 3
    print(f"    Single file:        {seq_single:.2f}s")
    print(f"    3 × sequential est: {seq_3x:.2f}s")
    print(f"    Bundle vs 3×seq:    {elapsed:.2f}s vs {seq_3x:.2f}s")
    print(f"    Speedup:            {seq_3x / elapsed:.1f}x")
    print("-" * 60)

    # Save results
    result = {
        "experiment": "v2_delimiter",
        "success": parse_ok,
        "generation_time_s": round(elapsed, 2),
        "sequential_3x_estimate_s": round(seq_3x, 2),
        "response_size_chars": response_size,
        "files_requested": 3,
        "files_returned": file_count,
        "file_details": file_details,
        "model": CODER_MODEL,
    }
    with open("experiment_output/result_v2.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n  Results saved to experiment_output/")
    print("=" * 60)

    return 0 if parse_ok else 1


if __name__ == "__main__":
    sys.exit(main())
