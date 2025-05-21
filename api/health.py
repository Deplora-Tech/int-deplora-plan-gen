"""
Health check endpoints for the application.
"""

from fastapi import APIRouter, HTTPException
from core.database import mongodb, ping_database
from core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check():

    return {"status": "ok", "service": "int-deplora-plan-gen", "version": "1.0.0"}


@router.get("/health/db")
async def db_health_check():

    try:
        db_reachable = await ping_database()

        if not db_reachable:
            logger.error("Database health check failed - could not ping database")
            raise HTTPException(status_code=503, detail="Database not reachable")

        await mongodb.connect()
        count = await mongodb.analysis_results.count_documents({})

        return {
            "status": "ok",
            "database": settings.MONGO_DB_NAME,
            "collections": {"analysis_results": {"count": count}},
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Database connection failed")
