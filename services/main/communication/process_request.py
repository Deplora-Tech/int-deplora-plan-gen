from core.logger import logger
from services.main.communication.models import MessageRequest
from services.main.communication.utils import process_initial_prompt, process_conversation_message, process_feedback

async def process_request(request: MessageRequest):
    try:
        # Parse the incoming message
        message = request.message
        logger.debug(f"Processing message: {message}")
        if message.startswith("INITIAL_PROMPT:"):
            data = message.replace("INITIAL_PROMPT:", "").strip()
            request.message = data
            return await process_initial_prompt(request)
        elif message.startswith("CONVERSATION_MESSAGE:"):
            data = message.replace("CONVERSATION_MESSAGE:", "").strip()
            request.message = data
            return await process_conversation_message(request)
        elif message.startswith("FEEDBACK:"):
            data = message.replace("FEEDBACK:", "").strip()
            request.message = data
            return await process_feedback(request)
        else:
            return f"ERROR: Unrecognized request."
    except Exception as e:
        return f"ERROR: Failed to process request. {str(e)}"