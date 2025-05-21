from pydantic import BaseModel
from typing import List
from services.main.enums import Preconndition
from enum import Enum


class MessageRequest(BaseModel):
    message: str
    client_id: str
    project_id: str
    organization_id: str
    session_id: str
    mid: str | None = None


class PromptRequest(BaseModel):
    messageRequest: MessageRequest
    prompt_type: str


class PreConditionRequest(BaseModel):
    client_id: str
    project_id: str
    organization_id: str
    session_id: str
    pre_condition: Preconndition


class FileChangeRequest(BaseModel):
    session_id: str
    file_path: str
    file_content: str


class OrganizationRequest(BaseModel):
    organization_id: str
    client_id: str
    organization_name: str
    organization_description: str


class ProjectRequest(BaseModel):
    client_id: str
    organization_id: str
    projects: dict[str, str]


class ProjectEnvironmentRequest(BaseModel):
    project_id: str
    environment_variables: dict[str, str]


class OrganizationEnvironmentRequest(BaseModel):
    organization_id: str
    environment_variables: dict[str, str]


class EnvType(str, Enum):
    ORG = "org"
    PROJECT = "project"
