from core.logger import logger
from services.main.communication.service import CommunicationService
from services.main.management.classifier import ClassifierService
from services.main.management.service import ManagementService

managementService = ManagementService()
classifierService = ClassifierService()
communicationService = CommunicationService()

async def handle_message(client_id: str, project_id: str, message: str, chat_history: dict) -> dict:
    # Step 1: Use the classifier to detect the intent
    intent = classifierService.classify_intent(message, chat_history)
    logger.debug(intent)
    # Step 2: Route the message based on the detected intent
    if intent == "greeting":
        return  {message :"Hello! How can I assist you?"}

    elif intent == "deployment_plan":
        # Extract the user's raw prompt
        dep_plan =  await managementService.generate_deployment_plan(client_id, project_id, message, chat_history)
        return await dep_plan

    elif intent == "feedback":
        # Extract feedback content
        return managementService.process_feedback(client_id, project_id, message)

    else:  # Handle unknown intent
        return {"status": "success", "response": "I'm sorry, I didn't understand that. Can you clarify?"}
