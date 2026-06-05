"""Bundle generation experiment v3 — 6-file realistic backend bundle.

Tests whether delimiters scale from 3 files to a full backend group.
"""

import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm_client import get_llm_response, CODER_MODEL

# Reuse v2 parser
def parse_delimiter_output(text: str) -> dict:
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


BUNDLE_6_PROMPT = """You are a code generation assistant. Generate exactly 6 files for an Express.js + PostgreSQL backend.

Use this exact delimiter format (no JSON, no markdown, no explanations):

===FILE: package.json===
<content>
===END===

===FILE: src/app.js===
<content>
===END===

===FILE: src/server.js===
<content>
===END===

===FILE: src/routes/projects.js===
<content>
===END===

===FILE: src/routes/auth.js===
<content>
===END===

===FILE: src/middleware/auth.js===
<content>
===END===

RULES:
- Each file starts with ===FILE: <path>=== on its own line.
- Each file ends with ===END=== on its own line.
- Write raw file content with real newlines and real quotes.
- Do NOT escape anything.
- Do NOT wrap in markdown code blocks.
- Do NOT add text before the first ===FILE or after the last ===END.
- Return ONLY the delimiter-formatted content.
- Generate ALL 6 files — do not skip any.

FILE 1 — package.json
- name: "project-api", version: "1.0.0"
- Dependencies: express, cors, helmet, dotenv, jsonwebtoken, bcryptjs, pg, express-rate-limit
- Dev dependencies: nodemon
- Scripts: "start": "node src/server.js", "dev": "nodemon src/server.js"

FILE 2 — src/app.js
- Express app setup
- Middleware: cors(), helmet(), express.json(), rate limiting
- Import and mount routes: projectsRouter at /api/projects, authRouter at /api/auth
- GET /api/health -> { status: "OK" }
- 404 handler
- Global error handler
- module.exports = app

FILE 3 — src/server.js
- Import app from ./app
- Read PORT from process.env (default 5000)
- app.listen(PORT, callback)
- Log "Server running on port PORT"

FILE 4 — src/routes/projects.js
- Express Router
- Use pg Pool from 'pg' for PostgreSQL
- Require auth middleware from ../middleware/auth
- Protected CRUD endpoints:
  GET    /           -> SELECT all projects
  GET    /:id        -> SELECT project by id
  POST   /           -> INSERT project (name, description, status)
  PUT    /:id        -> UPDATE project
  DELETE /:id        -> DELETE project
- Use parameterized queries ($1, $2, etc.)
- module.exports = router

FILE 5 — src/routes/auth.js
- Express Router
- Use pg Pool from 'pg' for PostgreSQL
- Use bcryptjs for password hashing
- Use jsonwebtoken for JWT signing
- Endpoints:
  POST   /register   -> hash password, INSERT user, return token
  POST   /login      -> find user, compare password, return token
  GET    /me         -> require auth middleware, return user info
- module.exports = router

FILE 6 — src/middleware/auth.js
- JWT verification middleware for Express
- Extract token from Authorization: Bearer <token> header
- Verify with jsonwebtoken using process.env.JWT_SECRET
- Attach decoded user to req.user
- Export middleware function

Return ONLY the delimiter-formatted content. No explanations. No markdown."""


def main():
    os.makedirs("experiment_output", exist_ok=True)

    expected_files = [
        "package.json",
        "src/app.js",
        "src/server.js",
        "src/routes/projects.js",
        "src/routes/auth.js",
        "src/middleware/auth.js",
    ]

    print("=" * 60)
    print("  BUNDLE EXPERIMENT V3 — 6-FILE BACKEND")
    print("=" * 60)
    print(f"  Model:            {CODER_MODEL}")
    print(f"  Files requested:  {len(expected_files)}")
    print()

    # --- Generate ---
    print("  [1/3] Sending 6-file bundle prompt to Qwen...")
    start = time.perf_counter()
    raw_text = get_llm_response(BUNDLE_6_PROMPT, model=CODER_MODEL)
    elapsed = time.perf_counter() - start
    response_size = len(raw_text)
    print(f"  [2/3] Response in {elapsed:.2f}s ({response_size} chars)")

    # Save raw
    with open("experiment_output/raw_response_v3.txt", "w", encoding="utf-8") as f:
        f.write(raw_text)
    with open("experiment_output/raw_response_v3_preview.txt", "w", encoding="utf-8") as f:
        f.write(raw_text[:3000])

    # --- Parse ---
    print("  [3/3] Parsing delimiter blocks...")
    parsed = parse_delimiter_output(raw_text)
    file_count = len(parsed)

    parse_ok = file_count > 0
    print(f"  Parse:             {'OK' if parse_ok else 'FAIL'} ({file_count} files)")

    # --- Validate ---
    print()
    print("  Validation:")
    file_details = {}
    all_ok = True

    for key in expected_files:
        content = parsed.get(key)
        if content is None:
            print(f"    {key}: MISSING")
            file_details[key] = {"status": "missing", "chars": 0}
            all_ok = False
            continue

        problems = []

        if key == "package.json":
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                problems.append(f"invalid JSON: {e}")

        if key.endswith(".js"):
            if "module.exports" not in content:
                problems.append("missing module.exports")

        if "projects" in key:
            if "pg" not in content and "postgres" not in content.lower():
                problems.append("no PostgreSQL usage")

        if "auth.js" in key and "middleware" in key:
            if "jwt" not in content.lower() and "jsonwebtoken" not in content:
                problems.append("no JWT verification")

        status = "ok" if not problems else "; ".join(problems)
        if problems:
            all_ok = False
        print(f"    {key}: {len(content)} chars — {status}")
        file_details[key] = {"status": status, "chars": len(content)}

    # Check for extra unexpected files
    extra = [k for k in parsed if k not in expected_files]
    if extra:
        print(f"    Extra files: {extra}")
        file_details["_extra"] = extra

    # --- Summary ---
    print()
    print("-" * 60)
    print("  SUMMARY")
    print("-" * 60)
    print(f"  Generation time:     {elapsed:.2f}s")
    print(f"  Response size:       {response_size} chars")
    print(f"  Files returned:      {file_count} / {len(expected_files)}")
    print(f"  All valid:           {'YES' if all_ok else 'NO'}")
    for key, info in file_details.items():
        print(f"    {key}: {info['status']}")

    # 6× sequential estimate
    print()
    print("  Measuring sequential baseline...")
    single_prompt = """You are a code generation assistant. Generate the content for a single file.

Context:
- Backend framework: Express.js
- Database: PostgreSQL
- Auth method: JWT

File to generate:
- Path: package.json
- Purpose: Node.js dependencies and scripts
- Type: config

Instructions:
- Return only the raw source code.
- Do NOT wrap the code in markdown code blocks.
- Do NOT include any explanations.
- Generate only the requested file."""

    s = time.perf_counter()
    get_llm_response(single_prompt, model=CODER_MODEL)
    seq_single = time.perf_counter() - s
    seq_6x = seq_single * 6
    print(f"    Single file:        {seq_single:.2f}s")
    print(f"    6 × sequential est: {seq_6x:.2f}s")
    print(f"    Bundle vs 6×seq:    {elapsed:.2f}s vs {seq_6x:.2f}s")
    print(f"    Speedup:            {seq_6x / elapsed:.1f}x")
    print("-" * 60)

    # Recommendation
    print()
    speedup = seq_6x / elapsed
    if parse_ok and all_ok and speedup >= 1.5:
        rec = "ADOPT — bundling is reliable and faster"
    elif parse_ok and all_ok:
        rec = "CAUTIOUS — bundling works but speedup is marginal"
    elif parse_ok and not all_ok:
        rec = "NEEDS WORK — parse succeeds but quality issues need fixing"
    else:
        rec = "ABANDON — delimiter parsing failed at 6 files"

    print(f"  RECOMMENDATION: {rec}")
    print("=" * 60)

    result = {
        "experiment": "v3_6file_bundle",
        "success": parse_ok and all_ok,
        "generation_time_s": round(elapsed, 2),
        "sequential_6x_estimate_s": round(seq_6x, 2),
        "speedup_x": round(speedup, 1),
        "response_size_chars": response_size,
        "files_requested": len(expected_files),
        "files_returned": file_count,
        "extra_files": extra,
        "all_valid": all_ok,
        "file_details": file_details,
        "model": CODER_MODEL,
        "recommendation": rec,
    }
    with open("experiment_output/result_v3.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n  Results saved to experiment_output/")
    return 0 if (parse_ok and all_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
