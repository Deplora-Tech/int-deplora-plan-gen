from core.logger import logger
from services.main.communication.service import CommunicationService
from services.main.enums import LoraStatus
from services.main.management.classifier import classify_intent
from services.main.management.service import ManagementService
from services.main.communication.models import MessageRequest

managementService = ManagementService()

async def handle_message(request: MessageRequest, communcationService: CommunicationService):
    # Step 1: Use the classifier to detect the intent
    intent = await classify_intent(request.message, request.chat_history)
    await communcationService.publisher(request.client_id, LoraStatus.INTENT_DETECTED.value)
    logger.debug(f"Detected intent: {intent}")
    # Step 2: Route the message based on the detected intent
    if intent == "Deployment Request":
        dep_plan =  await managementService.generate_deployment_plan(
            prompt=request.message,
            project_id=request.project_id,
            organization_id=request.organization_id,
            user_id=request.client_id,
            chat_history=request.chat_history,
            session_id=request.session_id,
            communication_service=communcationService
        )
        return dep_plan

    elif intent == "Other":
        return await managementService.process_conversation(request)

    else:  # Handle unknown intent
        return {"status": "success", "response": "I'm sorry, I didn't understand that. Can you clarify?"}
