from pydantic import BaseModel
from services.main.enums import Preconndition


class MessageRequest(BaseModel):
    message: str
    client_id: str
    project_id: str
    organization_id: str
    session_id: str


class PromptRequest(BaseModel):
    messageRequest: MessageRequest
    prompt_type: str


class PreConditionRequest(BaseModel):
    client_id: str
    project_id: str
    organization_id: str
    session_id: str
    pre_condition: Preconndition
