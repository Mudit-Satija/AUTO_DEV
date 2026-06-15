"""Shared prompt constraints derived from project_rules and build plan files.

No auth constraints. All constraints are SRS-driven and tech-stack-aware.
"""

from typing import List, Optional


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

    return lines


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
    route_files = [p for p in paths if "/routes/" in p or "/routers/" in p]
    model_files = [p for p in paths if "/models/" in p]
    page_files = [p for p in paths if "/pages/" in p or "/views/" in p]

    has_frontend = bool(page_files) and ("react" in frontend_fw or "vue" in frontend_fw)
    is_frontend_only = backend_fw in ("", "none", "frontend only")
    has_backend_project = not is_frontend_only and bool(backend_fw)

    lines = [
        f"- Required backend modules from SRS entities: {_csv(modules)}.",
        f"- Required frontend pages from SRS: {_csv(pages)}.",
        "- Treat the listed files/build plan as the single source of truth.",
        "- Never import, mount, document, or call modules, routes, models, pages, middleware, services, or database clients that are not implied by the build plan and listed file paths.",
    ]

    # ── ENTITY FIELD NAMES (use exact fields from SRS) ──
    srs = project_rules.get("srs", {})
    entities = srs.get("entities", []) or []
    if entities:
        lines.append("")
        lines.append("### ENTITY FIELD NAMES — use these exact field names in all code:")
        for e in entities:
            name = e.get("name", "")
            fields = e.get("fields", [])
            if name and fields:
                lines.append(f"  - {name}: {', '.join(fields)}")

    if route_files:
        lines.append(f"- Route/router files allowed in this prompt: {_csv(route_files)}.")
    if model_files:
        lines.append(f"- Model files allowed in this prompt: {_csv(model_files)}.")
    if page_files:
        lines.append(f"- Page/view files allowed in this prompt: {_csv(page_files)}.")

    for bp in file_blueprints or []:
        deps = [str(dep) for dep in bp.get("depends_on", [])]
        if deps:
            lines.append(f"- {bp.get('path', 'unknown')} may import only these local build-plan dependencies: {_csv(deps)}.")

        # For frontend-only pages: tell the LLM exactly what props App.jsx passes
        bp_path = bp.get("path", "")
        if is_frontend_only and "/pages/" in bp_path:
            source_entity = (bp.get("source_entity") or "").strip()
            source_page = (bp.get("source_page") or "").strip()
            if source_entity:
                entity_names = [e.strip() for e in source_entity.split(";") if e.strip()]
                prop_names = [e[0].lower() + e[1:] + "s" for e in entity_names]
                setter_names = ["set" + e + "s" for e in entity_names]
                props_str = ", ".join(f"{p}, {s}" for p, s in zip(prop_names, setter_names))
                comp_name = source_page.replace(" ", "") if source_page else "PageName"
                lines.append(f"- CRITICAL — App.jsx passes these EXACT props to {bp_path}: {{ {props_str} }}")
                lines.append(f"  Function signature MUST be: function {comp_name}({{ {props_str} }})")
                lines.append("  Do NOT use useState for entity data — use the props directly.")
                lines.append("  Use crypto.randomUUID() for every new item's id field.")
                lines.append("  If your JSX uses <Link>, <NavLink>, or <Navigate>, you MUST import it from 'react-router-dom'.")

    # For App.jsx/tsx bundles in frontend-only projects: route-to-props mapping
    if is_frontend_only:
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
                    bp_entity = (bp.get("source_entity") or "").strip()
                    bp_page = (bp.get("source_page") or "").strip()
                    if bp_entity:
                        e_names = [e.strip() for e in bp_entity.split(";") if e.strip()]
                        p_names = [e[0].lower() + e[1:] + "s" for e in e_names]
                        s_names = ["set" + e + "s" for e in e_names]
                        props_str = ", ".join(f"{p}, {s}" for p, s in zip(p_names, s_names))
                        comp_name = bp_page.replace(" ", "") if bp_page else "Page"
                        route_lines.append(f"  - {comp_name} expects: {{{props_str}}}")
            if len(route_lines) > 2:  # header + at least one page
                lines.extend(route_lines)

    if db_kind == "mongo":
        lines.append("- Database is MongoDB: use MongoDB/Mongoose for Express or Motor for FastAPI. Do not generate pg, pg.Pool, PostgreSQL SQL, SQLAlchemy, Sequelize, Prisma, CREATE TABLE, or INSERT INTO code.")
        if model_files:
            lines.append("- Model files depend on database.js for mongoose — import with: const mongoose = require(\"mongoose\"). Do NOT import from config/database.")
    elif db_kind == "sql":
        lines.append("- Database is SQL: use pg.Pool/raw SQL for Express/PostgreSQL or SQLAlchemy for FastAPI SQL. Do not generate MongoDB, mongoose, Motor, or document-schema code.")

    if "express" in backend_fw or "node" in backend_fw:
        if "package.json" in paths:
            lines.append("- package.json scripts must use src/app.js for start/dev because server.js and src/index.js are not listed files.")
        lines.append("- Express route aggregation must import and mount exactly the module route files listed by depends_on.")
        lines.append("- Express app.js must mount routes/index.js under /api, call connectDB before app.listen for MongoDB, and must not create a separate server.js unless server.js is listed.")
    if "fastapi" in backend_fw or "python" in backend_fw:
        lines.append("- FastAPI imports must use the app package paths that correspond to listed files; do not import routers, schemas, models, or services that are not listed.")
    if "react" in frontend_fw or "next" in frontend_fw:
        is_ts = "typescript" in frontend_fw or "ts" in frontend_fw
        ext = "tsx" if is_ts else "jsx"
        lines.append(f"- React/Vite files must import only listed src/pages/*.{ext} files. Never use React.X properties (like React.Fragment) — use named imports from 'react' (useState, useEffect, Fragment, etc.) or default import 'import React from \"react\"' if you must access React.X.")
        if is_ts:
            lines.append("- Since the project uses TypeScript, all generated code in .ts and .tsx files must be fully typed (e.g. define interfaces/types for all state variables like useState<Task[]>([]), specify parameter and return types for functions). Avoid implicit 'any' types.")
        lines.append("- In import statements, do NOT append file extensions (.js, .jsx, .ts, .tsx) to local imports. Vite resolves them automatically. Use './App' not './App.jsx'.")
    if "vue" in frontend_fw:
        lines.append("- Vue/Vite files must use Vue conventions, src/router/index.js, and listed src/views/*.vue files. Do not generate React JSX or React Router imports.")

    if len(pages) > 1:
        if "react" in frontend_fw or "next" in frontend_fw:
            lines.append("- Since there are multiple pages, App.tsx/App.jsx must render a visible navigation header/bar (e.g. using Link from 'react-router-dom') to allow navigating to all pages (Dashboard, Tasks, etc.).")
        elif "vue" in frontend_fw:
            lines.append("- Since there are multiple pages, App.vue must render a visible navigation header/bar (e.g. using RouterLink) to allow navigating to all views (Dashboard, Tasks, etc.).")

    # ── CSS COORDINATION (frontend-only and full-stack) ──
    if has_frontend:
        lines.extend([
            "",
            "### CSS COORDINATION RULES — these are CRITICAL for the app to render properly:",
            "- App.css is imported ONLY by App.jsx. No page file may import any CSS file.",
            "- CRITICAL: App.css must define ALL classes from the CSS CLASS REFERENCE below. Do not skip any.",
            "- CRITICAL: Every className in every page .jsx file MUST come ONLY from the CSS CLASS REFERENCE below. Do not invent new class names.",
            "- Use CSS custom properties (variables) in :root for a cohesive color palette, spacing, border-radius, and shadows.",
            "- Use modern CSS: flexbox, grid, gap, border-radius, box-shadow, transitions, responsive media queries (768px breakpoint).",
            "- The app must look polished and modern — cohesive palette, proper typography, consistent spacing, hover/focus states.",
        ])

    # ── VISUAL DESIGN QUALITY ──
    if has_frontend:
        lines.extend([
            "",
            "### VISUAL DESIGN STANDARDS:",
            "- Every page must have a proper layout with a page header/title, content sections, and consistent spacing.",
            "- Use cards/panels to group related content. Cards should have background, border-radius, shadow, and padding.",
            "- Navigation bar must be sticky at the top with a dark/semi-transparent background, horizontal link layout, and hover states.",
            "- Buttons must have clear hover effects, proper padding, and consistent styling.",
            "- Forms and inputs must have proper labels, padding, border styles, focus rings, and validation styling.",
            "- Empty states must show a helpful message and a call-to-action button/link.",
            "- Stats/metrics must be displayed in a responsive grid of cards with clear labels, large values, and optional icons.",
            "- Lists and tables must have proper spacing, alternating row colors, and clear headers.",
            "- Use subtle transitions and hover effects throughout for a polished feel.",
            "- The overall design should look like a modern SaaS application — not a bare prototype.",
        ])

    # ── SEED DATA for localStorage-based apps ──
    if has_frontend and is_frontend_only:
        lines.extend([
            "",
            "### SEED DATA REQUIREMENT (frontend-only, localStorage-based):",
            "- On first visit, localStorage will be empty. The app MUST include seed/initial data so the user sees meaningful content immediately.",
            "- In App.jsx or a separate seed file, define realistic sample data for each entity and write it to localStorage on first load.",
            "- Seed data should be realistic and demonstrate the app's features (e.g., sample goals, contests, submissions, achievements).",
            "- After seeding, the Dashboard and other pages must display this data beautifully — not as empty states.",
            "- Use a pattern like: if (!localStorage.getItem('contests')) { localStorage.setItem('contests', JSON.stringify([...sampleData])); }",
            "- Place the seeding logic in a useEffect in App.jsx that runs once on mount.",
        ])
    elif has_frontend and has_backend_project:
        lines.extend([
            "",
            "### BACKEND API INTEGRATION — CRITICAL: pages MUST call the backend, NEVER use mock data:",
            "- CRITICAL: The FIRST import in every page file MUST be: import api from '../services/api'",
            "- CRITICAL: DO NOT use fetch() directly. Use the imported api (axios instance) for all HTTP calls.",
            "- CRITICAL: DO NOT hardcode mock/sample/demo data arrays in any page component. All data must come from the backend API.",
            "- CRITICAL: DO NOT use localStorage for entity data when a backend exists. localStorage is only for auth tokens or UI preferences.",
            "- The EXACT pattern for fetching data: const [data, setData] = useState([]); useEffect(() => { api.get('/products').then(res => setData(res.data)).catch(err => setError(err.message)); }, []);",
            "- The EXACT pattern for mutations: api.post('/products', body).then(() => { navigate('/products'); })",
            "- Show loading state while fetching (e.g. return <div>Loading...</div> if loading is true).",
            "- Handle API errors gracefully with user-friendly error messages.",
            "- If the API returns empty data, show a helpful empty state with a button/link to the add form.",
        ])

    # ── PAGE-SPECIFIC LAYOUT GUIDANCE ──
    if has_frontend:
        lines.extend([
            "",
            "### PAGE LAYOUT GUIDELINES (generate based on the page type and SRS):",
            "- Dashboard: show a stats grid at the top (4 key metrics in cards), then recent activity list/feed, then upcoming items (contests, deadlines). Use the .stats-grid, .stat-card, .recent-activity CSS classes.",
            "- Analytics/Stats pages: show metric cards with values, then simple visualizations (you can use div-based progress bars, colored bars, or simple SVG charts — no external chart library needed), then breakdown sections. Use .metric-card, .chart-container, .breakdown-section CSS classes.",
            "- List/Management pages (Goals, Tasks, etc.): show an add form at top, then a stats summary row, then a grid/list of items with edit/delete actions. Use .management-form, .stats-summary, .items-grid CSS classes.",
            "- Calendar/Schedule pages: show month navigation, day headers, and a grid of days with items displayed inside. Use .calendar-nav, .calendar-grid, .day-cell, .day-number, .day-item CSS classes.",
            "- Profile/Settings pages: show user info card at top, stats row, then editable form sections. Use .profile-header, .profile-stats, .settings-section CSS classes.",
            "- Leaderboard/Ranking pages: show a table with rank, name, score columns. Use .leaderboard-table, .rank-badge CSS classes.",
        ])

    # ── DATA FLOW AND STATE ──
    lines.extend([
        "",
        "- For any entity that appears on multiple pages (like 'Task' appearing on both Dashboard and Tasks pages), a single source of truth must exist.",
    ])
    if is_frontend_only:
        lines.extend([
            "- In frontend-only projects with no backend/database, this single source of truth must be a shared localStorage key (e.g., 'tasks') or a unified React/Vue Context/state store. Pages like Dashboard and Tasks must read from/write to the exact same localStorage key or state store.",
            "- All localStorage reads and writes for entity data MUST be done inside useEffect hooks or handler functions, NOT in the component render body. Reading localStorage during render causes stale data and breaks React's rendering model.",
            "- Never read localStorage in the component function body. Always use useState + useEffect: initialize state with the correct default (empty array), then read from localStorage inside useEffect and call the setter.",
            "- Statistics and analytics pages must retrieve and compute metrics dynamically from this shared live entity collection. If the retrieved collection is empty, display a beautiful empty state with a button or a react-router-dom Link component to redirect the user to the management page (e.g., Tasks page) to add items.",
        ])
    else:
        lines.extend([
            "- This project has a backend — the single source of truth is the backend API, NOT localStorage.",
            "- Every page must fetch data from the backend on mount and never use localStorage for entity data.",
        ])

    # ── CSS CLASS REFERENCE + KNOWLEDGE BASE ──
    # All bundles embed FULL knowledge file content (no summaries) for rich context.
    if bundle_type == "frontend":
        if is_frontend_only:
            # For frontend-only projects, the complete working example in KNOWLEDGE
            # section below is the primary reference — skip verbose CSS boilerplate
            lines.append("")
            lines.append("### CSS — Use className values matching the patterns in the COMPLETE WORKING EXAMPLE below")
        else:
            lines.append("")
            lines.append("### REFERENCE — CSS classes, page layouts, and design conventions:")
            lines.extend(_summarize_knowledge({}))

    knowledge = project_rules.get("knowledge", {})
    if isinstance(knowledge, dict) and bundle_type in knowledge:
        bundle_knowledge = knowledge.get(bundle_type, [])
    elif isinstance(knowledge, dict) and bundle_type == "backend":
        bundle_knowledge = []
    elif isinstance(knowledge, dict):
        bundle_knowledge = knowledge.get("ui", []) + knowledge.get("patterns", []) + knowledge.get("architecture", [])
    else:
        bundle_knowledge = []
    if bundle_knowledge:
        lines.append("")
        lines.append(f"### KNOWLEDGE — {bundle_type} reference files:")
        for entry in bundle_knowledge:
            lines.append(f"\n--- {entry.get('file', 'unknown')} ---")
            lines.append(entry.get("content", ""))

    # ── FEW-SHOT EXAMPLES (for known Llama-3.1-8B issues) ──
    if bundle_type == "frontend":
        lines.extend([
            "",
            "### FEW-SHOT EXAMPLES — follow these patterns exactly:",
            "",
            "React Router v6 imports (CORRECT — useNavigate, Link, NOT useHistory):",
            "import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';",
            'const navigate = useNavigate();',
            '// ...',
            "navigate('/recipes');",
            "",
            "NOTE: useHistory and history.push are React Router v5 — DO NOT USE. This project uses v6.",
            "",
            "Output format (CORRECT — raw code, no markdown fences):",
            "Start your response with the first line of actual code (e.g. 'import React...').",
            "Do NOT wrap in ```jsx or ``` markdown fences.",
            "",
            "For page files: Do NOT add 'import ... from \"../App.css\"' or any CSS import.",
            "Styling is handled globally in App.css, not per-page.",
        ])

        if is_frontend_only:
            lines.extend([
                "",
                "### DATA ACCESS PATTERN (frontend-only — NO backend API):",
                "- CRITICAL: This project has NO backend API. Do NOT import '../services/api' or use api.get/post/put/delete.",
                "- CRITICAL: Do NOT add 'import api from \"../services/api\"' to any file.",
                "- CRITICAL: Do NOT use fetch() or axios. All data comes from localStorage via App.jsx.",
                "- All entity data must be managed through App.jsx props and localStorage.",
                "- Example CORRECT pattern for page components:",
                "  const Recipes = ({ recipes, setRecipes }) => {",
                "    const navigate = useNavigate();",
                '    return <div className="app-wrapper">...;',
                '  };',
                "- Pages receive data as props from App.jsx; they do NOT fetch or import data themselves.",
            ])
        else:
            lines.extend([
                "",
                "### DATA ACCESS PATTERN (full-stack — backend API):",
                "- The FIRST import in every page file MUST be: import api from '../services/api'",
                "- DO NOT use fetch() directly. Use the imported api (axios instance) for all HTTP calls.",
                "- DO NOT hardcode mock/sample/demo data arrays. All data comes from the backend API.",
            ])

    return lines
