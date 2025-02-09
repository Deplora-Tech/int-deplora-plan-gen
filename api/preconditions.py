from fastapi import (
    APIRouter,
)
from core.logger import logger
from services.main.communication.models import PreConditionRequest
from services.main.enums import Preconndition
from services.main.utils.caching.redis_service import SessionDataHandler
from services.main.precondition.service import TestCoverageService

router = APIRouter()


@router.post("/test-coverage")
async def test_coverage(request: PreConditionRequest):
    return await handle_precondition(request, Preconndition.TEST_COVERAGE)


@router.post("/code-quality")
async def code_quality(request: PreConditionRequest):
    return await handle_precondition(request, Preconndition.CODE_QUALITY)


@router.post("/build-status")
async def build_status(request: PreConditionRequest):
    return await handle_precondition(request, Preconndition.BUILD_STATUS)


async def handle_precondition(request: PreConditionRequest, condition: Preconndition):
    try:
        session_id = request.session_id
        redis_data = SessionDataHandler.get_preconditions(session_id, condition)

        if redis_data:
            return {
                "status": "Success",
                "processed_message": redis_data,
            }

        if condition == Preconndition.TEST_COVERAGE:
            service = TestCoverageService(root_path="D:\\repos")
            result = service.analyze_repo(
                "https://github.com/Deplora-Tech/test.git",
                session_id,
                language="Python",
            )
        elif condition == Preconndition.CODE_QUALITY:
            # service = CodeQualityService(root_path="D:\\repos")

            pass
        elif condition == Preconndition.BUILD_STATUS:
            # service = BuildStatusService(root_path="D:\\repos")
            pass
        else:
            raise HTTPException(status_code=400, detail="Invalid precondition type")

        return {"status": "Message sent", "processed_message": result}

    except Exception as e:
        logger.error("Error handling request", exc_info=True)

        return {
            "status": "Error",
            "processed_message": {"response": "An error occurred. Please try again."},
        }
