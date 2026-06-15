from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from llm_client import get_llm_response
from coding_agent.project_generator import generate_project
from coding_agent.build_plan import generate_build_plan
from coding_agent.rules_engine import build_project_rules
from coding_agent.metrics import get_metrics_collector, reset_metrics_collector
from knowledge_retriever import retrieve_knowledge
import logging
import os
import time
import zipfile
import json
from pathlib import Path

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="AUTO_DEV Generation System",
    description="SRS-driven project generation with knowledge retrieval",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/generate-from-srs")
async def generate_from_srs(request: dict) -> dict:
    """Generate project from flat SRS fields with knowledge retrieval.

    Expects flat JSON:
    {
        "project_name": "StudyHub",
        "complexity": "medium",
        "frontend_framework": "React",
        "pages": ["Dashboard", "Courses"],
        "entities": ["Course", "Assignment"],
        "flow": ["Create Course", "Edit Course"]
    }
    """
    try:
        project_name = request.get("project_name", "Untitled")
        complexity = request.get("complexity", "intermediate")
        backend_framework = request.get("backend_framework", "").strip().lower()
        frontend_framework = request.get("frontend_framework", "React")

        pages_raw = request.get("pages", []) or []
        entities_raw = request.get("entities", []) or []
        flow_raw = request.get("flow", []) or []

        # Detect frontend-only mode
        is_frontend_only = backend_framework in ("", "none", "frontend only")

        # Convert string[] -> object format for downstream pipeline
        pages = []
        for p in pages_raw:
            if isinstance(p, str) and p.strip():
                pages.append({"name": p.strip(), "purpose": "", "entities": []})
            elif isinstance(p, dict):
                pages.append(p)

        entities = []
        for e in entities_raw:
            if isinstance(e, str) and e.strip():
                entities.append({"name": e.strip(), "fields": ["name", "description", "createdAt"], "description": ""})
            elif isinstance(e, dict):
                entities.append(e)

        flow = []
        for f in flow_raw:
            if isinstance(f, str) and f.strip():
                flow.append({"name": f.strip(), "steps": [], "entities": []})
            elif isinstance(f, dict):
                flow.append(f)

        if is_frontend_only:
            page_names = [p.get("name", "") if isinstance(p, dict) else str(p) for p in pages_raw]
            srs = {
                "project_name": project_name,
                "project_description": "",
                "complexity": complexity,
                "pages": pages,
                "flow": flow,
                "entities": entities,
                "roles": [],
                "tech_stack": {"frontend": frontend_framework},
                "requirements": [],
            }
            project_rules = {
                "backend_framework": "none",
                "frontend_framework": frontend_framework,
                "database": "none",
                "auth_method": "",
                "required_backend_modules": [],
                "required_pages": page_names,
                "srs": srs,
            }
        else:
            tech_stack = {
                "backend": backend_framework if backend_framework else "Express.js",
                "frontend": frontend_framework,
                "database": "MongoDB",
            }
            srs = {
                "project_name": project_name,
                "project_description": "",
                "complexity": complexity,
                "pages": pages,
                "flow": flow,
                "entities": entities,
                "roles": [],
                "tech_stack": tech_stack,
                "requirements": [],
            }
            project_rules = build_project_rules(srs, tech_stack)

        logger.info(
            "SRS generation: project=%s pages=%d entities=%d flows=%d backend=%s",
            srs["project_name"],
            len(srs["pages"]),
            len(srs["entities"]),
            len(srs["flow"]),
            project_rules.get("backend_framework", "none"),
        )

        # 1. Knowledge retrieval
        knowledge = retrieve_knowledge(srs)
        knowledge_summary = {k: len(v) for k, v in knowledge.items() if v}
        logger.info(
            "Knowledge retrieved: %s",
            knowledge_summary,
        )

        # 2. Attach knowledge to project_rules for the coding agent
        project_rules["knowledge"] = knowledge

        # 4. Generate build plan
        build_plan = generate_build_plan(project_rules)

        # 5. Generate project files
        timestamp = int(time.time())
        output_dir = f"generated_outputs/project_{timestamp}"

        reset_metrics_collector()
        result = generate_project(build_plan, project_rules, output_dir, max_repair_attempts=0)

        # 6. Create zip
        zip_start = time.perf_counter()
        zip_filename = f"project_{timestamp}.zip"
        zip_path = os.path.join("generated_outputs", zip_filename)
        os.makedirs("generated_outputs", exist_ok=True)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root_dir, _, files in os.walk(output_dir):
                for fname in files:
                    fpath = os.path.join(root_dir, fname)
                    arcname = os.path.relpath(fpath, output_dir)
                    zf.write(fpath, arcname)
        zip_duration_ms = int((time.perf_counter() - zip_start) * 1000)

        metrics = get_metrics_collector()
        metrics.record_zip_time(zip_duration_ms)

        metrics_summary = metrics.get_summary()
        metrics_file = f"generated_outputs/metrics_{timestamp}.json"
        metrics.save_to_file(metrics_file)

        logger.info(
            "Generation complete: %d files, %s, knowledge=%s",
            result["files_generated"],
            zip_filename,
            knowledge_summary,
        )
        logger.info(
            "Pipeline metrics: bundles=%d, total_gen_time_ms=%d, validation_time_ms=%d, zip_time_ms=%d",
            metrics_summary["pipeline_metrics"]["total_bundles"],
            metrics_summary["pipeline_metrics"]["total_generation_time_ms"],
            metrics_summary["pipeline_metrics"]["validation_time_ms"],
            metrics_summary["pipeline_metrics"]["zip_creation_time_ms"],
        )

        return {
            "files_generated": result["files_generated"],
            "knowledge_retrieved": knowledge_summary,
            "zip_filename": zip_filename,
            "all_validations_pass": result.get("all_validations_pass", True),
            "metrics": metrics_summary,
            "metrics_file": metrics_file,
        }

    except Exception as e:
        logger.error("SRS generation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"SRS generation failed: {str(e)}")


@app.get("/download/{filename}")
async def download_file(filename: str):
    for candidate in ["generated_outputs", "generated_output", "."]:
        base = Path(candidate)
        if base.is_dir():
            fpath = base / filename
            if fpath.is_file():
                return FileResponse(str(fpath), filename=filename)
    raise HTTPException(status_code=404, detail=f"File {filename} not found")


@app.get("/info")
async def model_info():
    return {
        "version": "2.0.0",
        "generation_model": "qwen/qwen3-next-80b-a3b-instruct",
        "pipeline": "SRS -> Knowledge Retrieval -> Build Plan -> Code Generation",
        "knowledge_sources": {
            "architecture": 4,
            "ui": 5,
            "patterns": 7,
        },
    }


@app.get("/metrics/{filename}")
async def get_metrics(filename: str):
    for candidate in ["generated_outputs", "generated_output", "."]:
        base = Path(candidate)
        if base.is_dir():
            fpath = base / filename
            if fpath.is_file():
                return FileResponse(str(fpath), filename=filename)
    raise HTTPException(status_code=404, detail=f"Metrics file {filename} not found")


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
