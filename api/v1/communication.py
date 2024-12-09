from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.communication_service import CommunicationService

router = APIRouter()
service = CommunicationService()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await service.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            response = await service.process_message(data)
            await websocket.send_text(response)
    except WebSocketDisconnect:
        service.disconnect(websocket)

@router.post("/send-message")
async def send_message(message: str):
    return await service.process_message(message)
