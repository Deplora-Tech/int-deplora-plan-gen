from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    repo_url: str
    branch: str
    client_id: str
    project_id: str
