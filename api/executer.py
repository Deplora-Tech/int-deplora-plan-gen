from fastapi import (
    APIRouter,
)
from services.main.communication.service import CommunicationService
from services.main.excecutor.service import excecute_pipeline

router = APIRouter()
communication_service = CommunicationService("ChatService")
pipeline_communication_service = CommunicationService("PipelineService")


@router.get("/excecute/{session_id}")
async def execute(session_id: str):
    k = await excecute_pipeline(session_id)
    return k
