from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    File,
    UploadFile,
    HTTPException,
)
import base64
from core.logger import logger
from services.main.communication.models import MessageRequest
from services.main.communication.service import CommunicationService
from services.main.enums import LoraStatus
from services.main.management.api import handle_message
from services.main.utils.caching.redis_service import SessionDataHandler
from services.main.excecutor.service import excecute_pipeline
import requests
import os
from services.main.enums import GraphStatus

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
            await pipeline_communication_service.publisher(session_id, "Response", response)

    except WebSocketDisconnect:
        pipeline_communication_service.disconnect(session_id)


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await communication_service.connect(websocket, client_id)
    try:
        await communication_service.publisher(
            client_id, "Connected", "You are now connected."
        )
        while True:
            message = await websocket.receive_text()
            response = f"Received: {message}"
            await communication_service.publisher(client_id, "Response", response)

    except WebSocketDisconnect:
        communication_service.disconnect(client_id)


@router.post("/send-message")
async def send_message(request: MessageRequest):
    try:
        message = await handle_message(request, communication_service)
        await communication_service.publisher(
            request.client_id,
            LoraStatus.COMPLETED.value,
        )

        return {"status": "Message sent", "processed_message": message}

    except Exception as e:
        print("Error", e)
        return {
            "status": "Error",
            "processed_message": {"response": "An error occurred. Please try again."},
        }


@router.get("/get-chat-history/{session_id}")
async def get_chat_history(session_id: str):
    chat_history = SessionDataHandler.get_chat_history(session_id)
    return chat_history


@router.get("/excecute/{session_id}")
async def execute(session_id: str):
    k = await excecute_pipeline(session_id)
    return k


@router.post("/generate-graph/{session_id}")
async def generate_graph(session_id: str, file_contents: dict):
    res = await requests.post(
        os.environ.get("GRAPH_GENERATOR_URL"),
        json={"id": session_id, "files": file_contents},
    )


@router.post("/upload-image/{session_id}")
async def upload_image(session_id: str, file: UploadFile = File(...)):
    try:
        logger.info(f"Received image for session_id: {session_id}")
        file_content = await file.read()
        encoded_image = base64.b64encode(file_content).decode("utf-8")

        await communication_service.publisher(
            session_id,
            GraphStatus.COMPLETED.value,
            {
                "filename": file.filename,
                "content_type": file.content_type,
                "image_data": encoded_image,  # Base64 encoded image
            },
        )
        return {"message": "Image received successfully for session_id: " + session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
