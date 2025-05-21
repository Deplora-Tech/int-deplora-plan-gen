from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
import logging
import nest_asyncio
from services.main.analyzer.api import run_analyzer_task, get_projects_by_user_id
from services.main.analyzer.models import AnalyzeRequest
from fastapi.responses import JSONResponse
import requests


nest_asyncio.apply()
router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze")
async def analyze_repository(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    print(request)
    try:
        background_tasks.add_task(
            run_analyzer_task,
            client_id=request.client_id,
            project_id=request.project_id,
            repo_url=request.repo_url,
            branch=request.branch,
        )
        logger.info(f"Analysis task queued for client_id={request.client_id}, project_id={request.project_id}")
        return {"message": "Analysis task started successfully"}
    except Exception as e:
        logger.error(f"Failed to queue analysis task: {e}")
        raise HTTPException(status_code=500, detail="Failed to queue analysis task")
    
@router.get("/branches")
async def get_github_branches(repo_url: str = Query(..., description="GitHub repository URL")):
    try:
        # Extract owner and repo name from the URL
        parts = repo_url.rstrip('/').split('/')
        if len(parts) < 2:
            raise ValueError("Invalid GitHub repository URL format.")
            
        
        owner, repo = parts[-2], parts[-1].replace('.git', '')
        api_url = f"https://api.github.com/repos/{owner}/{repo}/branches"

        print(api_url)

        response = requests.get(api_url)
        response.raise_for_status()

        branches = [branch["name"] for branch in response.json()]
        return JSONResponse(content={"branches": branches}, status_code=200)

    except requests.HTTPError as http_err:
        return JSONResponse(
            content={"error": "Failed to connect", "details": str(http_err)},
            status_code=response.status_code
        )
        

    except Exception as e:
        return JSONResponse(
            content={"error": "An error occurred", "details": str(e)},
            status_code=500
        )
    

@router.get("/projects")
async def get_projects(client_id: str = Query(..., description="Client ID")):
    try:
        # Assuming you have a function to fetch projects from the database
        projects = await get_projects_by_user_id(client_id)
        return JSONResponse(content={"projects": projects}, status_code=200)
    except Exception as e:
        return JSONResponse(
            content={"error": "An error occurred", "details": str(e)},
            status_code=500
        )