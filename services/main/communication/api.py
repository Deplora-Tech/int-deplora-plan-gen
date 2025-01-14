from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core.logger import logger
from services.main.communication.models import MessageRequest
from services.main.communication.service import CommunicationService
from services.main.enums import LoraStatus
from services.main.management.api import handle_message
from services.main.utils.caching.redis_service import SessionDataHandler
from services.main.excecutor.service import excecute_pipeline


router = APIRouter()
communication_service = CommunicationService()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await communication_service.connect(websocket, client_id)
    try:
        await communication_service.publisher(client_id, f"Welcome!")
        while True:
            message = await websocket.receive_text()
            response = f"Received: {message}"
            await communication_service.publisher(client_id, response)

    except WebSocketDisconnect:
        communication_service.disconnect(client_id)

@router.post("/send-message")
async def send_message(request: MessageRequest):
    try:
        message = await handle_message(request, communication_service)
        await communication_service.publisher(request.client_id, LoraStatus.COMPLETED.value)
        
        print("Message:", message)

        return {"status": "Message sent", "processed_message": message}

    except Exception as e:
        print("Error", e)
        return {"status": "Error", "processed_message": {"response": "An error occurred. Please try again."}}


@router.get("/get_chat_history/{session_id}")
async def get_chat_history(session_id: str):
    chat_history = SessionDataHandler.get_chat_history(session_id)
    return chat_history


@router.get("/excecute/{session_id}")
async def execute(session_id: str):
    excecute_pipeline(session_id)