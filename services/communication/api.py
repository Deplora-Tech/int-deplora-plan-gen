# app/services/communication/api.py
from fastapi import APIRouter, WebSocket
from .service import CommunicationService

router = APIRouter()
service = CommunicationService()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await service.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            response = await service.process_message(message)
            await websocket.send_text(response)
    except Exception as e:
        service.disconnect(websocket)
