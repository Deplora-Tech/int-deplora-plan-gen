from pydantic import BaseModel


class MessageRequest(BaseModel):
    message: str
    client_id: str
    project_id: str
    organization_id: str
    session_id: str
    chat_history: dict

class PromptRequest(BaseModel):
    messageRequest: MessageRequest
    prompt_type: str 