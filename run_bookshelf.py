"""Generate BookShelf for local dev server."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coding_agent.build_plan import generate_build_plan
from coding_agent.rules_engine import build_project_rules
from knowledge_retriever import retrieve_knowledge
from coding_agent.project_generator import generate_project

srs = {
    "project_name": "BookShelf",
    "project_description": "A personal book collection and reading tracker",
    "complexity": "medium",
    "tech_stack": {"frontend": "React", "backend": "none", "database": "none"},
    "pages": [
        {"name": "Books", "entities": ["Book"]},
        {"name": "Add Book", "entities": ["Book"]},
        {"name": "Reading List", "entities": ["ReadingEntry", "Book"]},
        {"name": "Dashboard", "entities": ["Book", "ReadingEntry"]},
    ],
    "entities": [
        {"name": "Book", "fields": ["id", "title", "author", "genre", "totalPages", "dateAdded"]},
        {"name": "ReadingEntry", "fields": ["id", "bookId", "status", "dateAdded"]},
    ],
    "flow": [
        {"name": "Add Book", "entities": ["Book"]},
        {"name": "View Books", "entities": ["Book"]},
        {"name": "Manage Reading List", "entities": ["ReadingEntry", "Book"]},
        {"name": "View Dashboard", "entities": ["Book", "ReadingEntry"]},
    ],
    "roles": [],
    "requirements": [],
}
output_dir = f"generated_projects/BookShelf_{int(time.time())}"
project_rules = build_project_rules(srs, srs["tech_stack"])
knowledge = retrieve_knowledge(srs)
project_rules["knowledge"] = knowledge
build_plan = generate_build_plan(project_rules)
result = generate_project(build_plan, project_rules, output_dir)
print(f"OUTPUT_DIR={os.path.abspath(output_dir + '/frontend')}")
print(f"VALIDATIONS={result['all_validations_pass']}")
print(f"FILES={result['files_generated']}")
