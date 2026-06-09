from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from llm_client import get_llm_response
from coding_agent.project_generator import generate_project
from coding_agent.build_plan import generate_build_plan
from coding_agent.rules_engine import build_project_rules
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
    """Generate project from SRS document with knowledge retrieval.

    Expects JSON matching the SRSDocument schema:
    {
        "project_name": "...",
        "project_description": "...",
        "complexity": "intermediate",
        "pages": [{"name": "...", "purpose": "...", "entities": [...]}],
        "flow": [{"name": "...", "steps": [...], "entities": [...]}],
        "entities": [{"name": "...", "fields": [...], "description": "..."}],
        "roles": [...],
        "tech_stack": {"backend": "Express.js", "frontend": "React", "database": "MongoDB"},
        "requirements": [{"id": "REQ-001", "description": "..."}]
    }

    Returns:
    {
        "files_generated": 22,
        "knowledge_retrieved": {"architecture": 1, "ui": 1, "patterns": 2},
        "zip_filename": "project_123.zip"
    }
    """
    try:
        srs = {
            "project_name": request.get("project_name", "Untitled"),
            "project_description": request.get("project_description", ""),
            "complexity": request.get("complexity", "intermediate"),
            "pages": request.get("pages", []),
            "flow": request.get("flow", []),
            "entities": request.get("entities", []),
            "roles": request.get("roles", []),
            "tech_stack": request.get("tech_stack", {}),
            "requirements": request.get("requirements", []),
        }

        logger.info(
            "SRS generation: project=%s pages=%d entities=%d flows=%d",
            srs["project_name"],
            len(srs["pages"]),
            len(srs["entities"]),
            len(srs["flow"]),
        )

        # 1. Knowledge retrieval
        knowledge = retrieve_knowledge(srs)
        knowledge_summary = {k: len(v) for k, v in knowledge.items() if v}
        logger.info(
            "Knowledge retrieved: %s",
            knowledge_summary,
        )

        # 2. Build project rules from SRS
        tech_stack = srs.get("tech_stack", {})
        project_rules = build_project_rules(srs, tech_stack)

        # 3. Attach knowledge to project_rules for the coding agent
        project_rules["knowledge"] = knowledge

        # 4. Generate build plan
        build_plan = generate_build_plan(project_rules)

        # 5. Generate project files
        timestamp = int(time.time())
        output_dir = f"generated_outputs/project_{timestamp}"
        result = generate_project(build_plan, project_rules, output_dir)

        # 6. Create zip
        zip_filename = f"project_{timestamp}.zip"
        zip_path = os.path.join("generated_outputs", zip_filename)
        os.makedirs("generated_outputs", exist_ok=True)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root_dir, _, files in os.walk(output_dir):
                for fname in files:
                    fpath = os.path.join(root_dir, fname)
                    arcname = os.path.relpath(fpath, output_dir)
                    zf.write(fpath, arcname)

        logger.info(
            "Generation complete: %d files, %s, knowledge=%s",
            result["files_generated"],
            zip_filename,
            knowledge_summary,
        )

        return {
            "files_generated": result["files_generated"],
            "knowledge_retrieved": knowledge_summary,
            "zip_filename": zip_filename,
            "all_validations_pass": result.get("all_validations_pass", True),
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


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
