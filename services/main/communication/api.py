from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core.logger import logger
from services.main.communication.models import MessageRequest
from services.main.communication.service import CommunicationService
from services.main.management.api import handle_message
router = APIRouter()
service = CommunicationService()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await service.connect(websocket, client_id)
    try:
        await service.publisher(client_id, f"Welcome!")
        while True:
            message = await websocket.receive_text()
            response = f"Received: {message}"
            await service.publisher(client_id, response)

    except WebSocketDisconnect:
        service.disconnect(client_id)

@router.post("/send-message")
async def send_message(request: MessageRequest):
    message = await handle_message(request)
    logger.debug(message)
    await service.publisher(request.client_id, message)
    return {"status": "Message sent", "processed_message": message}