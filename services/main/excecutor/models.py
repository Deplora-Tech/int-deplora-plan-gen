from pydantic import BaseModel


class ExcecutionRequest(BaseModel):
    session_id: str
    env_variables: dict[str, dict[str, object]]


