from core.logger import logger
from services.main.communication.service import CommunicationService
from services.main.enums import LoraStatus
from services.main.management.classifier import classify_intent
from services.main.management.service import ManagementService
from services.main.communication.models import MessageRequest
from services.main.utils.caching.redis_service import SessionDataHandler
managementService = ManagementService()

async def handle_message(request: MessageRequest, communcationService: CommunicationService):
    # Step 1: Use the classifier to detect the intent
    chat_history = SessionDataHandler.get_chat_history(request.session_id, request.client_id)
    print("chat_history:", chat_history)
    SessionDataHandler.store_message(request.session_id, request.client_id, "user", request.message)

    intent = await classify_intent(request.message, chat_history)
    await communcationService.publisher(request.client_id, LoraStatus.INTENT_DETECTED.value)
    logger.debug(f"Detected intent: {intent}")
    # Step 2: Route the message based on the detected intent
    if "Deployment" in intent:
        dep_plan =  await managementService.generate_deployment_plan(
            prompt=request.message,
            project_id=request.project_id,
            organization_id=request.organization_id,
            user_id=request.client_id,
            chat_history=chat_history,
            session_id=request.session_id,
            communication_service=communcationService
        )
        SessionDataHandler.store_message(request.session_id, request.client_id,"You", dep_plan["response"])
        return dep_plan

    elif "Other" in intent:
        res =  await managementService.process_conversation(request, chat_history)
        SessionDataHandler.store_message(request.session_id, request.client_id,"You", res["response"])
        return res

    else:  # Handle unknown intent
        logger.debug("Unknown intent")
        return {"status": "success", "response": "I'm sorry, I didn't understand that. Can you clarify?"}
