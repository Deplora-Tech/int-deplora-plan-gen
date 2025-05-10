import asyncio
from fastapi import APIRouter, HTTPException
from services.main.excecutor.service import excecute_pipeline, abort_pipeline, get_status

router = APIRouter()


@router.post("/execute/{session_id}")
async def execute(session_id: str):

    build_id = await excecute_pipeline(session_id)

    return {"status": "Pipeline execution started", "session_id": session_id, "build_id": build_id}

@router.post("/abort/{session_id}/{build_id}")
async def abort(session_id: str, build_id: str):

    await abort_pipeline(session_id, build_id)
    return {"status": "Pipeline aborted", "session_id": session_id, "build_id": build_id}

@router.post("/status/{session_id}/{build_id}")
async def status(session_id: str, build_id: str):
    build_info = await get_status(session_id, build_id)
    if build_info is None:
        raise HTTPException(status_code=404, detail="Build not found")
    return build_info

