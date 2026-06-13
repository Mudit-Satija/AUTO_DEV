from coding_agent.bundle_generator import group_and_partition_files

files = [
    {"path": "README.md", "bundle": "docs"},
    {"path": "backend/.gitignore", "bundle": "backend"},
    {"path": "backend/.env", "bundle": "backend"},
    {"path": "backend/package.json", "bundle": "backend"},
    {"path": "backend/src/app.js", "bundle": "backend"},
    {"path": "backend/src/config/index.js", "bundle": "backend"},
    {"path": "backend/src/config/database.js", "bundle": "backend"},
    {"path": "backend/src/middleware/errorHandler.js", "bundle": "backend"},
    {"path": "backend/src/routes/index.js", "bundle": "backend"},
    {"path": "backend/src/models/transaction.js", "bundle": "backend"},
    {"path": "backend/src/routes/transaction.js", "bundle": "backend"},
    {"path": "backend/src/models/budget.js", "bundle": "backend"},
    {"path": "backend/src/routes/budget.js", "bundle": "backend"},
    {"path": "backend/src/models/category.js", "bundle": "backend"},
    {"path": "backend/src/routes/category.js", "bundle": "backend"},
    {"path": "frontend/package.json", "bundle": "frontend"},
    {"path": "frontend/.env", "bundle": "frontend"},
    {"path": "frontend/vite.config.js", "bundle": "frontend"},
    {"path": "frontend/index.html", "bundle": "frontend"},
    {"path": "frontend/src/main.jsx", "bundle": "frontend"},
    {"path": "frontend/src/App.jsx", "bundle": "frontend"},
    {"path": "frontend/src/App.css", "bundle": "frontend"},
    {"path": "frontend/src/services/api.js", "bundle": "frontend"},
    {"path": "frontend/src/pages/Dashboard.jsx", "bundle": "frontend"},
    {"path": "frontend/src/pages/Transactions.jsx", "bundle": "frontend"},
    {"path": "frontend/src/pages/Budgets.jsx", "bundle": "frontend"},
    {"path": "frontend/src/pages/Reports.jsx", "bundle": "frontend"},
    {"path": "frontend/src/pages/Analytics.jsx", "bundle": "frontend"},
    {"path": "seeds/seed.js", "bundle": "database"},
]

bundles = group_and_partition_files(files)
print(f"Bundles: {len(bundles)}")
for name, bps in bundles.items():
    print(f"  {name}: {len(bps)} files")
    for bp in bps:
        print(f"    {bp['path']}")