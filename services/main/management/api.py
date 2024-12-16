from core.logger import logger
from services.main.communication.service import CommunicationService
from services.main.management.classifier import classify_intent
from services.main.management.service import ManagementService
from services.main.communication.models import MessageRequest
managementService = ManagementService()
communicationService = CommunicationService()

async def handle_message(request: MessageRequest):
    # Step 1: Use the classifier to detect the intent
    intent = await classify_intent(request.message, request.chat_history)
    logger.debug(f"Detected intent: {intent}")
    # Step 2: Route the message based on the detected intent
    if intent == "Deployment Request":
        # Extract the user's raw prompt
        dep_plan =  await managementService.generate_deployment_plan(request)
        return dep_plan

    elif intent == "Other":
        # Extract feedback content
        return managementService.process_feedback(request)

    else:  # Handle unknown intent
        return {"status": "success", "response": "I'm sorry, I didn't understand that. Can you clarify?"}
