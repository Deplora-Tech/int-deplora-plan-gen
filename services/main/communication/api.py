from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.main.communication.models import MessageRequest
from services.main.communication.process_request import process_request
from services.main.communication.service import CommunicationService
from services.main.management.api import handle_message
router = APIRouter()
service = CommunicationService()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    # Connect the client
    await service.connect(websocket, client_id)
    try:
        # Send a welcome message to the connected client
        await service.publisher(client_id, f"Welcome!")
        while True:
            message = await websocket.receive_text()
            response = f"Received: {message}"
            await service.publisher(client_id, response)

    except WebSocketDisconnect:
        # Remove the client on disconnect
        service.disconnect(client_id)

@router.post("/send-message")
async def send_message(request: MessageRequest):
    message = await process_request(request)
    print(message)
    await service.publisher(request.client_id, message)
    return {"status": "Message sent", "processed_message": message}