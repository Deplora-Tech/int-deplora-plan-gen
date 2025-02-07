from fastapi import APIRouter, HTTPException, BackgroundTasks
import logging
import nest_asyncio
from services.main.analyzer.api import run_analyzer_task
from services.main.analyzer.models import AnalyzeRequest


nest_asyncio.apply()
router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze")
async def analyze_repository(
    request: AnalyzeRequest, background_tasks: BackgroundTasks
):
    try:
        # Add the task to background processing
        background_tasks.add_task(
            run_analyzer_task,
            client_id=request.client_id,
            project_id=request.project_id,
            repo_url=request.repo_url,
        )
        logger.info(
            f"Analysis task queued for client_id={request.client_id}, project_id={request.project_id}"
        )
        return {"message": "Analysis task started successfully"}
    except Exception as e:
        logger.error(f"Failed to queue analysis task: {e}")
        raise HTTPException(status_code=500, detail="Failed to queue analysis task")
