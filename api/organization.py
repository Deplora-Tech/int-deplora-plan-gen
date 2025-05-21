from core.database import env_manager, organizations
from services.main.communication.models import (
    OrganizationEnvironmentRequest,
    OrganizationRequest,
    EnvType,
)
from fastapi import APIRouter
from core.logger import logger


router = APIRouter()


@router.post("/create-organization")
async def create_organization(organization_data: OrganizationRequest):
    try:
        organization = await organizations.insert_one(organization_data)
        return {"status": "success", "organization": organization}
    except Exception as e:
        logger.error(f"Error creating organization: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/get-organizations/{client_id}")
async def get_organization(client_id: str):
    try:
        organization = await organizations.find_one({"client_id": client_id})
        logger.info(f"Organization found: {organization}")
        if organization:
            return {"status": "success", "organization": organization}
        else:
            return {"status": "error", "message": "Organization not found"}
    except Exception as e:
        logger.error(f"Error retrieving organization: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/store-org-credentials")
async def store_organization_credentials(organization: OrganizationEnvironmentRequest):
    try:
        await env_manager.save_multiple_variables(
            EnvType.ORG,
            organization.organization_id,
            organization.environment_variables,
        )
    except Exception as e:
        logger.error(f"Error storing organization credentials: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/use-org-credentials/{organization_id}")
async def get_organization_credentials(organization_id: str):
    try:
        env_vars = await env_manager.get_all_variables(EnvType.ORG, organization_id)

        return env_vars
    except Exception as e:
        logger.error(f"Error retrieving environment variables: {e}")
        return {}
