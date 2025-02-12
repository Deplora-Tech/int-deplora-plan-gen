import asyncio
from fastapi import APIRouter, HTTPException
from services.main.excecutor.service import excecute_pipeline, abort_pipeline

router = APIRouter()


@router.post("/execute/{session_id}")
async def execute(session_id: str):

    asyncio.create_task(excecute_pipeline(session_id))

    return {"status": "Pipeline execution started", "session_id": session_id}

@router.post("/abort/{session_id}/{build_id}")
async def abort(session_id: str, build_id: str):

    await abort_pipeline(session_id, build_id)
    return {"status": "Pipeline aborted", "session_id": session_id, "build_id": build_id}

