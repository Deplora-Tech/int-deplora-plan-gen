from fastapi import (
    APIRouter,
)
from core.logger import logger
from services.main.communication.models import MessageRequest
from services.main.communication.service import CommunicationService
from services.main.enums import LoraStatus
from services.main.management.api import handle_message
from services.main.utils.caching.redis_service import SessionDataHandler

router = APIRouter()
communication_service = CommunicationService("ChatService")
pipeline_communication_service = CommunicationService("PipelineService")


@router.post("/send-message")
async def send_message(request: MessageRequest):
    try:
        logger.info(f"Received message: {request.message}")
        message = await handle_message(request, communication_service)
        await communication_service.publisher(
            request.session_id,
            LoraStatus.COMPLETED.value,
        )

        return {"status": "Message sent", "processed_message": message}

    except Exception as e:
        print("Error", e)
        await communication_service.publisher(
            request.session_id,
            LoraStatus.FAILED.value,
        )

        return {
            "status": "Error",
            "processed_message": {"response": "An error occurred. Please try again."},
        }


@router.get("/get-chat-history/{session_id}")
async def get_chat_history(session_id: str):
    chat_history = SessionDataHandler.get_chat_history(session_id)
    return chat_history
