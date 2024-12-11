from services.main.communication.models import MessageRequest
from services.main.management.api import handle_message

async def process_initial_prompt(request: MessageRequest):
    res = await handle_message(request.client_id, request.project_id, request.message, request.chat_history)
    return res

async def process_conversation_message(request: MessageRequest):
    res = await handle_message(request.client_id, request.project_id, request.message, request.chat_history)
    return res

async def process_feedback(request: MessageRequest):
    res = await handle_message(request.client_id, request.project_id, request.message, request.chat_history)
    return res
