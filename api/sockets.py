from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)
from services.main.communication.service import CommunicationService

router = APIRouter()
communication_service = CommunicationService("ChatService")
pipeline_communication_service = CommunicationService("PipelineService")


@router.websocket("/pipeline-ws/{session_id}")
async def pipeline_websocket_endpoint(websocket: WebSocket, session_id: str):
    await pipeline_communication_service.connect(websocket, session_id)
    try:
        while True:
            message = await websocket.receive_text()
            response = f"Received: {message}"
            await pipeline_communication_service.publisher(
                session_id, "Response", response
            )

    except WebSocketDisconnect:
        pipeline_communication_service.disconnect(session_id)


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await communication_service.connect(websocket, session_id)
    try:
        await communication_service.publisher(
            session_id, "Connected", "You are now connected."
        )
        while True:
            message = await websocket.receive_text()
            response = f"Received: {message}"
            await communication_service.publisher(session_id, "Response", response)

    except WebSocketDisconnect:
        communication_service.disconnect(session_id)
