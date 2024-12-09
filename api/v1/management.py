from fastapi import APIRouter
from services.management_service import ManagementService

router = APIRouter()
service = ManagementService()

@router.post("/generate-deployment-plan")
async def generate_deployment_plan(request: dict):
    return await service.generate_deployment_plan(request)
