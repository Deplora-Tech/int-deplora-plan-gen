from core.database import env_manager, projects
from services.main.communication.models import (
    ProjectEnvironmentRequest,
    ProjectRequest,
    EnvType,
)
from fastapi import APIRouter
from core.logger import logger


router = APIRouter()


@router.post("/create-project")
async def create_project(project_data: ProjectRequest):
    try:
        project = await projects.insert_one(project_data)
        return {"status": "success", "project": project}
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/get-projects/{client_id}")
async def get_project(client_id: str, organization_id: str = None):
    try:
        project = await projects.find_one(
            {"client_id": client_id, "organization_id": organization_id}
        )
        logger.info(f"Project found: {project}")
        if project:
            return {"status": "success", "project": project}
        else:
            return {"status": "error", "message": "Project not found"}
    except Exception as e:
        logger.error(f"Error retrieving project: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/store-project-credentials")
async def store_project_credentials(project: ProjectEnvironmentRequest):
    try:
        await env_manager.save_multiple_variables(
            EnvType.PROJECT, project.project_id, project.environment_variables
        )
    except Exception as e:
        logger.error(f"Error storing project credentials: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/use-project-credentials/{project_id}")
async def get_project_credentials(project_id: str):
    try:
        env_vars = await env_manager.get_all_variables(EnvType.PROJECT, project_id)
        return env_vars
    except Exception as e:
        logger.error(f"Error retrieving environment variables: {e}")
        return {}
