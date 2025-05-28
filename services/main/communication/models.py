from pydantic import BaseModel
from typing import List
from services.main.enums import Preconndition
from enum import Enum

class GitRepo(BaseModel):
    repo_url: str
    branch: str
    id: str
    name: str

class MessageRequest(BaseModel):
    message: str
    client_id: str
    project: GitRepo
    organization_id: str
    session_id: str
    mid: str | None = None

    def to_dict(self):
        return {
            "message": self.message,
            "client_id": self.client_id,
            "organization_id": self.organization_id,
            "session_id": self.session_id,
            "mid": self.mid,
            "project": {
                "repo_url": self.project.repo_url,
                "branch": self.project.branch,
                "id": self.project.id,
                "name": self.project.name,
            },
        }


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
    id: str
    client_id: str
    name: str
    description: str


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
