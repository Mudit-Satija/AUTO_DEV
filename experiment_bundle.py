"""Bundle generation experiment — tests if Qwen can generate 3 files in one call.

Usage:
    cd AUTO_DEV
    python experiment_bundle.py

Requires:
    NVIDIA_API_KEY in .env
    llm_client.py (shared with AUTO_DEV)
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm_client import get_llm_response, CODER_MODEL

BUNDLE_PROMPT = """You are a code generation assistant. Generate the following 3 files for an Express.js project with PostgreSQL.

Return ONLY a single valid JSON object in this exact format (no markdown, no text before/after):

{
  "package.json": "...",
  "src/app.js": "...",
  "src/routes/projects.js": "..."
}

RULES FOR ESCAPING (CRITICAL):
- Each value is a STRING containing the file's content.
- Inside each string, escape: double quotes as \\", backslashes as \\\\, newlines as \\n.
- For package.json (which is itself JSON): double-escape everything inside the value string.
- If you follow escaping rules correctly, the entire output will be parseable by JSON.parse().

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

Return ONLY the JSON object. No explanations. No markdown."""


def _strip_markdown_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        first_nl = text.find("\n")
        if first_nl != -1:
            text = text[first_nl + 1:]
        if text.endswith("```"):
            text = text[:-3].strip()
    return text


def main():
    os.makedirs("experiment_output", exist_ok=True)

    print("=" * 60)
    print("  BUNDLE GENERATION EXPERIMENT")
    print("=" * 60)
    print(f"  Model:            {CODER_MODEL}")
    print(f"  Files requested:  3 (package.json, src/app.js, src/routes/projects.js)")
    print()

    # --- Phase 1: Generate ---
    print("  [1/4] Sending bundled prompt to Qwen...")
    start = time.perf_counter()
    raw_text = get_llm_response(BUNDLE_PROMPT, model=CODER_MODEL)
    elapsed = time.perf_counter() - start

    response_size = len(raw_text)
    print(f"  [2/4] Response received in {elapsed:.2f}s ({response_size} chars)")
    print()

    # Save raw output for inspection
    with open("experiment_output/raw_response.txt", "w", encoding="utf-8") as f:
        f.write(raw_text)

    with open("experiment_output/raw_response_preview.txt", "w", encoding="utf-8") as f:
        f.write(raw_text[:2000])

    # --- Phase 2: Parse ---
    print("  [3/4] Attempting JSON parse...")
    cleaned = _strip_markdown_fence(raw_text)
    parsed = None
    parse_ok = False

    try:
        parsed = json.loads(cleaned)
        parse_ok = True
        print(f"  Result:            PARSE SUCCESS")
    except json.JSONDecodeError as e:
        print(f"  Result:            PARSE FAILED")
        print(f"  Error:             {e}")

    # --- Phase 3: Validate ---
    print()
    print("  [4/4] Validating files...")

    file_count = 0
    file_details = {}

    if isinstance(parsed, dict):
        file_count = len(parsed)
        for key in ["package.json", "src/app.js", "src/routes/projects.js"]:
            content = parsed.get(key)
            if content is None:
                print(f"    {key}: MISSING")
                file_details[key] = {"status": "missing", "chars": 0}
                continue
            if not isinstance(content, str):
                print(f"    {key}: ERROR — value is {type(content).__name__}, expected str")
                file_details[key] = {"status": "wrong_type", "chars": 0}
                continue

            problems = []

            if key == "package.json":
                try:
                    json.loads(content)
                    pkg_status = "valid JSON"
                except json.JSONDecodeError:
                    pkg_status = "invalid JSON"
                    problems.append("not valid JSON")

            if key.endswith(".js"):
                if "module.exports" not in content:
                    problems.append("missing module.exports")

            status = "ok" if not problems else "; ".join(problems)
            print(f"    {key}: {len(content)} chars — {status}")
            file_details[key] = {"status": status, "chars": len(content)}
    else:
        print("    (no files to validate — parse failed)")

    # --- Summary ---
    print()
    print("-" * 60)
    print("  SUMMARY")
    print("-" * 60)
    print(f"  Generation time:     {elapsed:.2f}s")
    print(f"  Response size:       {response_size} chars")
    print(f"  JSON parse:          {'YES' if parse_ok else 'NO'}")
    print(f"  Files returned:      {file_count} / 3")

    if parse_ok and file_details:
        for key, info in file_details.items():
            print(f"    {key}: {info['status']}")
    print("-" * 60)

    # 3 sequential calls baseline for comparison
    seq_time_estimate = 0
    if parse_ok:
        # Measure one sequential call for baseline comparison
        print()
        print("  Measuring sequential baseline (1 file)...")

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
        seq_time_estimate = seq_single * 3
        print(f"  Single file:         {seq_single:.2f}s")
        print(f"  3 × sequential est:  {seq_time_estimate:.2f}s")
        print(f"  Bundle vs 3×seq:     {elapsed:.2f}s vs {seq_time_estimate:.2f}s")
        print(f"  Speedup:             {seq_time_estimate / elapsed:.1f}x")

    # Save machine-readable result
    result = {
        "success": parse_ok,
        "generation_time_s": round(elapsed, 2),
        "sequential_3x_estimate_s": round(seq_time_estimate, 2) if seq_time_estimate else None,
        "response_size_chars": response_size,
        "files_requested": 3,
        "files_returned": file_count,
        "file_details": file_details,
        "model": CODER_MODEL,
    }

    with open("experiment_output/result.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n  Full output saved to experiment_output/")
    print("=" * 60)

    return 0 if parse_ok else 1


if __name__ == "__main__":
    sys.exit(main())
