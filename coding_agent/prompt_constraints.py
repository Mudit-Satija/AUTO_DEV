"""Shared prompt constraints derived from project_rules and build plan files.

No auth constraints. All constraints are SRS-driven and tech-stack-aware.
"""

from typing import List, Optional

from coding_agent.naming import entity_prop_name, entity_setter_name


def database_kind(database: str) -> str:
    val = (database or "").strip().lower()
    if "mongo" in val:
        return "mongo"
    if "postgres" in val or "mysql" in val or "sql" in val:
        return "sql"
    return "unknown"


def _csv(values: List[str]) -> str:
    return ", ".join(values) if values else "none"


# ── CSS CLASS REFERENCE ──
# These are the ONLY CSS classes that pages should use.
# App.css MUST define rules for ALL of these classes.
# Every className in every .jsx file must come from this list.
_CSS_CLASSES = [
    # Layout
    ".app-wrapper", ".page-header", ".page-header h1", ".page-header p",
    ".section", ".section h2", ".section-header",
    # Stats grid
    ".stats-grid", ".stat-card", ".stat-card h3", ".stat-value",
    # Content cards
    ".card", ".card-header", ".card-content", ".card-footer",
    # Items / lists
    ".items-grid", ".item-card", ".item-title", ".item-details", ".item-actions",
    ".activity-feed", ".activity-item", ".activity-title", ".activity-meta",
    ".upcoming-list", ".upcoming-item", ".upcoming-title", ".upcoming-meta",
    # Forms
    ".form-card", ".form-group", ".form-label", ".form-input", ".form-select",
    ".form-row", ".form-actions", ".form-textarea",
    # Buttons
    ".btn", ".btn-primary", ".btn-secondary", ".btn-danger", ".btn-sm",
    # Tables
    ".table-wrapper", ".data-table", ".data-table th", ".data-table td",
    # Badges / status
    ".badge", ".badge-success", ".badge-warning", ".badge-danger", ".badge-info",
    # Empty state
    ".empty-state", ".empty-state p", ".empty-state .btn",
    # Nav
    ".navbar", ".navbar-brand", ".nav-links", ".nav-link", ".nav-link.active",
    # Calendar
    ".calendar-header", ".calendar-nav", ".calendar-grid", ".day-header",
    ".day-cell", ".day-number", ".day-event",
    # Profile
    ".profile-header", ".profile-avatar", ".profile-info", ".profile-stats",
    ".settings-section", ".settings-row",
    # Leaderboard
    ".leaderboard-table", ".rank-badge", ".leaderboard-row",
]

# ── PAGE LAYOUT TEMPLATES ──
# Standard layout structure for each page type.
# Pages MUST use these CSS classes in the exact structure shown.
_PAGE_LAYOUTS = {
    "dashboard": """
  <div className="app-wrapper">
    <div className="page-header">
      <h1>Dashboard</h1>
    </div>
    <div className="stats-grid">
      <div className="stat-card"><h3>Metric 1</h3><p className="stat-value">0</p></div>
      <div className="stat-card"><h3>Metric 2</h3><p className="stat-value">0</p></div>
      <div className="stat-card"><h3>Metric 3</h3><p className="stat-value">0</p></div>
      <div className="stat-card"><h3>Metric 4</h3><p className="stat-value">0</p></div>
    </div>
    <div className="section"><h2>Recent Activity</h2>
      <div className="activity-feed">{/* map items */}</div>
    </div>
    <div className="section"><h2>Upcoming</h2>
      <div className="upcoming-list">{/* map items */}</div>
    </div>
  </div>""",
    "management": """
  <div className="app-wrapper">
    <div className="page-header"><h1>Page Title</h1></div>
    <div className="form-card">{/* add form */}</div>
    <div className="stats-grid">{/* summary stats */}</div>
    <div className="section"><h2>List Title</h2>
      <div className="items-grid">{/* map items */}</div>
    </div>
  </div>""",
    "analytics": """
  <div className="app-wrapper">
    <div className="page-header"><h1>Analytics</h1></div>
    <div className="stats-grid">{/* metric cards */}</div>
    <div className="section"><h2>Breakdown</h2>{/* charts/bars */}</div>
  </div>""",
    "calendar": """
  <div className="app-wrapper">
    <div className="page-header"><h1>Calendar</h1></div>
    <div className="calendar-header">
      <button className="btn">{'<'}</button>
      <h2>Month Year</h2>
      <button className="btn">{'>'}</button>
    </div>
    <div className="calendar-grid">
      <div className="day-header">Sun</div>...
      <div className="day-cell"><span className="day-number">1</span><div className="day-event">Event</div></div>...
    </div>
  </div>""",
    "profile": """
  <div className="app-wrapper">
    <div className="profile-header">
      <div className="profile-avatar"><img /></div>
      <div className="profile-info"><h2>Name</h2><p>email</p></div>
    </div>
    <div className="profile-stats">{/* stat cards */}</div>
    <div className="settings-section">{/* forms */}</div>
  </div>""",
    "leaderboard": """
  <div className="app-wrapper">
    <div className="page-header"><h1>Leaderboard</h1></div>
    <div className="table-wrapper">
      <table className="leaderboard-table">
        <thead><tr><th>Rank</th><th>Name</th><th>Score</th></tr></thead>
        <tbody>{/* rows */}</tbody>
      </table>
    </div>
  </div>""",
}

_CSS_CLASS_LIST = ", ".join(_CSS_CLASSES)


def _summarize_knowledge(knowledge: dict) -> List[str]:
    lines = []

    # Always include CSS class reference and layout templates when called
    lines.append("")
    lines.append("### CSS CLASS REFERENCE — use ONLY these class names in ALL files")
    lines.append(f"Available classes: {_CSS_CLASS_LIST}")
    lines.append("")
    lines.append("### PAGE LAYOUT TEMPLATES — follow these exact className patterns per page type")
    for ptype, layout in _PAGE_LAYOUTS.items():
        lines.append("")
        lines.append(f"--- {ptype.upper()} LAYOUT ---")
        for line in layout.strip().split("\n"):
            lines.append(line)

def build_prompt_constraints(
    project_rules: dict,
    file_blueprints: Optional[List[dict]] = None,
    bundle_type: str = "frontend",
) -> List[str]:
    backend_fw = (project_rules.get("backend_framework") or "").lower()
    frontend_fw = (project_rules.get("frontend_framework") or "").lower()
    database = project_rules.get("database") or ""
    db_kind = database_kind(database)
    modules = [str(m) for m in project_rules.get("required_backend_modules", [])]
    pages = [str(p) for p in project_rules.get("required_pages", [])]
    paths = [bp.get("path", "") for bp in file_blueprints or []]
    
    is_frontend_only = backend_fw in ("", "none", "frontend only")
    
    lines = [
        "- Treat the listed files/build plan as the single source of truth.",
        "- Never import, mount, document, or call modules, routes, models, pages, middleware, services, or database clients that are not implied by the build plan and listed file paths.",
    ]
    
    # Entity field names — must be impossible to abbreviate
    srs = project_rules.get("srs", {})
    entities = srs.get("entities", []) or []
    if entities and bundle_type in ("frontend", "backend", "database"):
        lines.append("")
        lines.append("### ENTITY OBJECT SHAPES — copy these exact key names character-for-character:")
        for e in entities:
            name = e.get("name", "")
            fields = e.get("fields", [])
            if name and fields:
                lines.append(f"  - {name} — every object MUST have exactly this shape (do NOT abbreviate or use single-letter keys):")
                lines.append("    {")
                for f in fields:
                    lines.append(f"      {f}: ...,")
                lines.append("    }")
        if bundle_type == "frontend":
            lines.append("")
            lines.append("### VARIABLE NAMING RULE:")
            lines.append("- Name every form state variable after the EXACT entity field name from the shape above.")
            lines.append("  Example: field 'author' → const [author, setAuthor] = useState('')")
            lines.append("  Example: field 'dateAdded' → const [dateAdded, setDateAdded] = useState('')")
            lines.append("- Do NOT invent field names that are not listed in ENTITY OBJECT SHAPES above.")

    # 1. FRONTEND CONSTRAINTS
    if bundle_type == "frontend":
        lines.extend([
            f"- Required frontend pages from SRS: {_csv(pages)}.",
            "- In import statements, do NOT append file extensions (.js, .jsx, .ts, .tsx) to local imports. Vite resolves them automatically. Use './App' not './App.jsx'.",
            "- DO NOT import or use sub-components (like Form, List, Card, Modal, etc.) from other files. Write all helper components, forms, and dialogs INLINE inside the same file.",
            "- NEVER import components, forms, helper functions, page files, or anything else from other page files in the 'src/pages' directory (e.g., do NOT import Budget from './Budget'). All helper components must be defined inline within the same file.",
            "- CRITICAL: Do NOT add Update/Edit buttons that use navigate() or <Link to> with a dynamic ID segment (e.g. `/tasks/123`, `/books/abc`). There are NO dynamic routes like `/tasks/:id`. Every route is a static path listed in App.jsx. Use inline toggle/delete on the same page instead of navigating to an edit page.",
            "- CRITICAL: Do NOT use navigate() to go to any path that is not listed in App.jsx's routing table. Only the exact paths from the nav links are valid."
        ])
        
        # CSS classes and visual standards
        css_classes = "app-wrapper, page-header, section, form-card, form-group, form-label, form-input, form-select, form-actions, navbar, navbar-brand, nav-links, nav-link, btn, btn-primary, btn-secondary, btn-danger, btn-sm, empty-state, account-card, account-name, account-balance, account-type, account-details, account-number, account-actions, transaction-card, transaction-type, transaction-amount, transaction-date, transaction-details, transaction-title, transaction-actions, transaction-category, transaction-status, items-grid, item-card, item-title, item-details, item-actions, stats-grid, stat-card, stat-title, stat-details, transfers-grid, transfer-card, transfer-title, transfer-details, transfer-status, accounts-grid, error-message, activity-item, activity-title, activity-date, recent-activity, upcoming-items, upcoming-item, upcoming-title, upcoming-date, section-header, page-wrapper"
        lines.append("")
        lines.append("### AVAILABLE CSS CLASSES — use only these in className string literals (e.g. className=\"btn btn-primary\"):")
        lines.append("```css")
        for cls in css_classes.split(", "):
            lines.append(f".{cls} {{}}")
        lines.append("```")
        
        lines.extend([
            "",
            "### CSS COORDINATION & VISUAL STANDARDS:",
            "- App.css is imported ONLY by App.jsx. No page file may import ANY CSS file under any circumstances. Page files MUST NOT contain any import statement referencing a '.css' file (e.g., do NOT import './styles.css' or './App.css').",
            "- CSS files DO NOT export variables, styles, class names, or components. NEVER import React components, styles, variables, or class names from 'App.css' or any other CSS file (e.g., do NOT do: import { section } from './styles.css').",
            "- CSS class names must be written as literal strings in className (e.g., className=\"section\" or className=\"btn btn-primary\"). Do NOT import, define, or reference them as JavaScript variables or tags.",
            "- Use ONLY standard HTML/JSX tags (like div, button, input, label, select, p, h1, span) styled with className (e.g., <div className=\"navbar\">, NOT <Navbar>). Do NOT use PascalCase component tags unless you have defined them locally as standard functions or imported them from 'react-router-dom'.",
            "- CRITICAL: Every className in every page .jsx file MUST come ONLY from the AVAILABLE CSS CLASSES above. Do not invent new class names.",
            "- The app must look polished and modern — dark theme, soft shadows, rounded corners, good spacing, consistent typography, smooth transitions, responsive layouts.",
            "- Do NOT use heavy glassmorphism, excessive blur, excessive gradients, neon effects, or overly flashy animations.",
            "- Forms and inputs must have proper labels, padding, border styles, focus rings.",
            "- Stats/metrics must be displayed in a responsive grid of cards with clear labels, large values.",
        ])
        
        # Prop contracts and page-specific props (for frontend-only)
        if is_frontend_only:
            for bp in file_blueprints or []:
                bp_path = bp.get("path", "")
                if "/pages/" in bp_path:
                    source_entity = (bp.get("source_entity") or "").strip()
                    source_page = (bp.get("source_page") or "").strip()
                    # Prefer spec-stored props (single deterministic computation)
                    spec = bp.get("spec") or {}
                    fp = spec.get("frontend_props")
                    if fp:
                        props_str = fp["destructure"]
                        comp_name = source_page.replace(" ", "") if source_page else "PageName"
                        first_data_prop = props_str.split(",")[0].strip() if props_str else "data"
                        first_setter = props_str.split(",")[1].strip() if "," in props_str else "setData"
                        lines.append(f"- CRITICAL — App.jsx passes these EXACT props to {bp_path}: {{ {props_str} }}")
                        lines.append(f"  Function signature MUST be: function {comp_name}({{ {props_str} }})")
                        lines.append(f"  CRITICAL — The entity for this page is '{bp.get('source_entity', '')}'. The data prop is named '{first_data_prop}' and the setter is named '{first_setter}'. You MUST use these EXACT names. Do NOT substitute a different entity name (e.g. do NOT use 'books' when the entity is 'ReadingEntry').")
                        lines.append("  CRITICAL — Do NOT rename props. App.jsx will pass 'undefined' for any invented name, causing runtime crashes.")
                        lines.append("  Do NOT use useState for entity data — use the props directly.")
                        lines.append("  CRITICAL — Do NOT create independent useState copies of props data. Use props directly for ALL rendering. Compute derived values (totals, counts, filtered lists) from props in the render body, not from duplicate state.")
                        lines.append("  Use crypto.randomUUID() for every new item's id field.")
                        lines.append("  If your JSX uses <Link>, <NavLink>, or <Navigate>, you MUST import it from 'react-router-dom'.")
                    elif source_entity:
                        entity_names = [e.strip() for e in source_entity.split(";") if e.strip()]
                        prop_names = [entity_prop_name(e) for e in entity_names]
                        setter_names = [entity_setter_name(e) for e in entity_names]
                        props_str = ", ".join(f"{p}, {s}" for p, s in zip(prop_names, setter_names))
                        comp_name = source_page.replace(" ", "") if source_page else "PageName"
                        lines.append(f"- CRITICAL — App.jsx passes these EXACT props to {bp_path}: {{ {props_str} }}")
                        lines.append(f"  Function signature MUST be: function {comp_name}({{ {props_str} }})")
                        lines.append(f"  CRITICAL — The entity for this page is '{source_entity}'. The data prop '{prop_names[0] if prop_names else 'data'}' IS the entity data. Use it directly. Do NOT substitute another entity name (e.g. do NOT use 'books' when the entity is 'ReadingEntry').")
                        lines.append("  CRITICAL — Do NOT rename props. App.jsx will pass 'undefined' for any invented name, causing runtime crashes.")
                        lines.append("  Do NOT use useState for entity data — use the props directly.")
                        lines.append("  CRITICAL — Do NOT create independent useState copies of props data. Use props directly for ALL rendering. Compute derived values (totals, counts, filtered lists) from props in the render body, not from duplicate state.")
                        lines.append("  Use crypto.randomUUID() for every new item's id field.")
                        lines.append("  If your JSX uses <Link>, <NavLink>, or <Navigate>, you MUST import it from 'react-router-dom'.")

            # Route-to-props mapping in App.jsx
            is_app_bundle = any("App.jsx" in bp.get("path", "") or "App.tsx" in bp.get("path", "") for bp in file_blueprints or [])
            if is_app_bundle:
                all_files = project_rules.get("all_files", []) or []
                route_lines = [
                    "",
                    "CRITICAL — each page below expects these EXACT props from App.jsx. Do NOT omit any prop:",
                ]
                for bp in all_files:
                    bp_path = bp.get("path", "")
                    if "/pages/" in bp_path:
                        # Use spec-stored props if available (single deterministic computation)
                        spec = bp.get("spec") or {}
                        fp = spec.get("frontend_props")
                        if fp:
                            comp_name = (bp.get("source_page") or "").replace(" ", "") or "Page"
                            route_lines.append(f"  - {comp_name} expects: {{{fp['destructure']}}}")
                        else:
                            bp_entity = (bp.get("source_entity") or "").strip()
                            bp_page = (bp.get("source_page") or "").strip()
                            if bp_entity:
                                e_names = [e.strip() for e in bp_entity.split(";") if e.strip()]
                                p_names = [entity_prop_name(e) for e in e_names]
                                s_names = [entity_setter_name(e) for e in e_names]
                                props_str = ", ".join(f"{p}, {s}" for p, s in zip(p_names, s_names))
                                comp_name = bp_page.replace(" ", "") if bp_page else "Page"
                                route_lines.append(f"  - {comp_name} expects: {{{props_str}}}")
                if len(route_lines) > 2:
                    lines.extend(route_lines)
                lines.append("CRITICAL — Use these EXACT prop variable names when passing props to each page. Do NOT rename them. Every page's destructured parameter names MUST match exactly what you pass in the JSX.")
                # Literal routing table — computed from build plan, LLM must copy verbatim
                routing_table_lines = ["", "### EXACT ROUTES AND NAV LINKS — copy these verbatim, do not add/remove/rename:", ""]
                page_bps = [bp for bp in (file_blueprints or []) if "/pages/" in bp.get("path", "")]
                # Determine the home route page (Dashboard) if present
                home_route = "/"
                home_page_name = None
                # Aggregate all unique entity names across all pages (for Dashboard which has no specific entity)
                all_entity_names = []
                for pbp in page_bps:
                    pn = pbp.get("source_page", "")
                    if pn.lower() == "dashboard":
                        home_page_name = pn
                    entity_str = pbp.get("source_entity", "").strip()
                    if entity_str:
                        for e in entity_str.split(";"):
                            e = e.strip()
                            if e and e not in all_entity_names:
                                all_entity_names.append(e)
                # Build route map dict for JSON block
                route_map = {}  # comp_name -> route
                nav_links = {}  # route -> nav_label
                for pbp in page_bps:
                    page_name = pbp.get("source_page", "")
                    comp_name = page_name.replace(" ", "") if page_name else "Page"
                    route = pbp.get("route_path", "/" + page_name.lower().replace(" ", "-") if page_name else "/")
                    route_map[comp_name] = route
                    nav_label = page_name if page_name else "Page"
                    nav_links[route] = nav_label
                # JSON route map — structured reference the LLM must use for every navigate/link decision
                import json
                route_map_json = json.dumps(route_map, indent=2)
                nav_links_json = json.dumps(nav_links, indent=2)
                routing_table_lines.append("")
                routing_table_lines.append("### ROUTE MAP — use this for ALL navigate() and <Link to> decisions:")
                routing_table_lines.append("```json")
                routing_table_lines.append(f'"pageRoutes": {route_map_json}')
                routing_table_lines.append("")
                routing_table_lines.append(f'"navLinks": {nav_links_json}')
                routing_table_lines.append("```")
                routing_table_lines.append("CRITICAL RULE: Every single call to navigate() and every <Link to='...'> in EVERY file MUST use a path from 'pageRoutes' above.")
                routing_table_lines.append("If the path is not in 'pageRoutes', it does not exist in the router — using it will 404 at runtime.")
                routing_table_lines.append("For example: to navigate to AddTask, use navigate('/add') NOT navigate('/add-task'). To navigate to Tasks, use navigate('/') NOT navigate('/tasks').")
                routing_table_lines.append("Look up the component name in 'pageRoutes' to find the correct path. NEVER guess or infer a path from a component name.")
                routing_table_lines.append("")
                for pbp in page_bps:
                    page_name = pbp.get("source_page", "")
                    comp_name = page_name.replace(" ", "") if page_name else "Page"
                    route = pbp.get("route_path", "/" + page_name.lower().replace(" ", "-") if page_name else "/")
                    # Build JSX prop pairs (key={value} syntax) from entities
                    spec = pbp.get("spec") or {}
                    fp = spec.get("frontend_props")
                    if fp:
                        # destructure is "books, setBooks"; convert to "books={books} setBooks={setBooks}"
                        parts = [p.strip() for p in fp["destructure"].split(",")]
                        jsx_props = " ".join(f"{p}={{{p}}}" for p in parts)
                    else:
                        entity_str = pbp.get("source_entity", "").strip()
                        if entity_str:
                            e_names = [e.strip() for e in entity_str.split(";") if e.strip()]
                            props_parts = []
                            for e in e_names:
                                data_name = entity_prop_name(e)
                                setter_name = entity_setter_name(e)
                                props_parts.append(f"{data_name}={{{data_name}}}")
                                props_parts.append(f"{setter_name}={{{setter_name}}}")
                            jsx_props = " ".join(props_parts)
                        elif all_entity_names:
                            # Page with no entity (like Dashboard) gets all aggregated entities
                            props_parts = []
                            for e in all_entity_names:
                                data_name = entity_prop_name(e)
                                setter_name = entity_setter_name(e)
                                props_parts.append(f"{data_name}={{{data_name}}}")
                                props_parts.append(f"{setter_name}={{{setter_name}}}")
                            jsx_props = " ".join(props_parts)
                        else:
                            jsx_props = "data={data} setData={setData}"
                    nav_label = page_name if page_name else "Page"
                    routing_table_lines.append(f"  <Route path='{route}' element={{<{comp_name} {jsx_props} />}} />")
                    routing_table_lines.append(f"  <Link to='{route}'>{nav_label}</Link>")
                if home_page_name:
                    routing_table_lines.append(f"  (Dashboard at '{home_route}' is the home/index page)")
                routing_table_lines.append("")
                routing_table_lines.append("Do not add, remove, or rename any route or link path. Copy every character exactly as shown above.")
                routing_table_lines.append("CRITICAL CONSTRAINT: Dashboard MUST be at '/'. Do NOT create a separate '/dashboard' route. If you create '<Link to=\"/dashboard\">' or '<Route path=\"/dashboard\">', your output FAILS.")
                routing_table_lines.append("CRITICAL CONSTRAINT: Do NOT add ANY route or nav link beyond what is listed above. If it is not in this table, it does not exist. Do NOT add dynamic routes like '/tasks/:id' or '/books/:id'.")
                lines.extend(routing_table_lines)
            
            lines.extend([
                "",
                "### DATA ACCESS PATTERN (frontend-only — localStorage):",
                "- App.jsx is the SINGLE source of truth for both reading AND writing localStorage.",
                "- Pages MUST NOT read or write localStorage. Pages call setter props (e.g. setBooks). App.jsx persists automatically.",
                "- Do NOT add useEffect in pages for localStorage — that creates TWO sources of truth for the same key.",
                "- Do NOT fetch() or use axios. Do NOT import '../services/api'.",
                "- Seed data: Do NOT generate any sample/seed/starter data. On first visit, if localStorage has no data for an entity, initialize its state to an empty array: setItems([]). Do NOT create any hardcoded example objects. The app should show its empty-state UI (e.g. 'No items yet') until the user adds real data through the forms.",
                "- Read localStorage only inside useEffect, never in the render body.",
            ])
        else:
            lines.extend([
                "",
                "### DATA ACCESS PATTERN (fullstack — backend API):",
                "- All data must be fetched from/written to the backend API via the custom api utility: import api from '../services/api'",
                "- DO NOT use fetch() or direct axios calls. Use the imported api client.",
                "- DO NOT hardcode mock/sample/demo data arrays. Fetch everything on mount.",
                "- DO NOT use localStorage for entity data when a backend exists.",
            ])
            
        # React router v6 few-shot
        lines.extend([
            "",
            "### FEW-SHOT EXAMPLES:",
            "React Router v6 imports (CORRECT — useNavigate, Link, NOT useHistory):",
            "import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';",
            "const navigate = useNavigate();",
            "navigate('/recipes');",
            "",
            "Do NOT wrap in ```jsx or ``` markdown fences.",
            "Do NOT import CSS files in pages; global CSS is in App.css.",
        ])

    # 2. BACKEND CONSTRAINTS
    elif bundle_type == "backend":
        lines.extend([
            f"- Required backend modules from SRS entities: {_csv(modules)}.",
        ])
        if db_kind == "mongo":
            lines.append("- Database is MongoDB: use Mongoose models or Motor. Do not generate SQL code.")
        elif db_kind == "sql":
            lines.append("- Database is SQL: use raw SQL/pg for Node or SQLAlchemy for Python/FastAPI. Do not generate Mongoose or MongoDB code.")
        
        if "express" in backend_fw or "node" in backend_fw:
            lines.extend([
                "",
                "### EXPRESS BACKEND CONVENTIONS:",
                "- Do NOT generate app.js, config, or routes/index.js (these are deterministic).",
                "- Generate ONLY models (in models/) and CRUD routes (in routes/).",
                "- Every routes file must export a router (module.exports = router) containing standard CRUD endpoints.",
                "- Imports should be CommonJS (require / module.exports). Avoid ES modules (import / export).",
                "- To import models, use individual model files (e.g. const Category = require('../models/category')) or the models index (const { Category } = require('../models')).",
                "- You can import config (const config = require('../config')) and errorHandler (const errorHandler = require('../middleware/errorHandler')) if needed.",
                "- Do NOT return mock responses; connect dynamically to the database connector in config/database.js.",
            ])
        elif "fastapi" in backend_fw or "python" in backend_fw:
            lines.extend([
                "",
                "### FASTAPI BACKEND CONVENTIONS:",
                "- Do NOT generate main.py, db/database.py, or core/config.py (these are deterministic).",
                "- Generate ONLY models (models/), pydantic schemas (schemas/), and routers (routers/).",
                "- Routers must define a router (router = APIRouter()) and expose CRUD endpoints.",
                "- Connection to database must use the connection instance in app/db/database.py.",
            ])

    # 3. DATABASE CONSTRAINTS
    elif bundle_type == "database":
        lines.append(f"- Target Database: {database} ({db_kind})")
        if db_kind == "sql":
            lines.extend([
                "",
                "### SQL SCHEMA & SEED RULES:",
                "- Migrations in migrations/001_initial.sql must use CREATE TABLE IF NOT EXISTS.",
                "- Seeds in seeds/seed.sql must use INSERT INTO statements with realistic mock records.",
                "- Define foreign key relationships and matching data types.",
            ])
        elif db_kind == "mongo":
            import_inst = ""
            if "express" in backend_fw or "node" in backend_fw:
                import_inst = "- To import models in seeds/seed.js, require them from '../backend/src/models' (e.g. const { Category, Transaction } = require('../backend/src/models')). Do NOT require from '../src/models' or 'src/models'."
            elif "fastapi" in backend_fw or "python" in backend_fw:
                import_inst = "- To import models in seeds/seed.py, import them from app.models (e.g. from app.models import Category, Transaction)."
            
            lines.extend([
                "",
                "### MONGODB SEED RULES:",
                "- Seeds in seeds/seed.js or seeds/seed.py must insert sample records for all SRS entities.",
                "- Clear collections before inserting (e.g. deleteMany({})).",
                import_inst
            ])

    # 4. DOCS CONSTRAINTS
    elif bundle_type == "docs":
        lines.extend([
            "",
            "### DOCUMENTATION RULES:",
            "- Generate a clear README.md project outline, tech stack description, and installation instructions.",
        ])

    # 5. KNOWLEDGE FILES INJECTION
    knowledge = project_rules.get("knowledge", {})
    if isinstance(knowledge, dict) and bundle_type in knowledge:
        bundle_knowledge = knowledge.get(bundle_type, [])
        if bundle_knowledge:
            lines.append("")
            lines.append(f"### KNOWLEDGE — {bundle_type} reference files:")
            for entry in bundle_knowledge:
                lines.append(f"\n--- {entry.get('file', 'unknown')} ---")
                lines.append(entry.get("content", ""))

    return lines
