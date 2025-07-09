from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    UploadFile,
    File,
    HTTPException,
)
import base64
from services.main.enums import GraphStatus
from services.main.communication.service import CommunicationService
from core.logger import logger
from services.main.communication.service import CommunicationService

router = APIRouter()
communication_service = CommunicationService("ChatService")
pipeline_communication_service = CommunicationService("PipelineService")


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
                "content_type": "image/png",
                "image_data": encoded_image,
            },
        )

        return {"message": "Image received successfully for session_id: " + session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
