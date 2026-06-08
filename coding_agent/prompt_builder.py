"""Prompt Builder â€” converts file blueprints into deterministic Qwen prompts."""

from typing import Any, Dict, List

from coding_agent.prompt_constraints import auth_is_enabled, build_prompt_constraints


def _serialize_spec(spec: dict) -> List[str]:
    """Convert a blueprint spec into deterministic instruction strings.

    Handles three spec shapes:
      - CRUD route endpoints: spec["endpoints"] (no /register)
      - Auth route endpoints:  spec["endpoints"] (has /register)
      - Route aggregator:      spec["mounts"]
    """
    lines: List[str] = []

    if "endpoints" in spec:
        endpoints = spec["endpoints"]
        is_auth = any("/register" in ep.get("path", "") for ep in endpoints)
        model = spec.get("model", {})
        ops = model.get("operations", [])
        is_mongo = any(o.startswith("find") for o in ops)

        if is_auth:
            lines.append("Authentication routes:")
            lines.append("- Register: accept email and password, let the User model's pre-save hook hash the password (pass plain password to User.create()), sign JWT with process.env.JWT_SECRET, return 201 with { token }")
            lines.append("- Login: find user by email with User.findOne(), compare password with bcrypt.compare(), sign JWT with process.env.JWT_SECRET, return { token }")
            lines.append("- Logout: return 200 with { message: 'Logged out successfully' }")
            lines.append("- Never hash the password twice — pass the plain password and let the model's pre-save hook handle hashing")
            lines.append("- JWT payload must be: { id: user._id, email: user.email }")
            lines.append("- Use process.env.JWT_SECRET — never hardcode the secret")
            if model:
                model_name = model.get("name", "User")
                lines.append(f"- Import {model_name} from {model.get('path', '../models/users')}")
                lines.append(f"- Model name is exactly '{model_name}' — copy spelling exactly")
            lines.append("- Export the router as module.exports = router")
        else:
            model_name = model.get("name", "Model")
            model_path = model.get("path", "../models/model")
            middleware_list = spec.get("middleware", [])
            populate = spec.get("populate", {}) or {}

            lines.append("The complete file must follow this exact structure:")
            lines.append("1. const express = require('express');")
            lines.append("2. const router = express.Router();")
            lines.append(f"3. const {model_name} = require('{model_path}');")
            lines.append(f"- Model name is exactly '{model_name}' — copy spelling exactly")
            if middleware_list:
                for mw in middleware_list:
                    lines.append(f"4. const {mw['name']} = require('{mw['path']}');")
                for mw in middleware_list:
                    lines.append(f"5. {mw['apply']}")
            lines.append("6. [all routes in exact order shown below]")
            lines.append("7. module.exports = router;")

            lines.append("")
            lines.append("Generate exactly these routes in this exact order:")

            for ep in endpoints:
                lines.append("")
                meth = ep["method"]
                p = ep["path"]

                if p == "/stats":
                    if is_mongo:
                        lines.append(f"router.get('/stats', async (req, res) => {{")
                        lines.append(f"  const count = await {model_name}.countDocuments();")
                        lines.append(f"  res.json({{ count }});")
                        lines.append(f"}});")
                    else:
                        lines.append(f"router.get('/stats', async (req, res) => {{")
                        lines.append(f"  const {{ rows }} = await pool.query('SELECT COUNT(*) AS count FROM table_name');")
                        lines.append(f"  res.json({{ count: parseInt(rows[0].count, 10) }});")
                        lines.append(f"}});")

                elif meth == "POST" and p == "/evaluate":
                    lines.append(f"router.post('/evaluate', async (req, res) => {{")
                    lines.append(f"  try {{")
                    lines.append(f"    const {{ expression }} = req.body;")
                    lines.append(f"    const result = eval(expression);")
                    lines.append(f"    res.json({{ result }});")
                    lines.append(f"  }} catch (err) {{")
                    lines.append(f"    res.status(400).json({{ error: 'Invalid expression' }});")
                    lines.append(f"  }}")
                    lines.append(f"}});")

                elif meth == "POST" and p == "/":
                    if is_mongo:
                        lines.append(f"router.post('/', async (req, res) => {{")
                        lines.append(f"  const item = await {model_name}.create(req.body);")
                        lines.append(f"  res.status(201).json(item);")
                        lines.append(f"}});")
                    else:
                        lines.append(f"router.post('/', async (req, res) => {{")
                        lines.append(f"  const {{ rows }} = await pool.query(")
                        lines.append(f"    'INSERT INTO table_name (...) VALUES ($1, ...) RETURNING *',")
                        lines.append(f"    [req.body.field1, req.body.field2]")
                        lines.append(f"  );")
                        lines.append(f"  res.status(201).json(rows[0]);")
                        lines.append(f"}});")

                elif meth == "PUT" and p == "/:id":
                    if is_mongo:
                        lines.append(f"router.put('/:id', async (req, res) => {{")
                        lines.append(f"  const item = await {model_name}.findByIdAndUpdate(")
                        lines.append(f"    req.params.id, req.body, {{ new: true }}")
                        lines.append(f"  );")
                        lines.append(f"  if (!item) return res.status(404).json({{ message: 'Not found' }});")
                        lines.append(f"  res.json(item);")
                        lines.append(f"}});")
                    else:
                        lines.append(f"router.put('/:id', async (req, res) => {{")
                        lines.append(f"  const {{ rows }} = await pool.query(")
                        lines.append(f"    'UPDATE table_name SET ... WHERE id = $1 RETURNING *',")
                        lines.append(f"    [req.params.id, req.body.field1, req.body.field2]")
                        lines.append(f"  );")
                        lines.append(f"  if (rows.length === 0) return res.status(404).json({{ message: 'Not found' }});")
                        lines.append(f"  res.json(rows[0]);")
                        lines.append(f"}});")

                elif meth == "DELETE" and p == "/:id":
                    if is_mongo:
                        lines.append(f"router.delete('/:id', async (req, res) => {{")
                        lines.append(f"  await {model_name}.findByIdAndDelete(req.params.id);")
                        lines.append(f"  res.status(204).end();")
                        lines.append(f"}});")
                    else:
                        lines.append(f"router.delete('/:id', async (req, res) => {{")
                        lines.append(f"  await pool.query('DELETE FROM table_name WHERE id = $1', [req.params.id]);")
                        lines.append(f"  res.status(204).end();")
                        lines.append(f"}});")

                elif meth == "GET" and p == "/":
                    populate_clause = ""
                    if is_mongo and populate.get("field"):
                        populate_clause = f".populate('{populate['field']}', '{populate.get('select', '')}')"
                    if is_mongo:
                        lines.append(f"router.get('/', async (req, res) => {{")
                        lines.append(f"  const items = await {model_name}.find(){populate_clause};")
                        lines.append(f"  res.json(items);")
                        lines.append(f"}});")
                    else:
                        lines.append(f"router.get('/', async (req, res) => {{")
                        lines.append(f"  const {{ rows }} = await pool.query('SELECT * FROM table_name');")
                        lines.append(f"  res.json(rows);")
                        lines.append(f"}});")

                elif meth == "GET" and p == "/:id":
                    populate_clause = ""
                    if is_mongo and populate.get("field"):
                        populate_clause = f".populate('{populate['field']}', '{populate.get('select', '')}')"
                    if is_mongo:
                        lines.append(f"router.get('/:id', async (req, res) => {{")
                        lines.append(f"  const item = await {model_name}.findById(req.params.id){populate_clause};")
                        lines.append(f"  if (!item) return res.status(404).json({{ message: 'Not found' }});")
                        lines.append(f"  res.json(item);")
                        lines.append(f"}});")
                    else:
                        lines.append(f"router.get('/:id', async (req, res) => {{")
                        lines.append(f"  const {{ rows }} = await pool.query('SELECT * FROM table_name WHERE id = $1', [req.params.id]);")
                        lines.append(f"  if (rows.length === 0) return res.status(404).json({{ message: 'Not found' }});")
                        lines.append(f"  res.json(rows[0]);")
                        lines.append(f"}});")

    elif "mounts" in spec:
        for mount in spec.get("mounts", []):
            base = mount["router"].lstrip("./")
            lines.append(f"- Import {base}Router from {mount['router']}. Mount with: router.use('{mount['path']}', {base}Router)")
        lines.append("- Export the router as module.exports = router")

    elif "api_calls" in spec:
        lines.append("This page calls these exact API endpoints — use no other URLs:")
        for call in spec["api_calls"]:
            method = call["method"]
            endpoint = call["endpoint"]
            body = call.get("body")
            if body:
                lines.append(f"- {method} {endpoint} — body: {', '.join(body)}")
            else:
                lines.append(f"- {method} {endpoint}")
        if any("/auth/register" in call.get("endpoint", "") for call in spec["api_calls"]):
            lines.append("- Registration form fields: email, password, name")
            lines.append("- Send exactly { email, password, name } to POST /auth/register")

    elif "jwt_payload" in spec:
        lines.append("- JWT payload shape is: { id, email }")
        lines.append("- After jwt.verify(), set req.user = decoded (not decoded.user)")
        lines.append("- req.user.id gives the user id in route handlers")

    return lines


def build_file_prompt(file_blueprint: dict, project_rules: dict, all_blueprints: List[Dict] = None) -> str:
    """Build a deterministic prompt for Qwen to generate a single file.

    Args:
        file_blueprint: Single entry from build_plan["files"] with keys
            path, type, purpose.
        project_rules: Output from rules_engine.build_project_rules().

    Returns:
        A prompt string instructing Qwen to generate the file.
    """
    file_path = file_blueprint.get("path", "unknown")
    file_purpose = file_blueprint.get("purpose", "")
    file_type = file_blueprint.get("type", "")

    backend_fw = project_rules.get("backend_framework", "Unknown")
    frontend_fw = project_rules.get("frontend_framework", "Unknown")
    database = project_rules.get("database", "Unknown")
    auth_method = project_rules.get("auth_method", "Unknown")

    lines = [
        "You are a code generation assistant. Generate the content for a single file.",
        "",
        "Context:",
        f"- Backend framework: {backend_fw}",
        f"- Frontend framework: {frontend_fw}",
        f"- Database: {database}",
        f"- Auth method: {auth_method}",
        f"- Required backend modules: {', '.join(str(m) for m in project_rules.get('required_backend_modules', [])) or 'none'}",
        f"- Required frontend pages: {', '.join(str(p) for p in project_rules.get('required_pages', [])) or 'none'}",
        f"- Auth enabled: {'yes' if auth_is_enabled(auth_method) else 'no'}",
        "",
        "File to generate:",
        f"- Path: {file_path}",
        f"- Purpose: {file_purpose}",
        f"- Type: {file_type}",
        "",
        "Instructions:",
        "- Return only the raw source code.",
        "- Do NOT wrap the code in markdown code blocks.",
        "- Do NOT include any explanations, commentary, or natural language.",
        "- Generate only the requested file \u2014 do not suggest or create additional files.",
        "- The code must be complete, functional, and follow best practices.",
    ]

    lines.extend(build_prompt_constraints(project_rules, [file_blueprint]))

    # Dependency export information — tell the LLM what each dependency provides
    if all_blueprints:
        bp_by_path = {bp["path"]: bp for bp in all_blueprints}
        deps = file_blueprint.get("depends_on", [])
        if deps:
            lines.append("")
            lines.append("Dependency exports (import only what is listed below):")
            for dep_path in deps:
                dep_bp = bp_by_path.get(dep_path)
                if dep_bp:
                    provides = dep_bp.get("provides", [])
                    if provides:
                        lines.append(f"- {dep_path} exports: {', '.join(provides)}")
                    else:
                        lines.append(f"- {dep_path}: {dep_bp.get('purpose', 'no purpose declared')}")
                else:
                    lines.append(f"- {dep_path}")

    # Frontend page import path — prevent repair loop from mangling to ../../
    if file_path.startswith("frontend/src/pages/"):
        lines.append("")
        lines.append("Frontend page file instructions:")
        lines.append("- This file is located at frontend/src/pages/")
        lines.append("- The api service is at frontend/src/services/api.js")
        lines.append("- Import api using exactly: import api from '../services/api'")
        lines.append("- Never use ../../services/api or any other path variation")

    # Spec-based deterministic instructions (replaces generic blocks for route files)
    spec = file_blueprint.get("spec")
    has_spec = bool(spec)
    if has_spec:
        lines.append("")
        lines.append("File contract (generate exactly what is specified below):")
        lines.extend(_serialize_spec(spec))

    # Seed file instructions — seeds/ is one level deep, config/models are under backend/src/
    if file_path.startswith("seeds/"):
        db_val = (database or "").strip().lower()
        is_mongo = "mongo" in db_val
        modules = project_rules.get("required_backend_modules", [])
        lines.append("- All require() paths must start with ../ — from seeds/, backend config is at ../backend/src/config/database and backend models are at ../backend/src/models/")
        if is_mongo:
            lines.append("- Import mongoose directly: const mongoose = require('mongoose')")
            lines.append("- Import the database connection: const connectDB = require('../backend/src/config/database')")
            lines.append("- Call connectDB() to connect first, then use model.create() to insert sample documents for each model, then call mongoose.connection.close() to disconnect")
        else:
            lines.append("- Import the database Pool: const pool = require('../backend/src/config/database')")
            lines.append("- Use pool.query() to insert sample data for each model, then call pool.end() to disconnect")
        for mod in modules:
            lines.append(f"- Import the {mod} model: const {mod.capitalize()} = require('../backend/src/models/{mod}')")

    if not has_spec:
        if backend_fw.lower() == "express.js" and database.lower() == "postgresql":
            lines.append("- Database: Use raw SQL with the `pg` library (Pool). Do NOT generate Sequelize, mongoose, or any ORM code.")
            lines.append("- All model files must be plain JS modules that export helper functions using pg.Pool queries.")
            lines.append("- Never import from sequelize. Never call sequelize.define or sequelize.sync.")
            lines.append("- When importing the database Pool, use: const pool = require('../config/database'). Do NOT destructure it.")
            lines.append("- All local require() paths must start with ./ or ../ — never use bare paths like 'config/database'.")
            lines.append("- Route files must export the router as: module.exports = router")
            lines.append("- Route files must be imported with a bare require, not destructured and not using .router property access. Example: const router = require('./routeFile')")
            lines.append("- backend/src/config/database.js must export as: module.exports = pool")
            lines.append("- When importing the database connection in route files, always use a bare require: const pool = require('../config/database') — do NOT destructure")
            lines.append("- The database import variable in route files MUST be named \"pool\", not \"connectDB\" or \"db\"")

    if file_path == "frontend/src/pages/Login.jsx":
        lines.append("- Import useState from 'react', useNavigate from 'react-router-dom', and api from '../services/api'")
        lines.append("- On form submit, call api.post('/auth/login', { email, password }) — use 'email' as the field name, not 'username'")
        lines.append("- On success, save the token: localStorage.setItem('token', response.data.token); then navigate to '/' using navigate('/')")
        lines.append("- On error, display the error message to the user")
        lines.append("- Export the component as default")

    if not has_spec:
        if file_path.startswith("backend/src/routes/") and file_type == "module" and "express" in backend_fw.lower():
            lines.append("- Import express, create a router with express.Router(), import the model from '../models/<name>'")
            lines.append("- Import authenticateToken from '../middleware/auth' and apply it with router.use(authenticateToken) before any route definitions")
            lines.append("- Define GET /stats before GET /:id — stats returns { count: <number> }")
            lines.append("- Define GET / to list all documents (use Model.find()), GET /:id to find one, POST / to create, PUT /:id to update, DELETE /:id to delete using findByIdAndDelete")
            lines.append("- Export the router as module.exports = router")

    if file_path == "backend/src/middleware/auth.js":
        lines.append("- Import jsonwebtoken as jwt")
        lines.append("- Export a function named authenticateToken (not 'auth' or any other name)")
        lines.append("- The function signature is (req, res, next) — read req.header('Authorization'), split 'Bearer ', verify with jwt.verify(token, process.env.JWT_SECRET)")
        lines.append("- Set req.user = decoded (the decoded payload) and call next()")
        lines.append("- Do NOT import any database connection file — this middleware only needs jsonwebtoken")
        lines.append("- On missing or invalid token, return 401")

    if not has_spec:
        if file_path == "backend/src/routes/auth.js":
            lines.append("- Import express.Router(), the User model from '../models/users', bcrypt, and jsonwebtoken")
            lines.append("- Use process.env.JWT_SECRET for jwt.sign — do NOT hardcode a secret")
            lines.append("- The User model has a pre-save hook that hashes passwords — do NOT hash the password before creating the user. Pass the plain password in req.body and let the model hash it.")
            lines.append("- Accept email and password (not username) for login")
            lines.append("- On login, find user by email, compare password with bcrypt.compare, sign JWT and return { token }")
            lines.append("- On register, create a new User with the plain password from req.body, save it, sign JWT and return { token }")
            lines.append("- Export the router as module.exports = router")

    if not has_spec:
        if database.lower() == "mongodb":
            if ("express" in backend_fw.lower() or "node" in backend_fw.lower()) and file_path.startswith("backend/"):
                lines.append("- Database: Use Mongoose (MongoDB ODM). Do NOT generate pg, pg.Pool, SQLAlchemy, Sequelize, or raw SQL code.")
                lines.append("- All model files must be Mongoose schemas that define a mongoose.Schema and export a mongoose.model.")
                lines.append("- Never import from pg, sequelize, or any SQL/ORM library.")
                lines.append("- When importing the database connection in app.js, use: const connectDB = require('./config/database'). Route and model files must NEVER import connectDB.")
                lines.append("- All local require() paths must start with ./ or ../ — never use bare paths like 'config/database'.")
                lines.append("- Route files must export the router as: module.exports = router")
                lines.append("- Route files must be imported with a bare require, not destructured and not using .router property access. Example: const router = require('./routeFile')")
                lines.append("- backend/src/config/database.js must export as: module.exports = connectDB")
                lines.append("- When importing models in route files, use: const ModelName = require('../models/modelName')")
                lines.append("- Every module route file MUST include a GET /stats route defined BEFORE the GET /:id route. The /stats route returns an object with a count field (e.g. { count: 42 }). The dashboard always calls /api/{module}/stats.")
                lines.append("- Never use .remove() on a Mongoose document. Always use Model.findByIdAndDelete(id) to delete documents.")
                lines.append("- When a model schema references another model by ObjectId, use ref and call .populate() on the field in list queries so the frontend receives the full referenced document.")
                lines.append("- connectDB() must only be imported and called in backend/src/app.js. Route files must NOT import or call connectDB().")
                lines.append("- Every module route file must import authenticateToken from '../middleware/auth' and apply it with router.use(authenticateToken). Do NOT apply authentication middleware globally in app.js.")
                lines.append("- Frontend page files must import from '../services/api' using a relative path from frontend/src/pages/ to frontend/src/services/.")
                lines.append("- After successful login or register, navigate to '/' (dashboard root), not '/dashboard'.")
            elif "fastapi" in backend_fw.lower() or "python" in backend_fw.lower():
                lines.append("- Database: Use Motor (async MongoDB driver for FastAPI). Do NOT generate SQLAlchemy, psycopg2, or raw SQL code.")
                lines.append("- All model files must be Pydantic-compatible document models using Motor collection operations.")
                lines.append("- Never import from sqlalchemy, psycopg2, or any SQL library.")
                lines.append("- When importing the database connection, use: from app.db.database import db.")
                lines.append("- app/core/config.py must define a Settings class that inherits from BaseSettings (pydantic_settings). Never use plain constants or os.environ directly. Export a settings = Settings() instance.")
                lines.append("- app/main.py must include a uvicorn.run() call inside if __name__ == '__main__': at the end of the file. Do not omit this block.")

    if (
        file_path == "backend/src/models/users.js"
        and auth_is_enabled(auth_method)
        and "mongo" in (database or "").lower()
    ):
        lines.append("")
        lines.append("Critical file requirements:")
        lines.append("- User model MUST have a pre('save') hook that hashes password with bcrypt before saving. Use bcrypt.hash(this.password, 10). Only hash if this.isModified('password').")
        lines.append("- User model fields must be: email, password, name (not username)")

    if file_path == "backend/src/app.js":
        lines.append("")
        lines.append("Critical file requirements:")
        if "mongo" in (database or "").lower():
            lines.append("- connectDB() MUST be called before app.listen(). Use: connectDB().then(() => app.listen(PORT, () => console.log(...)))")
        if auth_is_enabled(auth_method):
            lines.append("- Do NOT apply auth middleware globally in app.js. Auth is applied per-router inside each route file already.")

    if file_path == "frontend/src/services/api.js":
        lines.append("")
        lines.append("Critical file requirements:")
        lines.append("- Create an axios instance with baseURL from import.meta.env.VITE_API_BASE_URL")
        lines.append("- Read token INSIDE the interceptor function, not at import time: const token = localStorage.getItem('token')")
        lines.append("- Add a request interceptor using api.interceptors.request.use() that reads the token from localStorage.getItem('token') and sets config.headers.Authorization to 'Bearer ' + token if token exists")
        lines.append("- Add a response interceptor using api.interceptors.response.use() that on 401 clears localStorage and redirects: window.location.href = '/login'")
        lines.append("- Do NOT set default headers outside the interceptor — use the interceptor so token changes are picked up after login")
        lines.append("- Export the axios instance as default")

    if file_path == "frontend/src/App.jsx":
        lines.append("")
        lines.append("Critical file requirements:")
        lines.append("- Import BrowserRouter, Routes, Route, Navigate, Link, Outlet from 'react-router-dom'")
        lines.append("- Never use <a href> for internal links — always use <Link to=''> from react-router-dom")
        lines.append("- Create PrivateRoute component that checks localStorage for token, redirects to /login if not found")
        lines.append("- Define PrivateRoute to check localStorage.getItem('token') — if falsy, render <Navigate to='/login' replace />; otherwise render <Outlet />")
        lines.append("- Wrap all non-auth routes with PrivateRoute")
        lines.append("- Mount the following routes: Login at /login (public), Register at /register (public), Dashboard at / (protected, wrapped in PrivateRoute), and any additional pages as /<page-name> (protected, wrapped in PrivateRoute)")
        lines.append("- Include a navigation bar: if token exists in localStorage show Dashboard and Logout links; if no token show Login and Home links")
        lines.append("- Logout must clear localStorage and redirect to /login")
        lines.append("- Export the App component as default")

    return "\n".join(lines)

