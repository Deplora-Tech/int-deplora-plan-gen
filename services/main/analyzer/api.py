from fastapi import APIRouter, HTTPException, BackgroundTasks
from git import Repo
from pydantic import BaseModel
from uuid import uuid4
from core.database import db
from services.main.analyzer.service import AnalyzerService
import os

router = APIRouter()

# Pydantic model for the client request
class AnalyzeRequest(BaseModel):
    repo_url: str
    client_id: str
    repo_id: str

# Background task for running the analyzer
from core.config import settings

async def run_analyzer_task(session_id: str, client_id: str, repo_id: str, repo_url: str):
    analyzer_service = AnalyzerService()

    # Fetch paths from environment variables
    described_template_path = settings.DESCRIBED_TEMPLATE_PATH
    empty_template_path = settings.INIT_TEMPLATE_PATH

    # Clone the repository and proceed as before
    repo_path = f"/tmp/{repo_id}"
    try:
        if not os.path.exists(repo_path):
            # ask Sahiru about this
            Repo.clone_from(repo_url, repo_path)
            print(f"Repository cloned to: {repo_path}")

        # Run the analyzer process
        generated_template = await analyzer_service.process_files_and_update_template(
            repo_path=repo_path,
            described_template_path=described_template_path,
            empty_template_path=empty_template_path,
        )

        # Store result in MongoDB
        db_entry = {
            "session_id": session_id,
            "client_id": client_id,
            "repo_id": repo_id,
            "generated_template": generated_template,
        }
        await db.db["analysis_results"].insert_one(db_entry)
        print(f"Analysis result stored in database for session_id: {session_id}")

    except Exception as e:
        print(f"Error during analysis: {e}")

# API endpoint to start the analysis
@router.post("/analyze")
async def analyze_repository(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    # Create a unique session ID
    session_id = str(uuid4())

    # Simulate repository path (you can replace this with actual cloning logic)
    repo_path = f"/tmp/{request.repo_id}"  # Example path to the cloned repository

    # Add the analysis task to the background
    background_tasks.add_task(
        run_analyzer_task,
        session_id=session_id,
        client_id=request.client_id,
        repo_id=request.repo_id,
        repo_path=repo_path,
    )

    return {"message": "Analysis started", "session_id": session_id}
