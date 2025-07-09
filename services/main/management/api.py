from core.logger import logger
from services.main.communication.service import CommunicationService
from services.main.enums import LoraStatus
from services.main.management.classifier import classify_intent
from services.main.management.service import ManagementService
from services.main.communication.models import MessageRequest, FileChangeRequest
from services.main.utils.caching.redis_service import SessionDataHandler
from dotenv import load_dotenv
import requests
import os

managementService = ManagementService()


async def handle_message(
    request: MessageRequest, communcationService: CommunicationService
):
    # Step 1: Use the classifier to detect the intent
    chat_history = SessionDataHandler.get_chat_history(request.session_id)

    SessionDataHandler.store_message_user(
        request.session_id, request.client_id, "user", request.message
    )
    SessionDataHandler.update_session_data(request.session_id, request.to_dict())

    intent = await classify_intent(request.message, chat_history)

    await communcationService.publisher(
        request.session_id, LoraStatus.INTENT_DETECTED.value
    )
    mid = SessionDataHandler.initialize_message_state_and_return(
        request.session_id,
        request.client_id,
        "You",
        [LoraStatus.STARTING.value, LoraStatus.INTENT_DETECTED.value],
    )
    request.mid = mid

    # Step 2: Route the message based on the detected intent
    if "create_deployment_plan" in intent:
        logger.info("Detected deployment intent")
        dep_plan = await managementService.generate_deployment_plan(
            request=request,
            prompt=request.message,
            project=request.project,
            organization_id=request.organization_id,
            user_id=request.client_id,
            chat_history=chat_history,
            session_id=request.session_id,
            communication_service=communcationService,
        )
        logger.info("Generated deployment plan")

        SessionDataHandler.store_current_plan(
            request.session_id, dep_plan["file_contents"]
        )
        SessionDataHandler.update_message_state_and_data(
            request.session_id,
            request.mid,
            LoraStatus.COMPLETED.value,
            dep_plan["response"],
        )

        # Send the files to the graph generator
        # logger.info("Sending files to the graph generator")
        # load_dotenv()
        # requests.post(
        #     os.environ.get("GRAPH_GENERATOR_URL"),
        #     json={"id": request.session_id, "files": dep_plan["file_contents"]},
        # )
        await handle_graph_generation(request.session_id)

        return dep_plan

    elif "modify_deployment_plan" in intent:
        logger.info("Detected modify deployment intent")
        await managementService.refine_deployment_plan(
            session_id=request.session_id,
            prompt=request.message,
        )

        SessionDataHandler.update_message_state_and_data(
            request.session_id,
            request.mid,
            LoraStatus.COMPLETED.value,
            "Your deployment plan has been modified.",
        )

        await handle_graph_generation(request.session_id)

    elif "greeting" in intent or "insult" in intent:
        logger.info("Detected other intent")
        res = await managementService.process_conversation(request, chat_history)
        SessionDataHandler.update_message_state_and_data(
            request.session_id,
            request.mid,
            LoraStatus.COMPLETED.value,
            res["response"],
        )
        return res

    else:  # Handle unknown intent
        logger.info("Detected unknown intent")
        SessionDataHandler.update_message_state_and_data(
            request.session_id,
            request.mid,
            LoraStatus.COMPLETED.value,
            "I'm sorry, I didn't understand that. Can you clarify?",
        )
        return {
            "status": "success",
            "response": "I'm sorry, I didn't understand that. Can you clarify?",
        }


async def handle_file_change(request: FileChangeRequest):

    return await managementService.update_file(request=request)


async def handle_graph_generation(session_id: str):
    """
    Handle the graph generation request by retrieving the files from the session data
    and sending them to the graph generator service.
    """
    try:
        logger.info(f"Handling graph generation for session_id: {session_id}")
        
        # Retrieve files from session data
        files = SessionDataHandler.get_session_data(session_id).get("current_plan", {})
        
        if not files:
            logger.error(f"No files found for session_id: {session_id}")
            return {"status": "error", "message": "No files to generate graph."}
        
        # Send files to the graph generator service
        load_dotenv()
        response = requests.post(
            os.environ.get("GRAPH_GENERATOR_URL"),
            json={"id": session_id, "files": files},
        )
        
        if response.status_code == 200:
            logger.info("Graph generation request sent successfully.")
            return {"status": "success", "message": "Graph generation initiated."}
        else:
            logger.error(f"Failed to send graph generation request: {response.text}")
            return {"status": "error", "message": "Failed to initiate graph generation."}
    except Exception as e:
        logger.error(f"Exception during graph generation: {e}")
        return {"status": "error", "message": f"Exception occurred: {str(e)}"}