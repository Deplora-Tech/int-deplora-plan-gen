from fastapi import APIRouter, HTTPException, BackgroundTasks
import logging
import nest_asyncio
from services.main.analyzer.api import run_analyzer_task, get_generated_template
from services.main.analyzer.models import AnalyzeRequest
from fastapi.responses import JSONResponse

nest_asyncio.apply()
router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze")
async def analyze_repository(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(
            run_analyzer_task,
            client_id=request.client_id,
            project_id=request.project_id,
            repo_url=request.repo_url,
        )
        logger.info(f"Analysis task queued for client_id={request.client_id}, project_id={request.project_id}")
        return {"message": "Analysis task started successfully"}
    except Exception as e:
        logger.error(f"Failed to queue analysis task: {e}")
        raise HTTPException(status_code=500, detail="Failed to queue analysis task")

# @router.get("/template/{project_id}")
# async def fetch_generated_template(project_id: str):
#     import inspect
#     logging.info(f"Is coroutine function? {inspect.iscoroutinefunction(get_generated_template)}")
#
#     try:
#         # Just for debug, call without await and see what happens
#         coro = get_generated_template(project_id)
#         logging.info(f"Type of coro: {type(coro)}")
#         # Now await properly
#         template = await coro
#         return JSONResponse(content=template)
#     except ValueError as ve:
#         raise HTTPException(status_code=404, detail=str(ve))
#     except Exception as e:
#         logging.error(f"Internal error fetching template: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")
