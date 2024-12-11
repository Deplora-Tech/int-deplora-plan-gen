from pydantic import BaseModel


class MessageRequest(BaseModel):
    message: str
    client_id: str
    project_id: str
    chat_history: dict

