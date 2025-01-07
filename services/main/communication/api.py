from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core.logger import logger
from services.main.communication.models import MessageRequest
from services.main.communication.service import CommunicationService
from services.main.enums import LoraStatus
from services.main.management.api import handle_message

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

        return {"status": "Message sent", "processed_message": message}

    except Exception as e:
        return {"status": "Error", "message": str(e)}
