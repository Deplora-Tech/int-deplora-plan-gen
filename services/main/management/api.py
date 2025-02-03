from core.logger import logger
from services.main.communication.service import CommunicationService
from services.main.enums import LoraStatus
from services.main.management.classifier import classify_intent
from services.main.management.service import ManagementService
from services.main.communication.models import MessageRequest
from services.main.utils.caching.redis_service import SessionDataHandler
from dotenv import load_dotenv
import requests
import os
managementService = ManagementService()

async def handle_message(request: MessageRequest, communcationService: CommunicationService):
    # Step 1: Use the classifier to detect the intent
    chat_history = SessionDataHandler.get_chat_history(request.session_id)
    
    SessionDataHandler.store_message(request.session_id, request.client_id, "user", request.message)
    SessionDataHandler.update_session_data(request.session_id, request)

    intent = await classify_intent(request.message, chat_history)
    logger.info(f"Detected intent: {intent}")
    await communcationService.publisher(request.session_id, LoraStatus.INTENT_DETECTED.value)
    
    # Step 2: Route the message based on the detected intent
    if "Deployment" in intent:
        logger.info("Detected deployment intent")
        dep_plan =  await managementService.generate_deployment_plan(
            prompt=request.message,
            project_id=request.project_id,
            organization_id=request.organization_id,
            user_id=request.client_id,
            chat_history=chat_history,
            session_id=request.session_id,
            communication_service=communcationService
        )
        logger.info("Generated deployment plan")
        SessionDataHandler.store_message(request.session_id, request.client_id,"You", dep_plan["response"])
        SessionDataHandler.store_current_plan(request.session_id, request.client_id, dep_plan["file_contents"])
        
        # Send the files to the graph generator
        logger.info("Sending files to the graph generator")
        load_dotenv()
        requests.post(
            os.environ.get("GRAPH_GENERATOR_URL"),
            json={"id": request.session_id, "files": dep_plan["file_contents"]},
        )

        return dep_plan

    elif "Other" in intent:
        logger.info("Detected other intent")
        res =  await managementService.process_conversation(request, chat_history)
        SessionDataHandler.store_message(request.session_id, request.client_id,"You", res["response"])
        return res

    else:  # Handle unknown intent
        logger.info("Detected unknown intent")
        return {"status": "success", "response": "I'm sorry, I didn't understand that. Can you clarify?"}
